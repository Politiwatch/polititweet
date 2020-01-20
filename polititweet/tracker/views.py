import math
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from .models import User, Tweet
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchVector
from django.db.models import TextField
from django.db.models.functions import Cast
from .util import first_or_none

ITEMS_PER_PAGE = 50


def _get(request, param, default=None):
    value = request.GET.get(param)
    if value is None:
        if default is None:
            raise Http404()
        else:
            return default
    return value


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
    deleted = Tweet.objects.filter(deleted=True).order_by("-tweet_id")
    tweets = Tweet.objects.order_by("-tweet_id")
    deletors = User.objects.order_by("-deleted_count")
    total_figures = deletors.count()
    last_archived = tweets[0].modified_date
    total_deleted = deleted.count()
    most_recently_deleted = Tweet.get_current_top_deleted_tweet(since=30)
    context = {"total_figures": total_figures,
               "last_archived": last_archived,
               "total_deleted": total_deleted,
               "most_recently_deleted": most_recently_deleted,
               "most_deletions": deletors[:4],
               "recently_deleted": deleted[:3],
               "recently_archived": tweets[:3]}
    return render(request, "tracker/index.html", context)


def figures(request):
    figures = User.objects.all()
    search = _get(request, "search", default="").replace("@", "")
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
    deleted = _get(request, "deleted", default="Neither")
    pagination_enabled = request.GET.get("pagination", "True")
    if pagination_enabled == "False":
        pagination_enabled = False
    else:
        pagination_enabled = True
    if deleted == "True":
        deleted = True
    elif deleted == "False":
        deleted = False
    else:
        deleted = None
    search = _get(request, "search", default="")
    page = int(_get(request, "page", default=1))
    active = "deleted" if deleted else "archive"
    matched_tweets = []
    if len(search) > 0:
        if deleted == None:
            matched_tweets = Tweet.objects.filter(user=user, full_text__search=search).prefetch_related("user").order_by("-tweet_id")
        else:
            matched_tweets = Tweet.objects.filter(user=user, deleted=deleted, full_text__search=search).prefetch_related("user").order_by("-tweet_id")
    else:
        if deleted == None:
            matched_tweets = Tweet.objects.filter(user=user).prefetch_related("user").order_by("-tweet_id")
        else:
            matched_tweets = Tweet.objects.filter(user=user, deleted=deleted).prefetch_related("user").order_by("-tweet_id")
    page_len = 30
    if not pagination_enabled:
        page_len = len(matched_tweets)
    paginator = Paginator(matched_tweets, page_len)
    page_obj = paginator.get_page(page)
    context = {
        "figure": user,
        "active": active,
        "total_matched": len(matched_tweets),
        "search_query": search,
        "page_obj": page_obj,
        "tweets": page_obj,
        "paginator": paginator,
        "pagination_enabled": pagination_enabled,
        "deleted_filter": deleted,
        "url_parameters": "&deleted=%s&account=%s&search=%s" % (deleted, user_id, search)
    }
    return render(request, 'tracker/tweets.html', context)


def tweet(request):
    tweet_id = _get(request, "tweet")
    tweet = get_object_or_404(Tweet, tweet_id=tweet_id)
    if request.GET.get("raw", "False") == "True":
        return JsonResponse(tweet.full_data)
    figure = tweet.user
    active = "deleted" if tweet.deleted else "archive"
    context = {
        "tweet": tweet,
        "figure": figure,
        "active": active,
        "preceding": tweet.preceding,
        "following": tweet.following,
    }
    return render(request, 'tracker/tweet.html', context)


def about(request):
    return render(request, 'tracker/about.html', {})
