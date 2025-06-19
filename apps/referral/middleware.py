# Django Imports
from django.utils.deprecation import MiddlewareMixin

# HTK Imports
from htk.utils import htk_setting

# Local Imports
from .utils import get_referrer_from_code


# isort: off


class ReferralMiddleware(MiddlewareMixin):
    def __init__(self, *args, **kwargs):
        super(ReferralMiddleware, self).__init__(*args, **kwargs)
        self.referrer = None

    def process_request(self, request):
        key = htk_setting('HTK_REFERRAL_QUERY_PARAM_KEY')
        referral_code = request.GET.get(key)
        if referral_code:
            self.referrer = get_referrer_from_code(referral_code)

    def process_response(self, request, response):
        if self.referrer:
            request.session['referrer_id'] = self.referrer.id
            response.set_cookie('referrer_id', self.referrer.id)
        return response
