# Django Imports
from django.core.exceptions import AppRegistryNotReady

# HTK Imports
from htk.utils import (
    htk_setting,
    resolve_model_dynamically,
)


try:
    Referral = resolve_model_dynamically(htk_setting('HTK_REFERRAL_MODEL'))
    ReferralCode = resolve_model_dynamically(
        htk_setting('HTK_REFERRAL_CODE_MODEL')
    )
except (LookupError, AppRegistryNotReady):
    pass
