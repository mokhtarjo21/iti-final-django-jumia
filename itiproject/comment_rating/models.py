from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from products.models import Product

from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.exceptions import ValidationError  

class Comment(models.Model):
    """
    Comments on projects with optional replies
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
   
  
    
    def __str__(self):
        return f"Comment by {self.user.first_name} {self.user.last_name} on {self.product.name}"


class Rating(models.Model):
    """
        project ratings 
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # composite primay key to add one rating to one project
        unique_together = ('user', 'product')

        
@receiver(post_save, sender=Rating)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    average = product.ratings.aggregate(avg_rating=Avg('value'))['avg_rating'] or 0.0
    product.rating_average = round(average, 2)
    product.save()




# Create your models here.
