from django import forms
from .models import Comment
from taggit.forms import TagField
from taggit_labels.widgets import LabelWidget


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment', 'user', 'post')
        widgets = {
            'post': forms.HiddenInput(),
            'user': forms.HiddenInput(),
        }



class TagsForm(forms.ModelForm):
    tags = TagField(required=False, widget=LabelWidget)
    

class SearchForm(forms.Form):
    query = forms.CharField()