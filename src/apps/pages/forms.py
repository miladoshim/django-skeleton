from django import forms
from .models import ContactUs


class ContactForm(forms.ModelForm):
    mobile = forms.CharField(
        min_length=11,
        max_length=11,
        label="شماره موبایل",
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "مثال:‌09121236515",
                "class": "form-control",
            },
        ),
    )

    class Meta:
        model = ContactUs
        fields = (
            "subject",
            "fullname",
            "mobile",
            "message",
        )
