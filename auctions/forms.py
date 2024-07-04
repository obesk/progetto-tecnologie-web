from django.contrib.auth.forms import UserCreationForm, User
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

# TODO: mettere is_seller
class CreateAppUser(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')