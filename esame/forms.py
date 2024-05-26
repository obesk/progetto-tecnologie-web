from django.contrib.auth.forms import UserCreationForm, User
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

class CreateCustomer(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

class CreateSeller(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit) 
        g = Group.objects.get(name="Seller") 
        g.user_set.add(user) 
        return user 
