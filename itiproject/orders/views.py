from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .serializers import VendorOrderItemSerializer
from django.shortcuts import get_object_or_404
from .paymob import get_paymob_token, create_paymob_order, generate_paymob_payment_key


from products.models import Product
from .models import Order, OrderItem


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("🔍 request.data:", request.data)
        user = request.user
        data = request.data

        shipping_address = data.get("shipping_address")
        payment_method = data.get("payment_method")
        cart_items = data.get("cart_items", [])

        if not shipping_address:
            return Response({"error": "Shipping address is required."}, status=400)

        if not cart_items:
            return Response({"error": "Your cart is empty."}, status=400)

        vendor_map = {}

        # Group items by vendor
        for item in cart_items:
            try:
                product = Product.objects.get(id=item["product"]["id"])
            except Product.DoesNotExist:
                return Response({"error": f"Product with ID {item['product']['id']} not found."}, status=404)

            vendor = product.seller  # this is a User instance with is_staff=True
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
                    total_price = sum(
                        (i["product"].sale_price if i["product"].sale_price else i["product"].price) * i["quantity"]
                        for i in items
                    )

                    order = Order.objects.create(
                        user=user,
                        vendor=vendor,
                        shipping_address=shipping_address,
                        total_price=total_price,
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
                            status="pending"
                        )

                    order_ids.append(order.id)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)

        return Response({"message": "Orders created successfully", "order_ids": order_ids}, status=201)


class VendorOrderItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({"error": "Unauthorized"}, status=403)

        items = OrderItem.objects.filter(vendor=request.user)
        serializer = VendorOrderItemSerializer(items, many=True)
        return Response(serializer.data)

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response({"error": "Unauthorized"}, status=403)

        item = get_object_or_404(OrderItem, pk=pk, vendor=request.user)

        new_status = request.data.get("status")
        if new_status not in ["accepted", "rejected"]:
            return Response({"error": "Invalid status."}, status=400)

        item.status = new_status
        item.save()
        item.order.check_status()  # will mark order as processing if all items accepted
        return Response({"message": f"Order item {item.id} updated to '{new_status}'."})




class PaymobPaymentView(APIView):
    def post(self, request):
        user = request.user
        total_price = request.data.get("total_price", 0)
        amount_cents = int(float(total_price) * 100)

        billing_data = {
            "first_name": user.first_name or "Ahmed",
            "last_name": user.last_name or "Abdelmoniem",
            "email": user.email or "user@example.com",
            "phone_number": user.phone or "01000000000",
            "apartment": "NA",
            "floor": "NA",
            "street": "NA",
            "building": "NA",
            "city": user.city or "Cairo",
            "country": user.countrycode or "EG",
            "state": "NA",
        }

        try:
            token = get_paymob_token()
            order_id = create_paymob_order(token, amount_cents)
            payment_token = generate_paymob_payment_key(token, amount_cents, order_id, billing_data)
            iframe_url = f"https://accept.paymob.com/api/acceptance/iframes/{settings.PAYMOB_IFRAME_ID}?payment_token={payment_token}"

            return Response({"iframe_url": iframe_url})
        except Exception as e:
            return Response({"error": str(e)}, status=500)