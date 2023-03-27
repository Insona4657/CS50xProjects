from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse


def index(request):
    return render(request, "google/index.html")


def advanced(request):
    return render(request, "google/advanced.html")


def images(request):
    return render(request, "google/images.html")


def back(request):
    return HttpResponseRedirect(reverse('index'))