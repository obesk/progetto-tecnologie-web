from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = "app"

urlpatterns = [
    path("seller/<int:seller_id>/", SellerProfile.as_view(), name="seller_profile"),
    path("customerprofile/", CustomerProfile.as_view(), name="customer_profile"),
    path("manageartworks/", SellerArtworkManagement.as_view(), name="manage_artworks"),
    path("artwork/<pk>", ArtworkDetailView.as_view(), name="artworkdetail"),
    path("create_artwork/", ArtworkCreateView.as_view(), name="create_artwork"),
    path("placebid/", placeBid, name="placebid"),
    path(
        "artworkmanage/<int:pk>/", SellerArtworkManage.as_view(), name="artwork_manage"
    ),
    path("", HomePageView.as_view(), name="homepage"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
