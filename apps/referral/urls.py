# Django Imports
from django.urls import re_path

# Local Imports
from . import views


# isort: off


urlpatterns = [
    re_path(
        # if the referral code is prefixed with an '@', it is an username
        r'^referrals/(?P<referral_code>@?[a-zA-Z0-9_-]+)$',
        views.referral_view,
        name='htk_referral',
    ),
]
