from django.db import models
from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    email = models.EmailField(unique=True) 
    password = models.CharField(max_length=256)
    facebook_acount = models.CharField(max_length=50, null=True,blank=True)
    Birthdate = models.DateTimeField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True,blank=True)
    active_email = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='users/', null=True, blank=True, default='default.jpg')

    is_vendor = models.BooleanField(default=False)  #added for order (Status)


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    def __str__(self):
        return self.first_name
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        
            
        super().save(*args, **kwargs)

class User_active(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.CharField(max_length=50)
    time_send = models.DateTimeField(auto_now_add=True)
    
# Create your models here.``