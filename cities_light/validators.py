# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytz
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def timezone_validator(value):
    """Timezone validator."""
    try:
        return pytz.timezone(value)
    except (pytz.UnknownTimeZoneError, AttributeError):
        raise ValidationError(
            _('Timezone validation error: %(value)s'),
            code='timezone_error',
            params={'value': value}
        )
