from django import forms

# class NewsletterSubscriberForm(forms.ModelForm):
#     email = forms.EmailField(
#         widget=forms.EmailInput(
#             attrs={
#                 "class": "form-control",
#             },
#         ),
#     )

#     class Meta:
#         model = NewsletterSubscriber
#         fields = ["email"]


class ContactForm(forms.Form):
    name = forms.CharField(
        min_length=3,
        max_length=128,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control"},
        ),
    )
    phone = forms.CharField(
        max_length=11,
        required=True,
        error_messages={"required": "شماره موبایل الزامی می باشد."},
    )
    message = forms.CharField(
        max_length=1024,
        required=True,
        widget=forms.Textarea(
            attrs={"class": "form-control"},
        ),
    )


class CommentCreateForm(forms.Form):
    comment = forms.CharField(
        min_length=4,
        max_length=1024,
        required=True,
        label="متن نظر",
        widget=forms.Textarea(
            attrs={"class": "form-control"},
        ),
    )


class CommentReplyCreateForm(forms.Form):
    reply = forms.CharField(
        min_length=4,
        max_length=1024,
        required=True,
        label="متن پاسخ",
        widget=forms.Textarea(
            attrs={"class": "form-control"},
        ),
    )
    pid = forms.HiddenInput()
