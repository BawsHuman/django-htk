# Django Imports
from django.conf import settings
from django.db import models


class ReferralCode(models.Model):
    """Referral Code model"""

    code = models.CharField(max_length=56, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='referral_codes',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        unique_together = ('code',)
