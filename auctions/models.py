from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1000)
    current_price = models.IntegerField()

    # TODO: ImageField
    # photo = models.ImageField(upload_to=)
