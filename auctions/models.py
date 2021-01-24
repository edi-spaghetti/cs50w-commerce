import logging
from uuid import uuid4

from PIL import Image

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max, Sum

from .utils import get_random_colour, BG_COLOURS


logger = logging.getLogger(__name__)


class User(AbstractUser):
    pass


class Category(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(
        max_length=64,
        verbose_name='Name',
        unique=True,
    )

    bg_colour = models.CharField(
        max_length=16,
        choices=BG_COLOURS,
        default=get_random_colour,
    )

    @property
    def active_listings(self):
        return Listing.objects.filter(category=self, is_open=True)

    @property
    def num_listings(self):
        return len(self.active_listings)

    @classmethod
    def top_three(cls):
        """
        Method to get the three categories as determined by number
        of active listings
        :return:
        """

        # get categories in order of listings count
        categories = cls.objects.annotate(
            sum=Sum('listings__is_open')).order_by('-sum')

        # remove misc as it is likely always the largest category
        categories = categories.exclude(name='Misc')

        # ensure we return a list of three objects, even if no category
        # objects are found
        categories = list(categories[:3])
        categories.extend([None, None, None])
        return categories[:3]


def get_misc():
    try:
        m = Category.objects.get(name='Misc')
    except Category.DoesNotExist:
        m = Category(name='Misc')
        m.save()

    return m.pk


def rename_image_files(instance, filename):

    new_file_name = f'listing/{uuid4().hex}.png'
    logger.info(f'Renaming filename: {filename} > : {new_file_name}')

    return new_file_name


class Listing(models.Model):

    def __str__(self):

        status = 'Open' if self.is_open else 'Closed'
        title_summary = self.title[:10]
        if len(self.title):
            title_summary += '...'

        return f"<{self.owner.username}'s {status} Listing: {title_summary}>"

    title = models.CharField(max_length=64, verbose_name='Title')
    description = models.CharField(max_length=1000, verbose_name='Description')
    starting_bid = models.IntegerField(verbose_name='Starting Bid')
    is_open = models.BooleanField(default=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Owner',
        related_name='listings',
        null=True,
        blank=True,
    )
    photo = models.ImageField(
        upload_to=rename_image_files,
        blank=True
    )
    watchers = models.ManyToManyField(User)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Category',
        related_name='listings',
        default=get_misc,
    )

    @property
    def highest_bid(self):
        """
        Gets the current highest bid, or if no bids have currently been made,
        the starting bid
        :rtype: int
        """
        bids = self.bids.values()
        highest_bid = bids.aggregate(Max('value'))['value__max']
        return highest_bid or self.starting_bid

    @property
    def highest_bidder(self):
        """
        Find and return the user object that is linked to the bid with the
        highest value on the current listing. If no bid has been submitted,
        or the user cannot be found, None will be returned.
        :return: User that submitted the highest bid
        :rtype: :class:`User` or None
        """
        try:
            bids = self.bids.values()
            highest_bid = sorted(bids, key=lambda x: x['value'])[-1]
            highest_bidder = User.objects.get(pk=highest_bid['bidder_id'])
            return highest_bidder
        except IndexError:
            return
        except User.DoesNotExist:
            return

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

    @property
    def reverse_chronological_comments(self):
        return self.comments.order_by('-created_at')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Listing, self).save(
            force_insert, force_update, using, update_fields
        )

        if self.photo:
            max_height = 350
            max_width = 400
            logger.debug(f'Resizing to height {max_height}')

            path = self.photo.path
            logger.debug(f'Opening image at path: {path}')
            img = Image.open(path)

            logger.debug('Calculating resized image')
            height_percentage = max_height / float(img.size[1])
            new_width = int(float(img.size[0]) * float(height_percentage))
            img = img.resize((new_width, max_height), Image.ANTIALIAS)

            logger.debug('Checking width')
            width, height = img.size
            if width > max_width:
                margin = int((width - max_width) / 2)

                # calculate new bbox to crop evenly either side of wide image
                left = margin
                top = 0
                right = max_width + margin
                bottom = height

                logger.debug(
                    f'Cropping to shape: '
                    f'l={left}, t={top}, r={right}, b={bottom}'
                )
                img = img.crop((left, top, right, bottom))

            logger.debug('Resize complete, overwriting')
            # add png because we're renaming the files without an extension
            img.save(path)
            logger.debug('Saved.')


class Bid(models.Model):

    def __str__(self):
        return (
            f"<{self.bidder.username}'s bid of {self.value} "
            f"on {self.listing}>")

    listing = models.ForeignKey(
        Listing,
        related_name='bids',
        on_delete=models.CASCADE,
        verbose_name='Listing'
    )
    bidder = models.ForeignKey(
        User,
        related_name='bids',
        on_delete=models.CASCADE,
        verbose_name='Bidder'
    )
    value = models.IntegerField(verbose_name='Bid')


class Comment(models.Model):

    def __str__(self):
        return f"<{self.author.username}'s Comment: {self.content}>"

    listing = models.ForeignKey(
        Listing,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Listing'
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Author'
    )
    content = models.CharField(max_length=500, verbose_name='Content')
    created_at = models.DateTimeField(auto_now_add=True)
