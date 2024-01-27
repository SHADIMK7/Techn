from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Author(models.Model):
    name = models.CharField(max_length=100)
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    

    def __str__(self):
        return self.name
    
class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_date = models.DateField(auto_now_add=True)
    book_code = models.CharField(max_length=100, unique=True, blank=True, null=True)

    
    def __str__(self):
        return self.title
    
