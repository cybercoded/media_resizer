from django.db import models
from django.contrib.auth.models import User


class OriginalImage(models.Model):
    filename = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate with User

class ResizedImage(models.Model):
    original = models.ForeignKey(OriginalImage, on_delete=models.CASCADE, related_name='resized_images')
    filename = models.CharField(max_length=255)
    device = models.CharField(max_length=10)

class Settings(models.Model):
    device = models.CharField(max_length=50, unique=True)  # e.g., 'mobile', 'tablet', 'desktop'
    width = models.IntegerField()  # e.g., 320 for mobile
    height = models.IntegerField()  # e.g., 480 for mobile

    def __str__(self):
        return f"{self.device} ({self.width}x{self.height})"

