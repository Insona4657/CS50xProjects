from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createListing/", views.createListing, name="createListing"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("show_watchlist/", views.show_watchlist, name="show_watchlist"),
    path("addwatchlist/<int:id>", views.addwatchlist, name="addwatchlist"),
    path("removewatchlist/<int:id>", views.removewatchlist, name="removewatchlist"),
    path("addComment/<int:id>", views.addComment, name="addComment"),
    path("addbid/<int:id>", views.addbid, name="addbid"),
    path("displayCategory", views.displayCategory, name="displayCategory"),
    path("close_auction/<int:id>", views.close_auction, name="close_auction"),
    #path("edit/<int:id>", views.edit, name="edit"),
]
