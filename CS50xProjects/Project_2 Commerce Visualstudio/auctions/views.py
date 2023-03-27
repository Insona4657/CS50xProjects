from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Category, Listing, Bid, Comment


def show_watchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/show_watchlist.html", {
        "listings":listings,
    })


def addwatchlist(request, id):
    name = Listing.objects.get(pk=id)
    currentUser = request.user
    name.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def removewatchlist(request, id):
    name = Listing.objects.get(pk=id)
    currentUser = request.user
    name.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def addComment(request, id):
    name = Listing.objects.get(pk=id)
    commentdata = request.POST["newComment"]
    user = request.user
    newComment=Comment(
        commenter=user,
        comment_on_listing=name,
        comment=commentdata
    )

    newComment.save()
    return HttpResponseRedirect(reverse('listing',args=(id, )))

def displayCategory(request):
    if request.method == "POST":
        categoryselected = request.POST['category']
        category = Category.objects.get(type=categoryselected)
        activelistings = Listing.objects.filter(isActive=True, category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/category.html", {
            "categories": allCategories,
            "listings": activelistings
        })
    else:
        activelistings = Listing.objects.filter(isActive=True)
        allCategories = Category.objects.all()
        return render(request, "auctions/category.html", {
            "categories": allCategories,
            "listings": activelistings
        })


def createListing(request):
    if request.method=="GET":
        allCategories = Category.objects.all()
        return render (request, "auctions/createListing.html", {
            "categories": allCategories
        })
    else:
        #Get Data from form
        name = request.POST["name"]
        description = request.POST["description"]
        image_url = request.POST["image"]
        price = request.POST["price"]
        user = request.user
        category = request.POST.get("category")
        bid = request.POST["bid"]

        #Get all content about particular category
        categoryData = Category.objects.get(type=category)

        #Create a new listing object
        newListing = Listing(
            name=name,
            description=description,
            imageUrl=image_url,
            price=float(price),
            owner=user,
            category=categoryData,
            bid= bid,
        )

        newListing.save()
        return HttpResponseRedirect(reverse(index))


def index(request):
    activeListings = Listing.objects.filter(isActive=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allCategories
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


def addbid(request, id):
    newbid = request.POST['bid']
    itemname = Listing.objects.get(pk=id)
    allComments = Comment.objects.filter(comment_on_listing=itemname)
    isListinginWatchlist = request.user in itemname.watchlist.all()
    isOwner = request.user == itemname.owner
    if int(newbid) > itemname.bid:
        updatebid = Bid(
            bidder=request.user,
            bid=int(newbid)
        )
        updatebid.save()
        itemname.bid = newbid
        itemname.save()
        return render(request, "auctions/listing.html", {
            "listing": itemname,
            "message": "Bid Updated Successfully",
            "update": True,
            "allComments": allComments,
            "isListinginWatchlist": isListinginWatchlist,
            "isOwner": isOwner,
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing":itemname,
            "message":"Bid not high enough",
            "update": False,
            "allComments": allComments,
            "isListinginWatchlist": isListinginWatchlist,
            "isOwner": isOwner,
        })


def listing(request, id):
    name = Listing.objects.get(pk=id)
    isListinginWatchlist = request.user in name.watchlist.all()
    allComments = Comment.objects.filter(comment_on_listing=name)
    allBids = Bid.objects.all()
    currentuserbids = allBids.filter(bidder=request.user)
    lastbidbyuser = currentuserbids.last()
    lastbidusername = lastbidbyuser.bidder
    isOwner = request.user == name.owner
    currentuserusername = request.user.username
    isAuctionWinnercurrentuser = str(lastbidusername) == str(currentuserusername)
    
    return render(request, "auctions/listing.html", {
        "listing": name,
        "isListinginWatchlist": isListinginWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "isAuctionWinnercurrentuser":isAuctionWinnercurrentuser,
        "lastbidusername": lastbidusername,
        "currentuserusername": currentuserusername,
    })


def close_auction(request, id):
    name = Listing.objects.get(pk=id)
    name.isActive = False
    name.save()
    isListinginWatchlist = request.user in name.watchlist.all()
    allComments = Comment.objects.filter(comment_on_listing=name)
    isOwner = request.user == name.owner
    return render(request, "auctions/listing.html", {
        "listing": name,
        "isListinginWatchlist": isListinginWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "update": True,
        "message": "Congratulations your auction has ended",


    })







        
