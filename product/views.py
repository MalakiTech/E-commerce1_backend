from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import LoginSerializer,RegisterSerializer,UserSerializer,ProductSerializer,CategorySerializer,OrderSerializer
from .models import Category,Products



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





class ProductListView(APIView):
    permission_classes=[permissions.AllowAny]

    def get(self,request):
        category_id=request.GET.get("category")
        products=Products.get_all_product_by_category_id(category_id)
        categories=Category.get_all_categories()

        data={
            "products":ProductSerializer(products,many=True).data,
            "categories":CategorySerializer(categories,many=True).data,
        }
        return Response(data,status=status.HTTP_200_OK)

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
# Create your views here.
