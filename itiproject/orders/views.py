from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from cart.models import CartItem
from products.models import Product
from users.models import Vendor
from .models import Order, OrderItem


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        shipping_address = data.get("shipping_address")
        payment_method = data.get("payment_method")
        cart_items = data.get("cart_items", [])

        if not cart_items:
            return Response({"error": "Your cart is empty."}, status=400)

        vendor_map = {}

        for item in cart_items:
            try:
                product = Product.objects.get(id=item["product"]["id"])
            except Product.DoesNotExist:
                return Response({"error": f"Product with ID {item['product']['id']} not found."}, status=404)

            vendor = product.seller
            if vendor not in vendor_map:
                vendor_map[vendor] = []

            vendor_map[vendor].append({
                "product": product,
                "quantity": item["quantity"],
                "color": item.get("color"),
                "size": item.get("size"),
            })

        order_ids = []

        try:
            with transaction.atomic():
                for vendor, items in vendor_map.items():
                    total = sum(i["product"].sale_price * i["quantity"] for i in items)

                    order = Order.objects.create(
                        user=user,
                        vendor=vendor,
                        shipping_address=shipping_address,
                        total_price=total,
                        payment_method=payment_method,
                        payment_completed=(payment_method != 'cod'),
                        status="pending"
                    )

                    for i in items:
                        OrderItem.objects.create(
                            order=order,
                            product=i["product"],
                            quantity=i["quantity"],
                            vendor=vendor,
                        )

                    order_ids.append(order.id)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response({"message": "Orders created successfully", "order_ids": order_ids})