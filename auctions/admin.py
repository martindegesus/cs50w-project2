from django.contrib import admin
from .models import Listing,Bid,Comment,Category, User

# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    list_display=("title","highestbid")
admin.site.register(Listing,ListingAdmin)

class BidAdmin(admin.ModelAdmin):
    list_display=("user","date","price")
admin.site.register(Bid,BidAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display=("user","description","listing")
admin.site.register(Comment,CommentAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display=("id","name")
admin.site.register(Category,CategoryAdmin)

