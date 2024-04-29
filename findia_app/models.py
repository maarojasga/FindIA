from django.db import models
from django.contrib.auth.models import User


class Movement(models.Model):
    INCOME_TYPE = 'I'
    COST_TYPE = 'C'
    TYPES = (
        (INCOME_TYPE, 'Income'),
        (COST_TYPE, 'Cost'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TYPES)
    value = models.DecimalField(max_digits=50, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.description} - {self.value}"


class ChatBot(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="GeminiUser", null=True
    )
    text_input = models.CharField(max_length=500)
    gemini_output = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.text_input
