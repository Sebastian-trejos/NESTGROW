from django.core.exceptions import ValidationError


class ContainsNumberValidator:
    def validate(self, password, user=None):
        if not any(c.isdigit() for c in password):
            raise ValidationError(
                'La contraseña debe contener al menos un número.',
                code='password_no_number',
            )

    def get_help_text(self):
        return 'La contraseña debe contener al menos un número.'
