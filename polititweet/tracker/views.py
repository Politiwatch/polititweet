import math
from django.shortcuts import render
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


def index(request):
    context = {}
    return render(request, "tracker/index.html", context)


def figures(request):
    context = {
        "figures": User.objects.all()
    }
    return render(request, "tracker/figures.html", context)


def figure(request):
    user_id = _get(request, "account")
    return HttpResponse("You are looking at the figure page for %s." % id)


def tweets(request):
    user_id = _get(request, "account")
    deleted = _get(request, "deleted", default=False)
    return HttpResponse("You are looking at the tweets page.")


def tweet(request):
    tweet_id = _get(request, "tweet")
    return HttpResponse("You are looking at the tweet page.")
