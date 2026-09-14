from django.db import models
import datetime
from django.conf import settings



class Category(models.Model):
    name=models.CharField(max_length=50)


    @staticmethod
    def get_all_categories():
        return  Category.objects.all()


    def __str__(self):
        return self.name


class Products(models.Model):
    name=models.CharField(max_length=60)
    price=models.IntegerField(default=0)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    description=models.CharField(max_length=250, default='', blank=True, null=True)
    image=models.ImageField(upload_to='uploads/product')

    @staticmethod
    def get_products_by_id(ids):
        return Products.objects.filter(id__in=ids)

    @staticmethod
    def get_all_products():
        return Products.objects.all()

    @staticmethod
    def get_all_product_by_category_id(category_id):
        if category_id:
            return Products.objects.filter(category=category_id)
        else:
            return Products.get_all_products()



class Order(models.Model):
    product=models.ForeignKey(Products,on_delete=models.CASCADE)
    customer=models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name="orders")
    quantity=models.IntegerField(default=1)
    price=models.IntegerField()
    address=models.CharField(max_length=50,default='',blank=True)
    phone=models.CharField(max_length=50,default='',blank=True)
    date=models.DateField(default=datetime.date.today)
    status=models.BooleanField(default=False)

    def placeOrder(self):
        self.save()

    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id).order_by('_date')

    class Meta:
        verbose_name_plural="Orders"

# Create your models here.
