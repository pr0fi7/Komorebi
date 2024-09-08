from django import forms
from .models import Challenge

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        exclude = ["id", 'user', 'created_at', 'impact']  # Excluding fields that are auto-managed or unnecessary
