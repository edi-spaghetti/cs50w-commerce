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
from .utils import RequestLogger


logger = RequestLogger(__name__)


def index(request):

    listings = Listing.objects.filter(is_open=True)
    logger.debug(request.user.id, f' viewed {len(listings)} listings on index')

    top_three = Category.top_three()
    logger.debug(request.user.id, f'view top 3 categories: {top_three}')

    return render(request, 'auctions/index.html', {
        'listings': listings,
        'top_categories': top_three,
    })


# ============================== Authentication ===============================


def login_view(request):
    if request.method == 'POST':

        # Attempt to sign user in
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            logger.debug(user.id, f'successful login')
            return HttpResponseRedirect(reverse('index'))
        else:
            try:
                user = User.objects.get(username=username)
                logger.debug(user.id, 'login fail > incorrect password')
            except User.DoesNotExist:
                logger.debug(username, 'login fail > incorrect username')

            top_three = Category.top_three()
            logger.debug(request.user.id,
                         f'view top 3 categories: {top_three}')

            return render(request, 'auctions/login.html', {
                'message': 'Invalid username and/or password.',
                'top_categories': top_three,
            })
    else:
        logger.debug(request.user.id, 'loaded login view')

        top_three = Category.top_three()
        logger.debug(request.user.id, f'view top 3 categories: {top_three}')

        return render(request, 'auctions/login.html', {
            'top_categories': top_three,
        })


def logout_view(request):
    logger.debug(request.user.id, 'log out')
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']

        # Ensure password matches confirmation
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        if password != confirmation:
            logger.debug(
                request.user.id,
                'Attempted register password no match'
            )

            top_three = Category.top_three()
            logger.debug(request.user.id,
                         f'view top 3 categories: {top_three}')

            return render(request, 'auctions/register.html', {
                'message': 'Passwords must match.',
                'top_categories': top_three,
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username, email, password,
                first_name=first_name
            )
            user.save()
            logger.info(user.id, 'New successful registration')
        except IntegrityError:
            logger.debug(
                request.user.id,
                f'failed register existing username: {username}'
            )

            top_three = Category.top_three()
            logger.debug(request.user.id,
                         f'view top 3 categories: {top_three}')

            return render(request, 'auctions/register.html', {
                'message': 'Username already taken.',
                'top_categories': top_three,
            })
        logger.debug(user.id, 'successful login')
        login(request, user)
        return HttpResponseRedirect(reverse('index'))
    else:
        logger.debug(request.user.id, 'loaded register view')

        top_three = Category.top_three()
        logger.debug(request.user.id, f'view top 3 categories: {top_three}')

        return render(request, 'auctions/register.html', {
            'top_categories': top_three,
        })


# ================================== Forms ====================================


class StyledFileInput(forms.FileInput):
    template_name = 'auctions/widgets/file.html'


class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'description', 'starting_bid', 'photo', 'category')
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
            'starting_bid': forms.NumberInput(attrs={'min': 1, 'step': 1}),
            'photo': StyledFileInput(),
        }


class NewBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ('value', 'listing', 'bidder')


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content', 'listing', 'author')


# ================================== Listings =================================


@login_required
def create_listing(request):
    if request.method == 'POST':

        form = NewListingForm(request.POST, request.FILES)

        valid = form.is_valid()
        positive = form.cleaned_data['starting_bid'] > 0
        if not positive:
            form.add_error(
                'starting_bid',
                'Must be a number above zero'
            )
            logger.debug(request.user.id, 'Below zero starting bid')

        if valid and positive:
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            logger.info(request.user.id, f'New Listing: {listing}')
            return HttpResponseRedirect(
                reverse(
                    'read_listing', args=[listing.id]
                )
            )
        else:
            logger.debug(request.user.id, 'Invalid create listing attempt')

            top_three = Category.top_three()
            logger.debug(request.user.id,
                         f'view top 3 categories: {top_three}')

            return render(request, 'auctions/create_listing.html', {
                'form': form,
                'top_categories': top_three,
            })

    top_three = Category.top_three()
    logger.debug(request.user.id,
                 f'view top 3 categories: {top_three}')

    logger.debug(request.user.id, 'Loaded create listing view')
    return render(request, 'auctions/create_listing.html', {
        'form': NewListingForm(),
        'top_categories': top_three,
    })


