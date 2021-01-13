from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max
from uuid import uuid4


class User(AbstractUser):
    pass


def rename_image_files(instance, filename):
    return f"listing/{uuid4().hex}"


class Listing(models.Model):
    title = models.CharField(max_length=64, verbose_name="Title")
    description = models.CharField(max_length=1000, verbose_name="Description")
    starting_bid = models.IntegerField(verbose_name="Starting Bid")
    is_open = models.BooleanField(default=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Owner",
        related_name="listings",
        null=True,
        blank=True,
    )
    photo = models.ImageField(
        upload_to=rename_image_files,
        blank=True
    )
    watchers = models.ManyToManyField(User)

    @property
    def highest_bid(self):
        """
        Gets the current highest bid, or if no bids have currently been made,
        the starting bid
        :rtype: int
        """
        bids = self.bids.values()
        highest_bid = bids.aggregate(Max("value"))["value__max"]
        return highest_bid or self.starting_bid

    @property
    def bid_increment(self):
        # setting to 1 for now, but potentially this could be configurable
        # by users for their listings.
        return 1

    @property
    def new_bid_minimum(self):
        """
        Lowest value a new bid can be created at on the current listing
        """
        return self.highest_bid + self.bid_increment


class Bid(models.Model):
    listing = models.ForeignKey(
        Listing,
        related_name="bids",
        on_delete=models.CASCADE,
        verbose_name="Listing"
    )
    bidder = models.ForeignKey(
        User,
        related_name="bids",
        on_delete=models.CASCADE,
        verbose_name="Bidder"
    )
    value = models.IntegerField(verbose_name="Bid")
