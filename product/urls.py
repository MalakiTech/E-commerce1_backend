
from django.urls import path
from .views import LogoutView,loginView,ProfileView,RegisterView,ProductListView,CartView,LoginView,CheckoutView,CallbackView,StatusView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,)




urlpatterns = [
     
     path("register/",RegisterView.as_view()),
     #path("login/",loginView.as_view()),
     path("logout/",LogoutView.as_view()),
     path("profile/",ProfileView.as_view()),
     path("products/",ProductListView.as_view()),
     path("cart/",CartView.as_view()),
     path("api/token",TokenObtainPairView.as_view()),
     path("api/token/refresh/",TokenRefreshView.as_view()),
     path("checkout/", CheckoutView.as_view(), name="mpesa-checkout"),
     path("status/<str:checkout_request_id>/", StatusView.as_view(), name="mpesa-status"),
     path("callback/", CallbackView.as_view(), name="mpesa-callback"),
     path("register/", RegisterView.as_view(), name="register"),
     path("login/", LoginView.as_view(), name="login"),
 
     

]