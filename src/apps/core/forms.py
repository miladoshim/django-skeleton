from django.forms import forms

from apps.core.models import NewsletterSubscriber

class NewsletterSubscriberForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        
        
        
# class BodyFieldForm(forms.ModelForm):
#     body = forms.Charfield(widget=forms.Textarea(attrs={'id':'richtext_field'}))
    
#     class Meta:
#         model=Post
#         fields = "__all__"