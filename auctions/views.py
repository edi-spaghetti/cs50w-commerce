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
    Category,
    Comment,
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
        # TODO: ensure first and last name added on registration

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


# ================================== Forms ====================================


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


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content", "listing", "author")


# ================================== Listings =================================


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


# ================================= Bids ======================================


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


# ================================ Watchlist ==================================


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


@login_required
def read_watchlist(request):

    listings = Listing.objects.filter(watchers=request.user)

    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


# ================================= Categories ================================


def read_categories(request):

    categories = Category.objects.all()

    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def read_category(request, pk):

    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        category = None

    return render(request, "auctions/category.html", {
        "category": category
    })


# ================================= Comments ==================================


@login_required
def create_comment(request):

    if request.method == "POST":

        try:
            listing = Listing.objects.get(pk=request.POST["listing_id"])
            content = request.POST["content"]

            comment = NewCommentForm({
                "listing": listing,
                "author": request.user,
                "content": content
            })
            if comment.is_valid():
                comment.save()

        except (Listing.DoesNotExist, KeyError, ValueError):
            # TODO: create 'something went wrong' page before redirect
            return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponseRedirect(
                reverse("read_listing", args=[listing.id]),
            )

    else:
        return HttpResponse("Method not allowed", status=405)


# TODO: post_only_pathway wrapper function + decorators
