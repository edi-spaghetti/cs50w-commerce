from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=64, verbose_name="Title")
    description = models.CharField(max_length=1000, verbose_name="Description")
    current_price = models.IntegerField(verbose_name="Current Price")

    # TODO: ImageField
    # photo = models.ImageField(upload_to=)
