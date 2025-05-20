from django.urls import path
from .views import *

urlpatterns = [
    path('my-cart/', UserCartView.as_view(), name='user-cart'),
    path("cart/", UserCartView.as_view(), name="user-cart"),
    path("cart/add/", AddToCartView.as_view(), name="add-to-cart"),
    path("cart/update/<int:item_id>/", UpdateCartItemView.as_view(), name="update-cart-item"),
    path("cart/bulk-add/", BulkAddToCartView.as_view(), name="bulk-add-to-cart"),
    path("cart/remove/<int:item_id>/", RemoveCartItemView.as_view(), name="remove-cart-item"),
    path("cart/clear/", ClearCartView.as_view(), name="clear-cart"),

]

