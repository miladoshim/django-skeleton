from django import forms
from .models import Comment


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment', 'user', 'post')
        widgets = {
            'post': forms.HiddenInput(),
            'user': forms.HiddenInput(),
        }
