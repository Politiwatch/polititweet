import math
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from .models import User, Tweet

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
    context = {}
    return render(request, "tracker/index.html", context)


def figures(request):
    figures = User.objects.all()
    search = _get(request, "search", default="")
    matched_figures = []
    if len(search) > 0:
        for figure in figures:
            if _search(search, figure.full_data["name"], figure.full_data["screen_name"], figure.full_data["description"]):
                matched_figures.append(figure)
    else:
        matched_figures = figures
    context = {
        "all_figures": User.objects.count(),
        "figures": matched_figures,
        "search_query": search
    }
    return render(request, "tracker/figures.html", context)


def figure(request):
    user_id = _get(request, "account")
    user = get_object_or_404(User, user_id=user_id)
    context = {
        "figure": user,
        "active": "overview",
        "tweets": Tweet.objects.filter(user=user, deleted=True).order_by("-modified_date")[:5]
    }
    return render(request, 'tracker/figure.html', context)


def tweets(request):
    user_id = _get(request, "account")
    deleted = _get(request, "deleted", default=False)
    return HttpResponse("You are looking at the tweets page.")


def tweet(request):
    tweet_id = _get(request, "tweet")
    return HttpResponse("You are looking at the tweet page.")
