from django import forms


class PayoutRequestForm(forms.Form):
    amount = forms.CharField(
        min_length=0,
        label="مبلغ قابل تسویه",
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "مبلغ قابل تسویه",
                "class": "form-control",
            },
        ),
    )
