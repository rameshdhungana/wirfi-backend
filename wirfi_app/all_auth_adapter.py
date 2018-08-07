from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter


# Overwrites email confirmation url so that the correct url is sent in the email.
# to change the actual address, see core.urls name: 'account_confirm_email'
class MyAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        url = "/account_confirm_email/{}/".format(emailconfirmation.key)
        return settings.FRONTEND_HOST + url
