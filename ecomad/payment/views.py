from django.shortcuts import render,redirect
from cart.cart import Cart
from payment.forms import ShippingForm,PaymentForm
from payment.models import shippingAddress,Order,OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product,Profile
import datetime
 

def orders(request,pk):
  if request.user.is_authenticated and request.user.is_superuser:
    order = Order.objects.get(id=pk)
    items = OrderItem.objects.filter(order=pk)

    if request.POST:
      status = request.POST['shipping_status']
      if status == "true" :
        order = Order.objects.filter(id=pk)
        now = datetime.datetime.now()
        order.update(shipped=True,date_shipped=now)
      else:
        order = Order.objects.filter(id=pk)
        order.update(shipped=False)
      messages.success(request,"Shipping Status Updated")
      return redirect('home')

    return render(request,'payment/orders.html',{"order":order,"items":items})
  else:
    messages.success(request, "Access Denied")
    return redirect ('home')





def not_shipped_dash(request):
  if request.user.is_authenticated and request.user.is_superuser:
    orders = Order.objects.filter(shipped=False)
    if request.POST:
      status = request.POST['shipping_status']
      num = request.POST['num']
      order =Order.objects.filter(id=num)
      now = datetime.datetime.now()
      order.update(shipped=True,date_shipped=now)
      
      messages.success(request,"Shipping Status Updated")
      return redirect('home')

    return render(request,'payment/not_shipped_dash.html',{"orders":orders})
  else:
    messages.success(request, "Access Denied")
    return redirect ('home')

  

def shipped_dash(request):
  if request.user.is_authenticated and request.user.is_superuser:
    orders = Order.objects.filter(shipped=True)
    
    if request.POST:
      status = request.POST['shipping_status']
      num = request.POST['num']
      order =Order.objects.filter(id=num)
      now = datetime.datetime.now()
      order.update(shipped=False)
      
      messages.success(request,"Shipping Status Updated")
      return redirect('home')
    return render(request,'payment/shipped_dash.html',{"orders":orders})
  else:
    messages.success(request, "Access Denied")
    return redirect ('home')

  

def process_order(request):
  if request.POST:
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totles = cart.cart_total()
    payment_form = PaymentForm(request.POST or None)

    my_shipping = request.session.get('my_shipping') 

    full_name = my_shipping['shipping_full_name']
    email = my_shipping['shipping_email']

    shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
    amount_paid = totles

    if request.user.is_authenticated:
      user = request.user

      create_order = Order(user=user,full_name=full_name,email=email,shipping_address=shipping_address,amount_paid=amount_paid)
      create_order.save()

      order_id = create_order.pk

      for product in cart_products():
        product_id =product.id
        if product.is_sale:
          price= product.sale_price
        else:
          price = product.price

        for key,value in quantities().items():
          if int(key) == product.id:
            create_order_item = OrderItem(order_id=order_id,product_id=product_id,user=user,quantity=value,price=price)
            create_order_item.save()

      # Delete our cart
      for key in list (request.session.keys()):
        if key == "session_key":
          #Delete the key
          del request.session[key]

      #Delete Cart from Database(old_cart field)
      current_user = Profile.objects.filter(user__id=request.user.id)
      # Delete shopping cart in dateabase (old_cart field)
      current_user.update(old_cart="")

      messages.success(request, "Order Placed!")
      return redirect ('home')
    else:
      create_order = Order(full_name=full_name,email=email,shipping_address=shipping_address,amount_paid=amount_paid)
      create_order.save()

      order_id = create_order.pk

      for product in cart_products():
        product_id =product.id
        if product.is_sale:
          price= product.sale_price
        else:
          price = product.price

        for key,value in quantities().items():
          if int(key) == product.id:
            create_order_item = OrderItem(order_id=order_id,product_id=product_id,quantity=value,price=price)
            create_order_item.save()
      # Delete our cart
      for key in list (request.session.keys()):
        if key == "session_key":
          #Delete the key
          del request.session[key]

      messages.success(request, "Order Placed!")
      return redirect ('home')
      
    
    

  else:
    messages.success(request, "Access Denied")
    return redirect ('home')



def billing_info(request):
  if request.POST:
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totles = cart.cart_total()

    # Create a session with Shipping Info
    my_shipping = request.POST
    request.session['my_shipping'] = my_shipping

    #Check to see if user is logged in
    if request.user.is_authenticated:
      # Get the billing Form
      billing_form = PaymentForm()
      return render(request,'payment/billing_info.html',{"cart_products":cart_products,"quantities":quantities,"totles":totles,"shipping_info":request.POST,"billing_form": billing_form})
    else:
      # not loged in
      billing_form = PaymentForm()
      return render(request,'payment/billing_info.html',{"cart_products":cart_products,"quantities":quantities,"totles":totles,"shipping_info":request.POST,"billing_form":billing_form})
    
  else:
    messages.success(request, "Access Denied")
    return redirect ('home')




  

def checkout(request):
  cart = Cart(request)
  cart_products = cart.get_prods
  quantities = cart.get_quants
  totles = cart.cart_total()

  if request.user.is_authenticated:
    # Checkout as logged in user
    #Shipping user
    shipping_user = shippingAddress.objects.get(user__id=request.user.id)
    shipping_form = ShippingForm(request.POST or None, instance = shipping_user)
    return render(request,'payment/checkout.html',{"cart_products":cart_products,"quantities":quantities,"totles":totles,"shipping_form":shipping_form})
  else:
    # Checkout as guest
    shipping_form = ShippingForm(request.POST or None)
    return render(request,'payment/checkout.html',{"cart_products":cart_products,"quantities":quantities,"totles":totles,"shipping_form":shipping_form})

  


def payment_success(request):
  return render (request,'payment/payment_success.html',{})
