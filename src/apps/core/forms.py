from django import forms

from apps.core.models import NewsletterSubscriber


class NewsletterSubscriberForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]


class ContactForm(form.Form):
    name = forms.CharField(
        min_length=3,
        max_length=128,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control"},
        ),
    )
    phone = forms.CharField(max_length=11, required=True)
    message = forms.CharField(
        1024,
        required=True,
        widget=forms.Textarea(
            attrs={},
        ),
    )


# class BodyFieldForm(forms.ModelForm):
#     body = forms.Charfield(widget=forms.Textarea(attrs={'id':'richtext_field'}))

#     class Meta:
#         model=Post
#         fields = "__all__"
