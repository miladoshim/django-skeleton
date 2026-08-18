from django import forms
from taggit.forms import TagField
from taggit_labels.widgets import LabelWidget


class CommentCreateForm(forms.Form):
    comment = forms.CharField(
        label="دیدگاه شما",
        max_length=1000,
        min_length=4,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "دیدگاه خود را بنویسید...",
            }
        ),
    )

    def clean_comment(self):
        comment = self.cleaned_data["comment"].strip()

        spam_keywords = [
            "http://",
            "https://",
            "www.",
        ]

        if any(keyword in comment for keyword in spam_keywords):
            raise forms.ValidationError(_("لینک در دیدگاه مجاز نیست"))

        return comment


class CommentReplyCreateForm(forms.Form):
    reply = forms.CharField(
        label="متن پاسخ",
        max_length=1000,
        min_length=4,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "متن پاسخ خود را بنویسید...",
            }
        ),
    )

    pid = forms.HiddenInput()


class TagsForm(forms.ModelForm):
    tags = TagField(required=False, widget=LabelWidget)
