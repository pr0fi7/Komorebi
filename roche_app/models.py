from django.db import models
from django.contrib.auth.models import User
import uuid

class Challenge(models.Model):
    challenge_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)  # Changed to CharField for shorter text
    why = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)  # Changed to CharField
    duration = models.TextField(null=True, blank=True)  # Changed to DurationField
    participants = models.ManyToManyField(User, related_name='challenges_joined', blank=True)
    reward = models.CharField(max_length=255, null=True, blank=True)  # Changed to CharField
    tracking_method = models.CharField(max_length=255, null=True, blank=True)  # Changed to CharField
    impact = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}: {self.title}'

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)     
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    co2_saved = models.FloatField(default=0.0)  # Storing CO2 savings, default is 0
    challenges_completed = models.IntegerField(default=0)  # Number of challenges completed
    challenges_created = models.IntegerField(default=0)  # Number of challenges created
    idea_created = models.IntegerField(default=0)  # Number of ideas created
    challenges_joined = models.IntegerField(default=0)  # Number of challenges joined
    wallet_points = models.IntegerField(default=0)  # Points in user's wallet

    def __str__(self):
        return f'{self.name} {self.surname} - {self.department} ({self.position})'

class Idea(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    co2_saved = models.FloatField(default=0.0)  # Storing CO2 savings, default is 0

    def __str__(self):
        return f'{self.title} - {self.user.username}'