def read_listing(request, pk):

    try:
        listing = Listing.objects.get(pk=pk)
    except Listing.DoesNotExist:
        listing = None

    logger.debug(request.user.id, f'Loaded listing: {listing}')

    top_three = Category.top_three()
    logger.debug(request.user.id, f'view top 3 categories: {top_three}')

    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'on_watchlist': listing.watchers.filter(pk=request.user.id).exists(),
        'insufficient_bid': False,
        'top_categories': top_three,
    })


@login_required
def close_listing(request):

    if request.method == 'POST':

        # TODO: error checking e.g. no listing id submitted /  not found
        try:
            listing = Listing.objects.get(pk=request.POST['listing_id'])
        except (Listing.DoesNotExist, KeyError, ValueError):
            # TODO: create 'something went wrong' page before redirect
            logger.warning(
                request.user.id,
                f'failed to get listing {request.POST.get("listing_id")}'
            )
            return HttpResponseRedirect(reverse('index'))
        else:
            if request.user == listing.owner:
                listing.is_open = False
                listing.save()
                logger.info(
                    request.user.id,
                    f'Closed Listing: {listing.id}'
                )
            else:
                logger.warning(
                    request.user.id,
                    f'Attempted close listing owned by '
                    f'User: {listing.owner.id}'
                )

            return HttpResponseRedirect(
                reverse('read_listing', args=[listing.id])
            )

    else:
        logger.warning(
            request.user.id,
            f'Invalid GET request on close listing'
        )
        return HttpResponse('Method not allowed', status=405)


# ================================= Bids ======================================


@login_required
def create_bid(request):

    if request.method == 'POST':

        try:
            listing = Listing.objects.get(pk=request.POST['listing_id'])

            bid = NewBidForm(
                {
                    'listing': listing,
                    'bidder': request.user,
                    'value': int(request.POST['value'])
                }
            )

            if request.user != listing.owner:
                if bid.is_valid():
                    new_value = int(bid.cleaned_data['value'])
                    if new_value >= listing.new_bid_minimum:
                        bid = bid.save()
                        logger.info(
                            request.user.id,
                            f'New Bid: <{bid.id}> {bid.value} '
                            f'on Listing: {listing.id}'
                        )
                    else:
                        # re-implementing read_listing template render
                        # so I can pass an error message without having to
                        logger.warning(
                            request.user.id,
                            f'Attempted bid below minimum'
                        )

                        top_three = Category.top_three()
                        logger.debug(request.user.id,
                                     f'view top 3 categories: {top_three}')

                        return render(request, 'auctions/listing.html', {
                            'listing': listing,
                            'on_watchlist': listing.watchers.filter(
                                pk=request.user.id).exists(),
                            'insufficient_bid': True,
                            'top_categories': top_three,
                        })

        except (Listing.DoesNotExist, KeyError, ValueError):
            # TODO: create 'something went wrong' page before redirect
            logger.warning(
                request.user.id,
                f'failed to get listing {request.POST.get("listing_id")}'
            )
            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponseRedirect(
                reverse('read_listing', args=[listing.id]),
            )
    else:
        logger.warning(
            request.user.id,
            f'Invalid GET request on create bid'
        )
        return HttpResponse('Method not allowed', status=405)


# ================================ Watchlist ==================================


