from django.contrib import admin

from .models import (
    Listing,
    Comment,
    Bid,
    Category,
)

admin.site.register(Listing)
admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(Category)
