
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('users/api/',include('users.urls')),

    path('api/',include('products.urls')),
    path('comment/api/',include('comment_rating.urls')),
    path('api/chat/',include('chatgpt.urls')),
    path('api/home/', include('home.urls')),
    path('api/', include('cart.urls')),  # Mn3m
    path('api/orders/', include('orders.urls')),#Mn3m


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

  



