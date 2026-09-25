from django.db import models


class Customer(models.Model):
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.email
