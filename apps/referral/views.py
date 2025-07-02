# Django Imports
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import redirect

# HTK Imports
from htk.utils import htk_setting

# Local Imports
from .utils import get_referrer_from_code


# isort: off


UserModel = get_user_model()


def referral_view(request, referral_code: str, *args, **kwargs):
    referrer = get_referrer_from_code(referral_code)

    if referrer:
        request.session['referrer_id'] = referrer.id
        request.set_cookie('referrer_id', referrer.id)
        response = redirect(htk_setting('HTK_REFERRAL_REDIRECT_URL'))
    else:
        response = Http404

        return response
