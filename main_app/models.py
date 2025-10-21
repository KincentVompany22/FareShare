from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.


CURRENCIES = [
    ('USD', '$ USD 🇺🇸'),
    ('EUR', '€ EUR 🇪🇺'),
    ('GBP', '£ GBP 🇬🇧'),
]

FARE_TYPES = [
    ("activities", "Activities 🏖️"),
    ("entertainment", "Entertainment 🎟️"),
    ("food_drink", "Food & Drink 🍽️"),
    ("housing", "Housing 🏨"),
    ("shopping", "Shopping 🛍️"),
    ("transportation", "Transportation 🚗"),
    ("misc", "Miscellaneous 💡"),
]




class Share(models.Model):
    title = models.CharField(max_length=100)
    currency = models.CharField(max_length=100, choices=CURRENCIES, default=CURRENCIES[0][0])
    created_at = models.DateTimeField(auto_now_add=True) # adding timestamp when created
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shares_created") # since both creator and participants refer to User model, need to establish
    participants = models.ManyToManyField(User, related_name="shares_participating", blank=True) # unique related names to be able to refer to each separately 

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("share-detail", kwargs={"pk": self.pk})

    
class Fare(models.Model):
    share = models.ForeignKey(Share, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField('Paid Date')
    category = models.CharField(max_length=100, choices=FARE_TYPES, default=FARE_TYPES[0][0])
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fares_paid")
    split_between = models.ManyToManyField(User, related_name="fares_split")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("share-detail", kwargs={"pk": self.share.pk})

    class Meta:
        ordering = ['-date']


