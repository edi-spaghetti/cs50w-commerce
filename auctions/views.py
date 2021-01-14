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
        "listings": Listing.objects.filter(is_open=True)
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
        fields = ("title", "description", "starting_bid", "photo", "category")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 80, "rows": 20}),
            "starting_bid": forms.NumberInput(attrs={"min": 1, "step": 1}),
        }


class NewBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ("value", "listing", "bidder")


@login_required
def create_listing(request):
    if request.method == "POST":

        form = NewListingForm(request.POST, request.FILES)

        valid = form.is_valid()
        positive = form.cleaned_data["starting_bid"] > 0
        if not positive:
            form.add_error(
                "starting_bid",
                "Must be a number above zero"
            )

        if valid and positive:
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
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

    # TODO: If a user is signed in on a closed listing page,
    #       and the user has won that auction, the page should say so.

    # TODO: Users who are signed in should be able to add comments to the
    #       listing page.

    #  TODO: The listing page should display all comments that have
    #        been made on the listing.

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "on_watchlist": listing.watchers.filter(pk=request.user.id).exists(),
        "insufficient_bid": False,
    })


@login_required
def close_listing(request):

    if request.method == "POST":

        # TODO: error checking e.g. no listing id submitted /  not found
        try:
            listing = Listing.objects.get(pk=request.POST["listing_id"])
        except (Listing.DoesNotExist, KeyError, ValueError):
            # TODO: create 'something went wrong' page before redirect
            return HttpResponseRedirect(reverse("index"))
        else:
            if request.user == listing.owner:
                listing.is_open = False
                listing.save()

            return HttpResponseRedirect(
                reverse("read_listing", args=[listing.id])
            )

    else:
        return HttpResponse("Method not allowed", status=405)


@login_required
def create_bid(request):

    if request.method == "POST":

        try:
            listing = Listing.objects.get(pk=request.POST["listing_id"])

            bid = NewBidForm(
                {
                    "listing": listing,
                    "bidder": request.user,
                    "value": int(request.POST["value"])
                }
            )

            if request.user != listing.owner:
                if bid.is_valid():
                    new_value = int(bid.cleaned_data["value"])
                    if new_value >= listing.new_bid_minimum:
                        bid.save()
                    else:
                        # re-implementing read_listing template render
                        # so I can pass an error message without having to
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "on_watchlist": listing.watchers.filter(
                                pk=request.user.id).exists(),
                            "insufficient_bid": True
                        })

        except (Listing.DoesNotExist, KeyError, ValueError):
            # TODO: create 'something went wrong' page before redirect
            return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponseRedirect(
                reverse("read_listing", args=[listing.id]),
            )
    else:
        return HttpResponse("Method not allowed", status=405)


@login_required
def add_watcher(request):

    if request.method == "POST":

        try:
            listing = Listing.objects.get(pk=request.POST["listing_id"])

            if not listing.watchers.filter(pk=request.user.id).exists():
                listing.watchers.add(request.user)
                listing.save()

        except (Listing.DoesNotExist, KeyError, ValueError):
            # TODO: create 'something went wrong' page before redirect
            return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponseRedirect(
                reverse("read_listing", args=[listing.id]),
            )

    else:
        return HttpResponse("Method not allowed", status=405)


@login_required
def remove_watcher(request):

    if request.method == "POST":

        try:
            listing = Listing.objects.get(pk=request.POST["listing_id"])

            if listing.watchers.filter(pk=request.user.id).exists():
                listing.watchers.remove(request.user)
                listing.save()

        except (Listing.DoesNotExist, KeyError, ValueError):
            # TODO: create 'something went wrong' page before redirect
            return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponseRedirect(
                reverse("read_listing", args=[listing.id]),
            )

    else:
        return HttpResponse("Method not allowed", status=405)


# TODO: Users who are signed in should be able to visit a Watchlist page

# TODO: Watchlist should display all of the listings that a user has added
#       to their watchlist

# TODO: Clicking on any of those listings should take the user to that
#       listing’s page


# TODO: Users should be able to visit a page that displays a list of all
#       listing categories.

# TODO: Clicking on the name of any category should take the user to a page
#       that displays all of the active listings in that category
