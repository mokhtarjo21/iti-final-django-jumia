from rest_framework import viewsets, permissions
from .models import CartItem
from .serializers import CartItemSerializer

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        print("🔍 User:", self.request.user)
        cart_items = CartItem.objects.filter(user=self.request.user)
        print("🛒 Cart Items:", cart_items)
        return cart_items

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
