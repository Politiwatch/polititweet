import twitterinterface
from time import gmtime, strftime
import json
import os
import database
from random import shuffle

following = [802399136012177408]
following_old = [802399136012177408]
accounts = {}
account_data_old = {}

"""
Loads the followers into memory, as well as their data.

Required to run before archiveAll() and scanForDeletedAccounts().

If a followed user cannot be found in the database, its data is
retrieved from Twitter.

It also does preliminary updating functions on the database, sooooo...
"""
def loadDatabase():
    print("Loading database...")
    if database.hasFollowingData():
        following_old.extend(database.getFollowing())
    following.extend(twitterinterface.api.GetFriendIDs())
    database.writeFollowingData(following)
    friend_data = twitterinterface.api.GetFriends()
    print(friend_data)
    for account in friend_data:
        accounts[account.id] = account.AsDict()

        #create a directory for the account if it doesn't already exist
        database.initializeAccountData(account.id)

        #load old account data into memory if it exists
        if database.hasAccountData(account.id):
                account_data_old[account.id] = database.getAccountFromDatabase(account.id)

        #write to account.json with new data
        database.writeAccountToDatabase(account)

        #create metadata
        metadata = {"deleted": False}

        #write metadata
        database.writeAccountMetadata(account.id, metadata)


        #write to archive
        database.archiveAccountData(account)


"""
Check whether or not an account has deleted a tweet.

WARNING: requires account[id] and account_data_old[id] to be UP TO DATE!
"""
def hasAccountDeletedTweet(id):
    if "has_deleted_tweet" in database.getAccountMetadata(id):
        if database.getAccountMetadata(id)["has_deleted_tweet"]:
            return True
    account = accounts[id]
    account_old = account_data_old[id]
    if account["statuses_count"] < account_old["statuses_count"]:
        return True
    tweets_since = twitterinterface.getAllStatusesSince(id, account_old["status"]["id"])
    return account["statuses_count"] - len(tweets_since) < account_old["statuses_count"]


def scanAllAccountsForDelete():
    for account in following:
        if hasAccountDeletedTweet(account):
            database.markAsHasDeletedTweet(account)
            scanForDeletedTweets(account)


"""
Check all following accounts to see if they have deleted a tweet.

Returns the ID of all detected deleted tweets.
"""
def checkForDeletedTweets():
    deleted = []
    for account in following:
        print("Checking account " + str(account) + " for deleted tweets...")
        #if(hasAccountDeletedTweet(account)):
        deleted.extend(scanForDeletedTweets(account))
    return deleted



def scanForDeletedTweets(account):
    current_statuses = twitterinterface.getAllStatuses(account)
    database_statuses = database.retreiveAllStatusesFromDatabase(account)
    ids_current = []
    for status in current_statuses:
        ids_current.append(status.id)
    deleted = []
    for status in database_statuses:
        if status["id"] not in ids_current:
            if not twitterinterface.doesStatusExist(status["id"]):
                print("[!] found deleted tweet: " + str(status["id"]))
                deleted.append(status)
                database.markTweetAsDeleted(account, status["id"])
            print('[i] status unavailable via API but not deleted: ' + str(status["id"]))
    print("   ...found " + str(len(deleted)) + " deleted tweets.")
    return deleted


"""
Scan for deleted accounts, and if the account is deleted, mark it as so in the database.
"""
def scanForDeletedAccounts():
    shuffle(following_old)
    for account in following_old:
        if account not in following:
            try:
                user = twitterinterface.api.GetUser(user_id=account)
                print("    (user " + str(account) + " still exists, false alarm)")
            except Exception as error:
                try:
                    if error[0][0]["code"] == 50:
                        print("[!] User has been deleted: " + str(account))
                        metadata = database.getAccountMetadata(account)
                        metadata["deleted"] = True
                        database.writeAccountMetadata(account, metadata)
                except Exception as e:
                    print(e)



"""
Smart archive.

Scans for deleted tweets AND archives everything.

Only run this for accounts that exist on Twitter.
"""
def smarchive(id):
    print("Smarchiving " + str(id) + "...")
    tweets = twitterinterface.getAllStatuses(id)
    print("Retrieved " + str(len(tweets)) + " tweets from Twitter. Archiving...")
    for tweet in tweets:
        tweet_dict = tweet.AsDict()
        tweet_dict["deleted"] = False
        tweet_dict["retrieved"] = database.time()
        database.writeTweet(id, tweet.id, json.dumps(tweet_dict))
    print("Retrieving tweets from database...")
    database_tweets = database.getAllTweetsInDatabase(id)
    twitter_tweet_ids = [t.id for t in tweets]
    database_tweet_ids = [t["id"] for t in database_tweets]
    deleted_tweets = [t for t in database_tweet_ids if t not in twitter_tweet_ids]
    print("Found " + str(len(deleted_tweets)) + " deletion candidates... checking")
    found_deleted = False
    for tweet in deleted_tweets:
        if twitterinterface.doesStatusExist(tweet):
            deleted_tweets.remove(tweet)
        else:
            database.markTweetAsDeleted(id, tweet)
            print("[!] deleted tweet: " + str(tweet))
            found_deleted = True
    if found_deleted:
        database.markAsHasDeletedTweet(id)
    print("Found " + str(len(deleted_tweets)) + " deleted tweets!")

"""
Archive every user that is being followed.
"""
def archiveAll(repeat=True, aggressive=False):
    shuffle(following)  # so that accounts at end will get same coverage over time
    first = []
    for account in following:
        if not database.hasTweetArchive(account):
            first.append(account)
            following.remove(account)
    print("Processing accounts first: " + str(first))
    for account in first:
        if not database.hasTweetArchive(account) or repeat:
            smarchive(account)
        else:
            print("Already archived " + str(account))
    print("Now processing others...")
    for account in following:
        if not database.hasTweetArchive(account) or repeat:
            smarchive(account)
        else:
            print("Already archived " + str(account))



"""
Takes a user (denoted by id) and archives
their data from Twitter if not already archived.

It will make a copy of their user data as well as
any new tweets (or simply any tweets that are not
currently in its database).
"""
def archiveAccount(id, aggressive=False):
    print("Archiving " + str(id) + "...")
    database.initializeAccountData(id)
    user = twitterinterface.api.GetUser(user_id=id)
    database.writeAccountToDatabase(user)
    database.archiveAccountData(user)
    database.initializeTweetArchive(id)
    statuses = []
    if aggressive:
        statuses = twitterinterface.getAllStatuses(id)
    else:
        archived_status_data = database.getHighestLowestArchivedStatus(id)
        lowest_archived_status = archived_status_data[1]
        highest_archived_status = archived_status_data[0]
        statuses = twitterinterface.getAllStatuses(id, lowest_archived_status=lowest_archived_status)
        if highest_archived_status != -1:
            print("    Also grabbing statuses since " + str(highest_archived_status))
            statuses.extend(twitterinterface.getAllStatusesSince(id, highest_archived_status)) # to fill in holes
    for status in statuses:
        data = status.AsDict()
        data["deleted"] = False
        data["retrieved"] = database.time()
        database.writeTweet(id, data["id"], json.dumps(data))
    print("Archived " + str(len(statuses)) + " tweets & account data for " + str(id) + ".")


while True:
    try:
        loadDatabase()
        shuffle(following)
        while True:
            archiveAll(aggressive=True)  # includes Smarchive, which does deleted tweets!
    except Exception as e:
        print(e)
        print("Restarting...")
