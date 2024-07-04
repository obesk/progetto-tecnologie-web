from django.shortcuts import render
from django.views import View
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from .forms import CreateAppUser


class HomeView(View):
	template_name = 'home.html'
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name)

class CustomerRegistrationView(SuccessMessageMixin, CreateView):
	template_name = "register.html"
	success_url = reverse_lazy('login')
	form_class = CreateAppUser
	success_message = "User created successfully"

