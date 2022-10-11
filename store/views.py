from django.shortcuts import render
from django.http      import JsonResponse
from .models          import *
import json
import datetime as dt

# Create your views here.
def store_view(request):
    productQuerySet = Product.objects.all()
    
    if request.user.is_authenticated:
        customer       = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # orderItems     = order.orderitem_set.all()
        cartTotalItems = order.get_cart_items
    else:
        # orderItems     = []
        order          = {'get_cart_items' : 0, 'get_cart_total' : 0, 'need_shipping' : False}
        cartTotalItems = order['get_cart_items']
    
    context = {
        'products'      : productQuerySet,
        'cartTotalIcon' : cartTotalItems
    }
    return render(request, 'store/store.html', context)

def cart_view(request):
    # Check if the Customer is authenticated:
    if request.user.is_authenticated:   # Customer - User
        # Registered Customer => User
        # => Get the Customer Class associated with it thru the User class:
        customer       = request.user.customer
        # Get a certiain Order (open cart) attached to the Customer OR create that certain order (that open cart) if it Doesn't exist. 
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # Get the order items attached to that order & Display them in the cart page.
        orderItems     = order.orderitem_set.all() # list
        # We're able to capture the child objects (that represent Many to parent object that represents One)
        cartTotalItems = order.get_cart_items
    # We can't return nothig here in the else statement because it'll loop between here and 'cart.html' page.
    else:                               # Customer - Guest
        orderItems     = []
        order          = {'get_cart_items' : 0, 'get_cart_total': 0, 'need_shipping' : False}
        cartTotalItems = order['get_cart_items']
    
    context = {
        'items'         : orderItems,
        'order'         : order,
        'cartTotalIcon' : cartTotalItems
    }
    return render(request, 'store/cart.html', context)

def checkout_view(request):
    if request.user.is_authenticated:
        customer       = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItems     = order.orderitem_set.all()
        cartTotalItems = order.get_cart_items
    else:
        orderItems = [] # Empty Order 
        order      =  {'get_cart_items' : 0, 'get_cart_total' : 0, 'need_shipping' : False} # Empty Totals
        cartTotalItems     = order['get_cart_items']

    context = {
        'items'         : orderItems,
        'order'         : order,
        'cartTotalIcon' : cartTotalItems
    }
    return render(request, 'store/checkout.html', context)
# For the "Add to Cart" Button in the 'store.html' & "Up-Down arrows" in the 'cart.html'| Expecting Values Only, Returning Json type.
def update_item_function(request): 
    #*Grabbing Data from the Front-End.
    # Parse json data to a Python dictionary.
    data      = json.loads(request.body) # Parsing Data: 'str' => 'dict'.
    # Accessing data variable contents. (dictionary keys)
    productId = data['productId']
    action    = data['action']
    #*Processing Data.
    customer           = request.user.customer
    product            = Product.objects.get(id=productId)
    # Create an open cart to the customer (to add products (id est: items) to it) or Add to his opened cart if he's already has one.
    order, created     = Order.objects.get_or_create(customer=customer, complete=False)
    # Create the order item in the customer's cart (instantiate the OrderItem Class) or just get it to double it as many as he wants(just change the quantity field)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    #*Control the Quantity of the order item in the Cart, Update the quantity based on the action.
    if action   == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1
    
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Data is being Processed...', safe=False) # 'safe' is False So we can pass non-dict-Format data to be dumped into json.
# For the "Make Payment" Button in the 'checkout.html'| Expecting Values Only, Returning Json Type.
def process_order_function(request):
    transactionId = dt.datetime.now().timestamp()
    data          = json.loads(request.body) # Primary Keys: `UserInfo` & `ShippingInfo`.
    # Processing the order for the Authenticated User.
    if request.user.is_authenticated:
        customer            = request.user.customer     # Quering the User Peronal Info from the Database. (name and email)
        total               = float(data['UserInfo']['total']) # Quering the Total Price for all the order items in the Customer's Cart.
        order, created      = Order.objects.get_or_create(customer=customer, complete=False)
        order.transactionID = transactionId
        #*Checking if the `total` passed in from the Front-End Equals the total of the order items in the Back-End.
        # Hackers (if they know javascript) can manipulate that.
        if total == float(order.get_cart_total):
            order.complete = True
        order.save() # Save the Order regardless of if the User has manipulated the data or not. (helps setting up a 'trap' for the hackers)
        #*Creating an instance of the class 'ShippingAddress' if the Shipping Information was sent.
        if order.need_shipping == True:
            ShippingAddress.objects.create(
                order    = order,
                customer = customer,
                state    = data['ShippingInfo']['state'],
                city     = data['ShippingInfo']['city'],
                address  = data['ShippingInfo']['address'],
                zipCode  = data['ShippingInfo']['zipCode']
            )
    else:
        print("\"Guest Customer Checkout\" is Not available for Basic Version!.")
    return JsonResponse('Submitted, Form has got Processed in the Back-End', safe=False)
