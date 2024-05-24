from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import CreateView

#TODO: manage views
urlpatterns = [
	path("admin/", admin.site.urls),
	path("auctions/", include("app.urls")),
	path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", CreateView.as_view(), name="register"),
]
