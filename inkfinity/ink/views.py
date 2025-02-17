import json
from django.shortcuts import render,HttpResponse,get_object_or_404,redirect
from .models import product,contact,Cart,OrderItem,Order
from math import ceil
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required


def home(request):
    allProds = []
    
    # Get unique categories
    catProds = product.objects.values('category', 'id')
    cats = {item['category'] for item in catProds}

    for cat in cats:
        prod = product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    # 🔹 Get specific categories separately
    new_products = product.objects.filter(category="new")
    men_tshirt = product.objects.filter(category="men Tshirt")
    women_collection = product.objects.filter(category="women collection")
    watch = product.objects.filter(category="watch")

    params = {
        'allProds': allProds,  
        'new_products': new_products,  
        'men_tshirt': men_tshirt,  
        'women_collection': women_collection,
        'watch':watch
    }
    
    return render(request, 'ink/index1.html', params)


def about(request):
    return render(request,'ink/about.html')

def contact_view(request):

    if request.method == "POST":
        print(request)
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone= request.POST.get('phone','')
        desc = request.POST.get('desc','')
        newcontacts = contact(name=name,email=email,phone=phone,desc=desc)
        newcontacts.save()

    return render(request,'ink/contact.html')

def tracker(request):
    return render(request,'ink/tracker.html')

def prodView(request, id):
    product_instance = product.objects.get(id=id)  # Fetch a single object
    print(product_instance)
    return render(request, 'ink/prodView.html', {'products': product_instance})

def checkout(request):
    return HttpResponse("checkout")




def add_to_cart(request, product_id):
    if request.method == 'GET' and request.user.is_authenticated:
        # Ensure 'Product' is used with the correct capitalization
        product_instance = get_object_or_404(product, id=product_id)

        # Check if the product is already in the cart
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product_instance,
            defaults={'quantity': 1}  # Default quantity is set to 1
        )

        if not created:
            # If the item already exists in the cart, increase the quantity
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({'success': True, 'message': f'{product_instance.product_name} has been added to your cart!'})
    
    # Return an error if the user is not authenticated or method is incorrect
    return JsonResponse({'success': False, 'message': 'You need to be logged in to add items to the cart or invalid request method.'}, status=400)


def cart_view(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'ink/cart.html', {'cart_items': cart_items, 'total_price': total_price})
    else:
        return redirect('login') 

    
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after registration
            return redirect('home')  # Redirect to home or another page
    else:
        form = CustomUserCreationForm()
    return render(request, 'ink/register.html', {'form': form})




class CustomLogoutView(SuccessMessageMixin, LogoutView):
    success_message = "You have successfully logged out."


def delete_cart_item(request, item_id):
    # Retrieve the cart item by its ID
    cart_item = get_object_or_404(Cart, id=item_id)
    
    # Delete the item from the cart
    cart_item.delete()
    
    # Redirect back to the cart page
    return redirect('cart')

from django.shortcuts import render, redirect
from .models import Cart, Order, OrderItem
from .utils import send_sms  # Assuming you've created the send_sms function for Twilio

def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if cart_items.exists():  # Ensure cart is not empty
        # Calculate total price
        total_price = sum([item.product.price * item.quantity for item in cart_items])
    else:
        total_price = 0  # If no items in cart, set total price to 0

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')

        # Create an order
        order = Order.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            email=email,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            total_price=total_price
        )

        # Add all cart items to the order as OrderItems
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        # Clear the cart after order is placed
        cart_items.delete()

        # Send SMS to the user
        sms_message = f"Hi {name}, your order has been confirmed! Order Total: ₹{total_price}. Thank you for shopping with us!.You will get your order within 6 to 7 days."
        sms_response = send_sms(phone, sms_message)

        # Debugging SMS Response (Optional)
        if sms_response.get("success"):
            print("SMS sent successfully!")
        else:
            print(f"Failed to send SMS: {sms_response.get('error')}")

        # Redirect to the order summary page
        return redirect('order_summary')

    return render(request, 'ink/checkout.html', {
        'cart_items': cart_items, 
        'total_price': total_price
    })

@login_required
def order_summary(request):
    return render(request, 'ink/order_summary.html')
