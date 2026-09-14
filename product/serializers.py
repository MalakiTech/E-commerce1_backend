from django.contrib.auth import get_user_model,authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Category,Order,Products

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,required=True,validators=[validate_password])
    password2=serializers.CharField(write_only=True, required=True)

    class Meta:
        model=User
        fields = ("username","email","password","password2")

    def validate(self, attrs):
        if attrs["password"]!= attrs["password2"]:
            raise serializers.ValidationError({"password":"password fiels didnt match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user=User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email",""),
            password=validated_data["password"],
        )
        return user

class LoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs.get("username"),
            password=attrs.get("password")
        )
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is disabled.")
        attrs["user"]=user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=("id","username","email")



#Serializing data from models
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Products
        fields='__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields='__all__'


