from django.http import Http404
from django.conf import settings

from rest_framework.exceptions import ErrorDetail
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import exception_handler


def combine_multiple(exceptions):
    message = ""
    for key, val in exceptions.items():
        if key == 'non_field_errors':
            key = ''

        if message:
            message += ", '{0}': {1}".format(key, ''.join(val)) if key else ", '{}".format(''.join(val))
        else:
            message += "'{0}': {1}".format(key, ''.join(val)) if key else ", '{}".format(''.join(val))
    return message


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response:
        response.data = {'code': getattr(settings, 'ERROR_CODE', '0000')}
        if isinstance(exc, Http404):
            response.data['message'] = str(exc)
        elif isinstance(exc.detail, ErrorDetail):
            response.data['message'] = exc.detail
        elif isinstance(exc.detail, ReturnDict):
            response.data['message'] = combine_multiple(exc.detail)
    return response
