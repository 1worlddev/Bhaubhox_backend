from django.db import models
from django.contrib.auth.models import User
from core.storage_backends import R2Storage
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True,  null=True)
    city = models.CharField(max_length=100, blank=True,  null=True)
    state = models.CharField(max_length=50, blank=True,  null=True)
    zip = models.CharField(max_length=20, blank=True,  null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} Profile"


class Dog(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dog')
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('boy', 'Boy'), ('girl', 'Girl')])
    size = models.CharField(max_length=10, choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')])
    
    # Change breeds to be a list (JSONField)
    breeds = models.JSONField(default=list, blank=True)
    
    adoptionDate = models.CharField(max_length=15, blank=True)
    allergies = models.JSONField(default=list, blank=True)
    image = models.ImageField(storage=R2Storage(), upload_to='dogs/', null=True, blank=True)

    @property
    def image_public_url(self):
        if self.image:
            return f"https://pub-73f82101c9e54e9b960f80a91111f8c6.r2.dev/{self.image.name}"
        return None

    def __str__(self):
        return f"{self.name} ({self.owner.email})"


from django.db import models
from django.utils import timezone

from django.db import models
from django.utils import timezone
from core.storage_backends import R2Storage

class MonthlyBox(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(storage=R2Storage(), upload_to='boxes/', blank=True, null=True)

    # You want to manually control these:
    month = models.IntegerField()  # e.g., 6 for June
    year = models.IntegerField()   # e.g., 2025
    day = models.IntegerField(default=1)  # default to 1st of the month if not specified

    rating = models.FloatField(default=0.0)
    total_ratings = models.IntegerField(default=0)
    rating_sum = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.day}/{self.month}/{self.year})"

    @property
    def image_public_url(self):
        if self.image:
            return f"https://pub-73f82101c9e54e9b960f80a91111f8c6.r2.dev/{self.image.name}"
        return None

    def update_rating(self, new_rating):
        self.total_ratings += 1
        self.rating_sum += new_rating
        self.rating = round(self.rating_sum / self.total_ratings, 1)
        self.save()



from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    PLAN_CHOICES = [
        ('3mo', '3 Month'),
        ('6mo', '6 Month'),
        ('monthly', 'Monthly'),
    ]

    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('paused', 'Paused'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    billing_type = models.CharField(max_length=20)
    selected_plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    total_treats_delivered = models.IntegerField(default=0)
    total_toys_delivered = models.IntegerField(default=0)
    skipped_months = models.IntegerField(default=0)  # Track how many months skipped
    
    def mark_as_delivered(self):
        if self.status != 'delivered':
            self.status = 'delivered'
            self.total_treats_delivered += 2  # default per box
            self.total_toys_delivered += 3
            self.save()

    # shipping info
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip = models.CharField(max_length=20)
    rating = models.IntegerField(default=0, null=True, blank=True) 
    monthly_box = models.ForeignKey(MonthlyBox, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    use_shipping_as_billing = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')

    # payment dummy (Cash on Delivery for now)
    payment_method = models.CharField(max_length=50, default='Cash on Delivery')
    is_paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email} [{self.status}]"






 
 