from django.db import models

class Category(models.Model):
    name=models.CharField(max_length=35)
    
class Quiz(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()
    category=models.OneToOneField(Category,on_delete=models.CASCADE)
    quiz_fiel=models.FileField(upload_to='quiz/')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

