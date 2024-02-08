import re

from django.core.exceptions import ValidationError


def validate_hex_color(value):
    hex_color = re.search(r'^#[A-Fa-f0-9]{6}$|^#[A-Fa-f0-9]{3}$', value)
    if not hex_color:
        raise ValidationError(
            'Цвет в формате HEX содержит цифры и латиские буквы A-F и a-f'
        )
