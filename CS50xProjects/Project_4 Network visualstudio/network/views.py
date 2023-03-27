from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from .models import User, Post, Follow, Like


def unlike(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(user=user, post=post)
    like.delete()
    return JsonResponse({"message": "Unliked!"})



def like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like(user=user, post=post)
    like.save()
    return JsonResponse({"message": "Liked!"})


def index(request):
    all_posts = Post.objects.all().order_by("id").reverse()

    # Pagination logic
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    post_page = paginator.get_page(page_number)
    
    allLikes = Like.objects.all()
    user_liked_posts = []

    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                user_liked_posts.append(like.post.id)
    except:
        user_liked_posts = []

    return render(request, "network/index.html", {
            "all_posts": all_posts,
            "post_page": post_page,
            "user_liked_posts": user_liked_posts,
    })
    

def edit(request, post_id):
    if request.method == "POST":
        edited_post_data = json.loads(request.body)
        post_to_be_edited = Post.objects.get(pk=post_id)
        post_to_be_edited.post_body = edited_post_data["post_body"]
        post_to_be_edited.save()
        
        return JsonResponse({"message": "Message has been edited", "edited_post_data": edited_post_data['post_body']})


def allpost(request):
    all_posts = Post.objects.all().order_by("id").reverse()

    # Pagination logic
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    post_page = paginator.get_page(page_number)

    return render(request, "network/allpost.html", {
        "all_posts": all_posts,
        "post_page": post_page
    })
    

def follow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowingData = User.objects.get(username=userfollow)
    f = Follow(user=currentUser, user_being_followed=userfollowingData)
    f.save()
    user_id = userfollowingData.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))


def unfollow(request):
    userunfollow = request.POST['userunfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userunfollowingData = User.objects.get(username=userunfollow)
    f = Follow.objects.get(user=currentUser, user_being_followed=userunfollowingData)
    f.delete()
    user_id = userunfollowingData.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))


def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    all_posts = Post.objects.filter(post_user=user.id).order_by("id").reverse()
    profileuser = User.objects.get(pk=user_id)

    # Pagination logic
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    post_page = paginator.get_page(page_number)

    # Following Logic
    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_being_followed=user)

    # Follow & Unfollow button Logic
    try:
        checkFollow = followers.filter(user=User.objects.get(pk=request.user.id))
        if len(checkFollow) !=0:
            isFollowing = True
        else:
            isFollowing = False
    except:
        isFollowing = False

    return render(request, "network/profile.html", {
        "all_posts": all_posts,
        "post_page": post_page,
        "following": following,
        "followers": followers,
        "profileuser": profileuser,
        "isFollowing": isFollowing,
    })


def following(request):
    currentUser = User.objects.get(pk=request.user.id)
    follow_list = Follow.objects.filter(user=currentUser)
    all_posts = Post.objects.all().order_by("id").reverse()
    follow_list_post = []

    for post in all_posts:
        for person in follow_list:
            if person.user_being_followed == post.post_user:
                follow_list_post.append(post)

    # Pagination logic
    paginator = Paginator(follow_list_post, 10)
    page_number = request.GET.get('page')
    post_page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "all_posts": all_posts,
        "post_page": post_page
    })
    


def new_post(request):
    if request.method == "POST":
        body = request.POST['post_body']
        user = User.objects.get(pk=request.user.id)
        post = Post(post_body=body, post_user=user)
        post.save()
    return HttpResponseRedirect(reverse(index))


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
