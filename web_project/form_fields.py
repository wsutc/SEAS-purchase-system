from django import forms


class PercentageField(forms.DecimalField):
    widget = forms.TextInput

    def to_python(self, value):
        val = super().to_python(value)
        if is_number(val):
            return val / 100
        return val

    def prepare_value(self, value):
        val = super().prepare_value(value)
        if is_number(val) and not isinstance(val, str):
            return str(float(val) * 100)
        return val


def is_number(s):
    if s is None:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False
