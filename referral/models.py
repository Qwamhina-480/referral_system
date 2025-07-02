from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    contact = models.CharField(max_length=50) # Temporarliy removed , unique=True
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    referral_code = models.CharField(max_length=10, unique=True)
    referrer = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username()
    

    # or use settings.SITE_URL in production
    def get_referral_link(self):
        return f"http://localhost:8000/api/signup?ref={self.referral_code}"


    def __str__(self):
        return f"{self.username} → {self.email}"
    

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = get_random_string(6).upper()
        super().save(*args, **kwargs)

    def referral_count(self):
        return self.referrals.count()

    def total_points(self):
        return self.rewards.aggregate(total=models.Sum('points'))['total'] or 0
    
class Reward(models.Model):
    user = models.ForeignKey(User, related_name='rewards', on_delete=models.CASCADE)
    points = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    