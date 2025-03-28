from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _

from rest_framework import status

class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('Occur an unexpected error. please contact support.')
    default_code = 'service_unavailable'