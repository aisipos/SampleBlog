from django.forms import ModelForm, Form
from blog.models import User




class LoginForm(Form):
    """
    Form for login
    """
    username = forms.CharField()
    password = forms.CharField()
