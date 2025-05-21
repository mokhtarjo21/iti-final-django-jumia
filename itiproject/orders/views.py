from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .serializers import VendorOrderItemSerializer
from django.shortcuts import get_object_or_404


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