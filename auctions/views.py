from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import (
    User,
    Listing,
    Bid,
)


def index(request):

    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


# ============================== Authentication ===============================

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# ================================= Listings ==================================


class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ("title", "description", "starting_bid", "photo")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 80, "rows": 20})
        }


@login_required
def create_listing(request):
    if request.method == "POST":

        form = NewListingForm(
            request.POST, request.FILES,
            {"owner": request.user}
        )

        if form.is_valid():
            listing = form.save()
            return HttpResponseRedirect(
                reverse(
                    "read_listing", args=[listing.id]
                )
            )
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form,
            })

    return render(request, "auctions/create_listing.html", {
        "form": NewListingForm()
    })


def read_listing(request, pk):

    try:
        listing = Listing.objects.get(pk=pk)
    except Listing.DoesNotExist:
        listing = None

    return render(request, "auctions/listing.html", {
        "listing": listing
    })


@login_required
def close_listing(request):

    if request.method == "POST":

        # TODO: error checking e.g. no listing id submitted /  not found
        listing = Listing.objects.get(pk=request.POST["listing_id"])
        if request.user == listing.owner:
            listing.is_open = False
            listing.save()
        else:
            HttpResponseRedirect(reverse("read_listing"), args=[listing.id])

    else:
        return HttpResponse("Method not allowed", status=405)


@login_required
def create_bid(request):

    if request.method == "POST":

        # TODO: error checking e.g. no post values submitted /  not found
        listing = Listing.objects.get(pk=request.POST["listing_id"])
        bid = Bid({"listing": listing, "bidder": request.user, "value": request.POST["bid"]})
        if request.user != listing.owner:
            if bid.is_valid():


    else:
        return HttpResponse("Method not allowed", status=405)
