# Django Imports
from django.contrib.auth import get_user_model

# HTK Imports
from htk.utils import htk_setting

# Local Imports
from .resolvers import ReferralCode


# isort: off


UserModel = get_user_model()


def get_referrer_from_code(referral_code):
    referrer = None
    if htk_setting('HTK_REFERRAL_ALLOW_USERNAME') and referral_code.startswith(
        '@'
    ):
        # referral code is an username
        username = referral_code[1:]
        try:
            referrer = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            pass
    elif htk_setting('HTK_REFERRAL_ALLOW_HASH_CODE'):
        try:
            referral_code = ReferralCode.objects.get(code=referral_code)
            referrer = referral_code.user
        except ReferralCode.DoesNotExist:
            pass
    else:
        raise ValueError(
            'Either usernames or hash codes must be allowed in referral codes.'
        )
    return referrer


def get_referrer(request):
    referrer = None
    key = 'referrer_id'
    referrer_id = request.COOKIE.get(key) or request.session.get(key)

    if referrer_id:
        try:
            referrer = UserModel.objects.get(id=referrer_id)
        except UserModel.DoesNotExist:
            pass
    return referrer
