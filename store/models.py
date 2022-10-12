from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# We're putting the 'null' & 'blank' argumetns to Ture for not getting any Error while building classes and testing'em.

#* ``Customer`` can be a ``User`` or a ``Guest`` BUT ``User`` can only be ``Customer``
class Customer(models.Model):
    #? ONE to ONE Relationship.
    # A User can only be one Customer & a Customer can ony be one User.
    # on_delete=models.CASCADE: For deleting this 'Customer' item when the 'User' item is deleted.
    #                           delete the customer when the user gets deleted.
    user  = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name  = models.CharField(max_length=120, null=True)
    email = models.EmailField(null=True)
    # This is the value that's gonna shows up in the Admin panel when we create the Model.
    def __str__(self):
        return self.name


class Product(models.Model):
    name    = models.CharField(max_length=120, null=True)
    price   = models.DecimalField(max_digits=100, decimal_places=2)
    # default=False: Most of the products is physical and need shipping.
    digital = models.BooleanField(default=False, null=True, blank=False)
    image   = models.ImageField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    # model (class) method.
    @property # So we can access it as an attribute.
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

# One Customer can have Many Orders, (Order = Cart)
class Order(models.Model):
    #? MANY to ONE Relationship.
    # A Customer can have multiple Orders.
    # on_delete = models.SET_NULL: So if a Customer gets deleted.
    # Set the customer field to 'null' when the customer gets deleted don't deleted the order 
    customer      = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    dateOrdered   = models.DateTimeField(auto_now_add=True)
    # Cart status whether its still open 'Flase' to keep add items for example OR closed to do something else.
    complete      = models.BooleanField(default=False)
    transactionID = models.CharField(max_length=60, null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
    @property
    def need_shipping(self) -> bool:
        shipping   = False # Order Items don't need to be shipped.
        orderItems = self.orderitem_set.all()
        for item in orderItems:
            if item.product.digital == False: # if any of the order items is not digital 
                shipping = True
        return shipping

    @property
    def get_cart_items(self):
        orderItems       = self.orderitem_set.all()
        cartTotalNumber  = sum([item.quantity for item in orderItems])
        return cartTotalNumber
    @property
    def get_cart_total(self):
        orderItems      = self.orderitem_set.all()
        cartTotalPrice  = sum([item.get_orderItem_total for item in orderItems ])
        return cartTotalPrice

# Remember: One Order can have Many Order Items & One Product can be in Many Order Items (as a quantity).
# How many items are there in the whole order.
# 18 item (distributed on 6 Rolex-Watch, 7 T-Shirts, 5 Books)
class OrderItem(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    # The same product can be placed as an order item many times as the customer specify the quantity.
    # Rolex-Watcg, T-Shirts, Books
    product    = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    # How many items the Customer wants form this Product.
    # 6 Rolex-Watch, 7 T-Shirts, 5 Books
    quantity   = models.IntegerField(default=0, null=True, blank=True)
    # The date we add the item to our order.
    dateAdded  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order.id)
        
    @property
    def get_orderItem_total(self):
        return (self.product.price * self.quantity)


class ShippingAddress(models.Model):
    # NOTE: The order field and the customer field here in this model are realistically the same.
    # The Same Order can be shipped to Many places.
    order     = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    # The Same Customer can have Many shipping addresses, It's set to null on_delete bcz we want to keep the user's location data, For cookies purposes.
    customer  = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    state     = models.CharField(max_length=120, null=True, blank=True)
    city      = models.CharField(max_length=120, null=True, blank=True)
    address   = models.CharField(max_length=120, null=True, blank=True)
    zipCode   = models.CharField(max_length=120, null=True, blank=True)
    dateAdded = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.address
