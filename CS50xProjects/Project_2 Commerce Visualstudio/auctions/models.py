from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

class User(AbstractUser):
    pass

class Category(models.Model):
    type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.type}"

class Listing(models.Model):
    name = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=300, null=True)
    imageUrl = models.CharField(max_length=300, null=True)
    isActive = models.BooleanField(default=True)
    price = models.DecimalField((""), max_digits=5, decimal_places=2, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="listingWatchlist")
    bid = models.DecimalField(MinValueValidator(price), max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name}"

    
        


class Bid (models.Model):
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE, blank=True, null=True, related_name="listing")
    bid = models.DecimalField((""), max_digits=10, decimal_places=2, null=True, blank=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="bidder")
    
    def __str__(self):
        return f"{self.bidder}: has bid ${self.bid}"


class Comment(models.Model):
    comment_on_listing = models.ForeignKey(Listing,on_delete=models.CASCADE, blank=True, null=True, related_name="comment_on_listing")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="commenter")
    comment = models.CharField(max_length=300, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.commenter} has commented{self.comment} on {self.comment_on_listing}"
