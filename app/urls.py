from django.urls import path
from .views import *

app_name = "app"

urlpatterns = [
	path("artworklist/", ArtworksListView.as_view(), name="artworklist"),
]
