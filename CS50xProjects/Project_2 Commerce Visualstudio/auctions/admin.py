from django.contrib import admin
from . models import Listing, Category, Bid, User, Comment
# Register your models here.

admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(User)
admin.site.register(Comment)
