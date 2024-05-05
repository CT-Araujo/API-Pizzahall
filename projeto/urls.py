
from django.contrib import admin
from django.urls import path
from app.views import ClienteViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ClienteViews.as_view(), name = 'cliente'),
]

