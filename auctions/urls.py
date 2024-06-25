from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import CreateView
from .views import HomeView, CustomerRegistrationView

#TODO: manage views
urlpatterns = [
	path("admin/", admin.site.urls),
	path("", include("app.urls")),
	path("login/", auth_views.LoginView.as_view(), name="login"),
	path("logout/", auth_views.LogoutView.as_view(), name="logout"),
	path("register/", CustomerRegistrationView.as_view(), name="register"),
]
