import math
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from .models import User, Tweet
from django.core.paginator import Paginator

ITEMS_PER_PAGE = 50


def _get(request, param, default=None):
    value = request.GET.get(param)
    if value is None:
        if default is None:
            raise Http404()
        else:
            return default
    return value


def _first_or_none(obj):
    try:
        return obj[0]
    except:
        return None


def _search(query, *items):
    tokens = query.split(" ")
    unused_tokens = [token for token in tokens]
    for token in tokens:
        for item in items:
            if token.lower() in item.lower():
                if token in unused_tokens:
                    unused_tokens.remove(token)
    return len(unused_tokens) == 0


def index(request):
    deleted = Tweet.objects.filter(deleted=True).order_by("-modified_date")
    tweets = Tweet.objects.order_by("-tweet_id")
    deletors = User.objects.order_by("-deleted_count")
    total_figures = deletors.count()
    total_tweets = tweets.count()
    total_deleted = deleted.count()
    most_recently_deleted = _first_or_none(deleted)
    context = {"total_figures": total_figures,
               "total_tweets": total_tweets,
               "total_deleted": total_deleted,
               "most_recently_deleted": most_recently_deleted,
               "most_deletions": deletors[:4],
               "recently_deleted": deleted[:3],
               "recently_archived": tweets[:3]}
    return render(request, "tracker/index.html", context)


def figures(request):
    figures = User.objects.all()
    search = _get(request, "search", default="")
    matched_figures = []
    page = int(_get(request, "page", default=1))
    if len(search) > 0:
        for figure in figures:
            if _search(search, figure.full_data["name"], figure.full_data["screen_name"], figure.full_data["description"]):
                matched_figures.append(figure)
    else:
        matched_figures = figures
    url_parameters = "&search=%s" % search
    paginator = Paginator(
        sorted(matched_figures, key=lambda k: k.deleted_count, reverse=True), 30)
    page_obj = paginator.get_page(page)
    context = {
        "all_figures": User.objects.count(),
        "total_matched": len(matched_figures),
        "figures": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "search_query": search,
        "url_parameters": url_parameters
    }
    return render(request, "tracker/figures.html", context)


def figure(request):
    user_id = _get(request, "account")
    user = get_object_or_404(User, user_id=user_id)
    context = {
        "figure": user,
        "active": "overview",
        "tweets": Tweet.objects.filter(user=user, deleted=True).order_by("-modified_date")[:4],
        "total_archived": Tweet.objects.filter(user=user).count()
    }
    return render(request, 'tracker/figure.html', context)


def tweets(request):
    user_id = _get(request, "account")
    user = get_object_or_404(User, user_id=user_id)
    deleted = _get(request, "deleted", default="False") == "True"
    search = _get(request, "search", default="")
    page = int(_get(request, "page", default=1))
    active = "deleted" if deleted else "archive"
    tweets = Tweet.objects.filter(
        user=user, deleted=deleted).order_by("-modified_date")
    matched_tweets = []
    if len(search) > 0:  # todo: move search to db side?
        for tweet in tweets:
            if _search(search, tweet.text()):
                matched_tweets.append(tweet)
    else:
        matched_tweets = tweets
    paginator = Paginator(
        sorted(matched_tweets, key=lambda k: k.tweet_id, reverse=True), 30)
    page_obj = paginator.get_page(page)
    context = {
        "figure": user,
        "active": active,
        "total_matched": len(matched_tweets),
        "search_query": search,
        "page_obj": page_obj,
        "tweets": page_obj,
        "paginator": paginator,
        "url_parameters": "&deleted=%s&account=%s&search=%s" % (deleted, user_id, search)
    }
    return render(request, 'tracker/tweets.html', context)


def tweet(request):
    tweet_id = _get(request, "tweet")
    tweet = get_object_or_404(Tweet, tweet_id=tweet_id)
    figure = tweet.user
    active = "deleted" if tweet.deleted else "archive"
    tweet_before = _first_or_none(Tweet.objects.filter(
        user=figure, tweet_id__lt=tweet_id).order_by("-tweet_id"))
    tweet_after = _first_or_none(Tweet.objects.filter(
        user=figure, tweet_id__gt=tweet_id).order_by("tweet_id"))
    context = {
        "tweet": tweet,
        "figure": figure,
        "active": active,
        "preceding": tweet_before,
        "following": tweet_after
    }
    return render(request, 'tracker/tweet.html', context)

def about(request):
    return render(request, 'tracker/about.html', {})