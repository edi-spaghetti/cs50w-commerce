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
    current_price = models.IntegerField(verbose_name="Current Price")

    photo = models.ImageField(
        upload_to=rename_image_files,
        blank=True
    )
