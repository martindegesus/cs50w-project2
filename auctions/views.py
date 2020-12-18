from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from .models import User,Listing,Bid,Comment,Category
from .forms import ListingForm, CommentForm, BidForm
import datetime
from urllib.request import urlopen
import imghdr
from django.core.exceptions import ValidationError

def active(listing):
    if listing.endDate>=datetime.date.today():
        return True

def index(request):
    # if user is logged the system checks if the user won any bids, otherwise it just renders without checking
    if request.user.is_authenticated:
        for listing in Listing.objects.all():
            if not active(listing):
                if not listing.highestbid.user == listing.user:
                    listing.winner=listing.highestbid.user
                    listing.save()
    # create an array with all the active listings
    activelistings= []
    for listing in Listing.objects.all():
        if active(listing):
            activelistings.append(listing)
    
    if request.user.is_authenticated:        
        return render(request, "auctions/index.html",{
            "activelistings": activelistings,
            "listings": Listing.objects.all(),
            "watchlist": request.user.watchlist,
            "user": request.user
        })
    else:
        return render(request, "auctions/index.html",{
            "activelistings": activelistings,
            "listings": Listing.objects.all(),
            "user": request.user
    })

def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request, "auctions/index.html",{
        "listings": request.user.watchlist.all(),
        "renderingwatchlist": "true"
    })

def categories(request):
    
    return render(request, "auctions/categories.html",{
        "categories": Category.objects.all()
    })

def categorieslisting(request,id):
    
    return render(request, "auctions/index.html",{
        "listings": Listing.objects.all().filter(category=id)
    })

def comment(request,id):
    if request.method == "POST":
        if 'save_comment' in  request.POST:
            newcomment=Comment(user=request.user,description=request.POST["description"],date=datetime.date.today(),listing=Listing.objects.get(pk=request.POST["id"]))
            newcomment.save()
            commentForm = CommentForm
            return render(request, "auctions/listing.html",{
                    "listing": Listing.objects.get(pk=id),
                    "highestbid": get_highestbid(id),
                    "commentForm": commentForm
                })

def get_highestbid(id):
    bidslist=Bid.objects.all().filter(listing=id)
    highestbid = 0
    for bids in bidslist:
        if bids.price > highestbid:
            highestbid = bids.price
    return highestbid

def get_minbid(id):
    gap = 1
    if (len(Bid.objects.all().filter(listing=id))==1):
        gap = 0
    return get_highestbid(id)+gap

def listing(request,id):
    commentslist=Comment.objects.all().filter(listing=id)
    highestbid=get_highestbid(id)
    listing=Listing.objects.get(pk=id)
    bidform=BidForm
    if request.method == "POST":
        if 'save_bid' in request.POST:
            newbid=Bid(listing=listing,user=request.user,date=datetime.date.today(),price=request.POST["price"])
            highestbid = get_highestbid(id)
            bidform=BidForm(request.POST, request=request)
            if bidform.is_valid():
                newbid.save()
                highestbid = get_highestbid(id)   
        if 'save_comment' in  request.POST:
            newcomment=Comment(user=request.user,description=request.POST["description"],date=datetime.date.today(),listing=Listing.objects.get(pk=request.POST["id"]))
            newcomment.save()
            commentslist=Comment.objects.all().filter(listing=id)
        watchlist=request.user.watchlist
        id = request.POST["id"]
        if 'add_watchlist' in  request.POST:
            watchlist.add(Listing.objects.get(pk=id)) 
            request.user.save()
        if 'remove_watchlist' in  request.POST:
            watchlist.remove(Listing.objects.get(pk=id))
            request.user.save()
        if 'close' in  request.POST:
            listing.endDate=datetime.date.today()-datetime.timedelta(days=2)
            listing.winner=listing.highestbid.user
            listing.save()
    if request.user.is_authenticated:
        watchlist=request.user.watchlist
    else:
        watchlist=[]
    return render(request, "auctions/listing.html",{
                "bidform":bidform,
                "listing": Listing.objects.get(pk=id),
                "highestbid": get_highestbid(id),
                "commentslist": commentslist,
                "commentForm": CommentForm,
                "minbid": get_minbid(id),
                "active": active(Listing.objects.get(pk=id)),
                "user": request.user,
                "watchlist": watchlist
            })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        print(request.POST["image"])
        listing = Listing(
            title=request.POST["title"],
            user= request.user,
            description=request.POST["description"],
            startDate= datetime.date.today(),
            endDate= datetime.date.today()+datetime.timedelta(days=2)
        )
        if (request.POST["category"]==''):
            listing.category=None
        else:
            listing.category=Category.objects.get(pk=request.POST["category"])
        if (request.POST["image"]==''):
            listing.image=None
        else:
            listing.image=request.POST["image"]
        form = listing
        form = ListingForm(request.POST)
        form.is_valid()
        listing.save()

        newbid=Bid(listing=listing,user=User.objects.get(pk=request.user.id),date=datetime.date.today(),price=request.POST["startingbid"])
        
        newbid.listing=listing
        newbid.save()
        listing.highestbid=newbid
        listing.save()


    form=ListingForm
    return render(request, "auctions/create.html",{'form':form, "user": request.user})