from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import LoginSerializer,RegisterSerializer,UserSerializer,ProductSerializer,CategorySerializer,OrderSerializer
from .models import Category,Products
#for mpesa
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Order
from . import mpesa
#for registarion
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer




class RegisterView(generics.CreateAPIView):
    permission_classes=[permissions.AllowAny]
    serializer_class=RegisterSerializer

    def create(self,request,*args,**kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        token,_=Token.objects.get_or_create(user=user)
        return Response(
            {"user":UserSerializer(user).data,
            "token":token.key,},
            status=status.HTTP_200_OK,
        )


class loginView(APIView):
    permission_classes=[permissions.AllowAny]

    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data["user"]
        token,_=Token.objects.get_or_create(user=user)
        return Response(
                    {"user":UserSerializer(user).data,
                    "token":token.key,},
                    status=status.HTTP_201_CREATED,
                )



 



class LogoutView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def post(self,request):
        try:
            request.user.auth_token.delete()

        except(AttributeError, Token.DoesNotExist):
            pass
        return Response(
            {"detail":"Successfully logged out."},
            status=status.HTTP_200_OK
        )

class ProfileView(generics.RetrieveAPIView):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=UserSerializer

    def get_object(self):
        return self.request.user

    
#End of authentication and authorization





"""class ProductListView(APIView):
    permission_classes=[permissions.AllowAny]

    def get(self,request):
        category_id=request.GET.get("category")
        products=Products.get_all_product_by_category_id(category_id)
        categories=Category.get_all_categories()

        data={
            "products":ProductSerializer(products,many=True).data,
            "categories":CategorySerializer(categories,many=True).data,
        }
        return Response(data,status=status.HTTP_200_OK)"""


class ProductListView(generics.ListCreateAPIView):
    permission_classes=[permissions.AllowAny]
    queryset=Products.objects.all()
    serializer_class=ProductSerializer



class CartView(APIView):
    permission_classes=[permissions.AllowAny]
    def get(self,request):
        cart=request.session.get("cart",{})
        return Response({"cart":cart},status=status.HTTP_200_OK)

    def post(self,request):
        product=request.data.get("product")
        remove=request.data.get("remove")
        cart=request.session.get("cart",{})

        if product:
            pid=str(product)
            quantity=cart.get(pid,0)
        
        if remove:
        
            if quantity <= 1:
                 cart.pop(pid,None)
        
            else:
                 cart[pid]=quantity-1
        
        else:
          cart[pid]=quantity+1
        
        request.session['cart']=cart
        return Response({"cart":cart},status=status.HTTP_200_OK)


"""
class Index(View):
    def post(self, request):
        product=request.POST.get('product')
        remove=request.POST.get('remove')
        cart=request.session.get('cart',{})

        if product:
            pid=str(product)
            quantity=cart.get(pid,0)

            if remove:

                if quantity <= 1:
                    cart.pop(pid,None)

                else:
                    cart[pid]=quantity-1

            else:
                cart[pid]=quantity+1

        request.session['cart']=cart
        return redirect('homepage')

    def get(self, request):
        products=None
        categories=Category.get_all_categories()
        categoryID=request.GET.get('category')

        if categoryID:
            products=Products.get_all_products_by_catgoryid(categoryID)

        else:
            products=Products.get_all_products_by_categoryid(categoryID)

        data={'products':products,
              'categories':categories}
        return render(request,'index.html',data)
    def store(request):
        return render(request,'store.html')
    
        

        

"""


#This is for Mpesa
class CheckoutView(APIView):
    """POST /api/mpesa/checkout/  body: {phone, amount, items:[{id,name,price,qty}]}"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone = request.data.get("phone")
        amount = request.data.get("amount")
        items = request.data.get("items")
        if not phone or not amount or not items:
            return Response({"error": "phone, amount and items are required"}, status=400)

        try:
            result = mpesa.stk_push(
                phone=phone,
                amount=amount,
                account_ref=f"MALAKI-{request.user.id}",
            )
        except Exception as exc:
            return Response({"error": f"Could not initiate M-Pesa payment: {exc}"}, status=500)

        if result.get("ResponseCode") != "0":
            return Response({"error": result.get("ResponseDescription", "STK push failed")}, status=400)

        order = Order.objects.create(
            user=request.user,
            items=items,
            amount=amount,
            phone=phone,
            checkout_request_id=result["CheckoutRequestID"],
            merchant_request_id=result.get("MerchantRequestID", ""),
        )
        return Response({
            "message": "STK push sent. Enter your M-Pesa PIN on your phone to complete payment.",
            "checkoutRequestId": order.checkout_request_id,
        })


class StatusView(APIView):
    """GET /api/mpesa/status/<checkout_request_id>/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, checkout_request_id):
        try:
            order = Order.objects.get(checkout_request_id=checkout_request_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        return Response({"status": order.status, "mpesaReceipt": order.mpesa_receipt or None})


class CallbackView(APIView):
    """POST /api/mpesa/callback/ — called server-to-server by Safaricom. Must be public HTTPS."""
    permission_classes = [AllowAny]

    def post(self, request):
        stk_callback = request.data.get("Body", {}).get("stkCallback", {})
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")

        try:
            order = Order.objects.get(checkout_request_id=checkout_request_id)
        except Order.DoesNotExist:
            return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

        if result_code == 0:
            meta = {
                item["Name"]: item.get("Value")
                for item in stk_callback.get("CallbackMetadata", {}).get("Item", [])
            }
            order.status = "paid"
            order.mpesa_receipt = meta.get("MpesaReceiptNumber", "")
            order.save()

            rows = "".join(
                f"- {i['name']} x{i['qty']}: ${i['price']*i['qty']:.2f}\n" for i in order.items
            )
            send_mail(
                subject="Your Malaki order is confirmed",
                message=(
                    f"Hi {order.user.first_name or order.user.username},\n\n"
                    f"Thank you for your payment of KES {meta.get('Amount')}. "
                    f"Your M-Pesa receipt number is {order.mpesa_receipt}.\n\n"
                    f"{rows}\nWe'll notify you once your order ships.\n\n— Malaki"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.user.email],
                fail_silently=True,
            )
        else:
            order.status = "failed"
            order.save()

        # Safaricom just needs a 200 acknowledging receipt
        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})


#for registration
def issue_token(user):
    token = RefreshToken.for_user(user)
    return str(token.access_token)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"token": issue_token(user), "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        # Notify the user of this login by email. Don't fail the login if email sending errors.
        try:
            send_mail(
                subject="New login to your Malaki account",
                message=(
                    f"Hi {user.first_name or user.username},\n\n"
                    "We noticed a new login to your Malaki account just now. "
                    "If this wasn't you, please reset your password immediately.\n\n— Malaki"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass

        return Response({"token": issue_token(user), "user": UserSerializer(user).data})


# Create your views here.
