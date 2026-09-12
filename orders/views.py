from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from shop.models import Product
from .cart import Cart
from .models import Order, OrderItem


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = min(max(quantity, 1), 20)

    phone_model = request.POST.get('phone_model', '').strip()
    if not phone_model:
        messages.error(request, "Iltimos, telefon modelingizni tanlang.")
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'shop:home'
        return redirect(next_url)

    cart.add(product=product, quantity=quantity, phone_model=phone_model)
    messages.success(request, f"“{product.name}” savatga qo'shildi.")
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'shop:home'
    return redirect(next_url)


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('orders:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'orders/cart_detail.html', {'cart': cart})


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Savatingiz bo'sh.")
        return redirect('shop:home')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()

        order = Order.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            phone_number=phone_number,
            address=address,
        )
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity'],
                phone_model=item.get('phone_model', '') or item['product'].phone_model,
            )

        order_lines = "\n".join(
            f"- {item.product.name} ({item.phone_model or item.product.phone_model}) x{item.quantity} = {item.get_cost()} so'm"
            for item in order.items.all()
        )
        send_mail(
            subject=f"Yangi buyurtma #{order.id} — OnlyGirls",
            message=(
                f"{order.full_name} ({request.user.email}) zakaz berdi.\n"
                f"Telefon: {order.phone_number}\n"
                f"Manzil: {order.address or '-'}\n\n"
                f"Mahsulotlar:\n{order_lines}\n\n"
                f"Jami: {order.get_total_cost()} so'm"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ORDER_NOTIFICATION_EMAIL],
            fail_silently=True,
        )

        cart.clear()
        messages.success(request, "Buyurtmangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.")
        return redirect('orders:order_success', order_id=order.id)

    return render(request, 'orders/checkout.html', {'cart': cart})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})
