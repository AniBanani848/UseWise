from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def items_placeholder(request):
    return render(request, "items_placeholder.html")
