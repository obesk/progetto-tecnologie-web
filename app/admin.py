from django.contrib import admin
from .models import Artist, Artwork, Category, Photo, Bid, AppUser


admin.site.register(Artist)
admin.site.register(Artwork)
admin.site.register(Category)
admin.site.register(Photo)
admin.site.register(Bid)
admin.site.register(AppUser)
