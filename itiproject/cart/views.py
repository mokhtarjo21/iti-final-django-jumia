from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartItemSerializer
from rest_framework import status
from products.models import Product
from users.models import User
class UserCartView(APIView):
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            print ("Cart does not exist")
            return Response({"cart": [], "message": "Cart is empty."}, status=status.HTTP_200_OK)

        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)
     
        return Response({"cart_id": cart.cart, "items": serializer.data}, status=status.HTTP_200_OK)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        luser = request.user
        user = User.objects.get(id=luser.id)
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)
        colors = request.data.get("colors")
        size = request.data.get("size")

        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
            cart_item.colors = colors
            cart_item.size = size
        cart_item.save()

        return Response({"message": "Product added to cart"}, status=status.HTTP_200_OK)
class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, item_id):
        try:
            user = User.objects.get(id=request.user.id)
            cart_item = CartItem.objects.get(id=item_id, cart__user=user)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_item.quantity = request.data.get("quantity", cart_item.quantity)
        cart_item.colors = request.data.get("colors", cart_item.colors)
        cart_item.size = request.data.get("size", cart_item.size)
        cart_item.save()

        return Response({"message": "Cart item updated"}, status=status.HTTP_200_OK)
class BulkAddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        luser = request.user
        user = User.objects.get(id=luser.id)
        items = request.data.get("items", [])
        if not items:
            return Response({"error": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=user)

        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            colors = item.get("colors")
            size = item.get("size")

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                continue  # skip this item if product not found

            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += int(quantity)
            else:
                cart_item.quantity = int(quantity)
                cart_item.colors = colors
                cart_item.size = size
            cart_item.save()

        return Response({"message": "Products added to cart"}, status=status.HTTP_200_OK)


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            user= User.objects.get(id=request.user.id)
            cart_item = CartItem.objects.get(id=item_id, cart__user=user)
            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            user = User.objects.get(id=request.user.id)
            cart = Cart.objects.get(user=user)
            CartItem.objects.filter(cart=cart).delete()
            return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"message": "Cart already empty"}, status=status.HTTP_200_OK)
