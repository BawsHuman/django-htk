# Django Imports
from django.conf import settings
from django.db import models


# isort: off


class Referral(models.Model):
    """Referral model"""

    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='referrals',
        on_delete=models.CASCADE,
    )
    referred = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='referred_by',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        unique_together = ('referrer', 'referred')
