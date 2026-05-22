from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('accounts/', include('accounts.urls')),
    path('categories/', include('categories.urls')),
    path('elonlar/', include('listings.urls')),
]
