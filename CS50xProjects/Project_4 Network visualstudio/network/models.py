from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    post_user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="post")
    post_body = models.TextField(blank=True)
    post_timestamp = models.DateTimeField(auto_now_add=True)
    #like = models.ManyToOneRel("User", related_name="post_likes")

def __str__(self):
    return f"POST {self.id} posted by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"
        

class Follow(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="follower")
    user_being_followed = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followed")

def __str__(self):
    return f"{self.user} is following {self.user_being_followed}"


class Like(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user_like")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="post_like")

    def __str__(self):
        return f"{self.user} has liked {self.post}"