@login_required
def add_watcher(request):

    if request.method == 'POST':

        try:
            listing = Listing.objects.get(pk=request.POST['listing_id'])

            if not listing.watchers.filter(pk=request.user.id).exists():
                listing.watchers.add(request.user)
                listing.save()
                logger.info(
                    request.user.id,
                    f'added as watcher to Listing: {listing.id}'
                )
            else:
                logger.warning(
                    request.user.id,
                    f'attempted to add as watcher to '
                    f'Listing: {listing.id} when already is watcher'
                )

        except (Listing.DoesNotExist, KeyError, ValueError):
            # TODO: create 'something went wrong' page before redirect
            logger.warning(
                request.user.id,
                f'failed to get listing {request.POST.get("listing_id")}'
            )
            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponseRedirect(
                reverse('read_listing', args=[listing.id]),
            )

    else:
        logger.warning(
            request.user.id,
            f'Invalid GET request on add watcher'
        )
        return HttpResponse('Method not allowed', status=405)


@login_required
def remove_watcher(request):

    if request.method == 'POST':

        try:
            listing = Listing.objects.get(pk=request.POST['listing_id'])

            if listing.watchers.filter(pk=request.user.id).exists():
                listing.watchers.remove(request.user)
                listing.save()
                logger.info(
                    request.user.id,
                    f'removed as watcher on Listing: {listing.id}'
                )
            else:
                logger.warning(
                    request.user.id,
                    f'attempted to remove as watcher on '
                    f'Listing {listing.id} when not a watcher'
                )

        except (Listing.DoesNotExist, KeyError, ValueError):
            # TODO: create 'something went wrong' page before redirect
            logger.warning(
                request.user.id,
                f'failed to get listing {request.POST.get("listing_id")}'
            )
            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponseRedirect(
                reverse('read_listing', args=[listing.id]),
            )

    else:
        logger.warning(
            request.user.id,
            f'Invalid GET request on remove watcher'
        )
        return HttpResponse('Method not allowed', status=405)


@login_required
def read_watchlist(request):

    listings = Listing.objects.filter(watchers=request.user)
    logger.debug(
        request.user.id,
        f'Loaded watchlist of {len(listings)} listings'
    )

    top_three = Category.top_three()
    logger.debug(request.user.id, f'view top 3 categories: {top_three}')

    return render(request, 'auctions/watchlist.html', {
        'listings': listings,
        'top_categories': top_three,
    })


# ================================= Categories ================================


def read_categories(request):

    categories = Category.objects.all()
    logger.debug(
        request.user.id,
        f'Loaded categories view with {len(categories)} categories'
    )

    top_three = Category.top_three()
    logger.debug(request.user.id, f'view top 3 categories: {top_three}')

    return render(request, 'auctions/categories.html', {
        'categories': categories,
        'top_categories': top_three,
    })


def read_category(request, pk):

    try:
        category = Category.objects.get(pk=pk)
        logger.debug(
            request.user.id,
            f'Loaded Category: {category} view'
        )
    except Category.DoesNotExist:
        category = None
        logger.warning(
            request.user.id,
            f'Attempted load category with bad id: {pk}'
        )

    top_three = Category.top_three()
    logger.debug(request.user.id, f'view top 3 categories: {top_three}')

    return render(request, 'auctions/category.html', {
        'category': category,
        'top_categories': top_three,
    })


# ================================= Comments ==================================


@login_required
def create_comment(request):

    if request.method == 'POST':

        try:
            listing = Listing.objects.get(pk=request.POST['listing_id'])
            content = request.POST['content']

            comment = NewCommentForm({
                'listing': listing,
                'author': request.user,
                'content': content
            })
            if comment.is_valid():
                comment = comment.save()
                logger.info(
                    request.user.id,
                    f'Created Comment {comment.id} on Listing: {listing.id}'
                )
            else:
                logger.warning(
                    request.user.id,
                    f'attempted to create invalid comment on '
                    f'Listing {listing.id}'
                )
        except (Listing.DoesNotExist, KeyError, ValueError):
            # TODO: create 'something went wrong' page before redirect
            logger.warning(
                request.user.id,
                f'failed to get listing {request.POST.get("listing_id")}'
            )
            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponseRedirect(
                reverse('read_listing', args=[listing.id]),
            )

    else:
        logger.warning(
            request.user.id,
            f'Invalid GET request on create comment'
        )
        return HttpResponse('Method not allowed', status=405)


# TODO: post_only_pathway wrapper function + decorators
