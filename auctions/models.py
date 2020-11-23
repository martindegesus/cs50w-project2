from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
from django import forms


#Note: It is required to install Pillow Image processing API: https://pillow.readthedocs.io/en/stable/installation.html

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="+",
    )
    description = models.CharField(max_length=100, blank=False)
    date = models.DateField()
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user} {self.date}"


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, blank=False)
    
    def __str__(self):
        return f"{self.name}"

class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=16, unique=True)
    password = models.CharField(max_length=16)
    watchlist = models.ManyToManyField('Listing',blank=True,related_name="+")
    
    def __str__(self):
        return f"{self.username}"




class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="bidder"
    )
    price = models.PositiveIntegerField()
    date = models.DateField()
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} {self.price}"

class Listing(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owner"
    )
    description = models.TextField()
    #setting highestbid as nullable to avoid deadlock from saving both listing and bid
    highestbid = models.ForeignKey(Bid, null=True,blank=True, on_delete=models.CASCADE, related_name="max price+")
    category =  models.ForeignKey(Category,  null=True,blank=True, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to="image_uploader/")
    startDate = models.DateField()
    endDate = models.DateField()
    winner = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE)

    

    def __str__(self):
        return f"{self.title}"
