from django.db import models
from users.models import User
class ChatMessage(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    messages = models.TextField()
    

    
# Create your models here.
