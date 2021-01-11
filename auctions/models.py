from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid import uuid4


class User(AbstractUser):
    pass


def rename_image_files(instance, filename):
    return f"listing/{uuid4().hex}"


class Listing(models.Model):
    title = models.CharField(max_length=64, verbose_name="Title")
    description = models.CharField(max_length=1000, verbose_name="Description")
    starting_bid = models.IntegerField(verbose_name="Starting Bid", default=0)
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
