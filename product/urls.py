from django.contrib import admin
from django.urls import path
from .views import LogoutView,loginView,ProfileView,RegisterView,ProductListView,CartView

urlpatterns = [
     
     path("register/",RegisterView.as_view()),
     path("login/",loginView.as_view()),
     path("logout/",LogoutView.as_view()),
     path("profile/",ProfileView.as_view()),
     path("products/",ProductListView.as_view()),
     path("cart/",CartView.as_view()),
     
     

]