
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('users/api/',include('users.urls')),
<<<<<<< HEAD
    path('api/', include('cart.urls')),

=======

    path('api/',include('products.urls')),
    path('comment/api/',include('comment_rating.urls')),

    path('api/home/', include('home.urls')),
>>>>>>> 4c5ec7797cd86a188f6b81d34abc6ebd347e638b
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

  



