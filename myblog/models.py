from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class signupModel(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)

class profileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')  # profile is the name by which we will access the model fields in posts.html file along with the posts
    bio = models.TextField()  # Default bio text
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png')


class postcreateModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Added user field
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)  # Optional: to track when the post was created

