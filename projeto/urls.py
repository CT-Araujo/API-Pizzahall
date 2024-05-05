
from django.contrib import admin
from django.urls import path
from app.views import ClienteViews, LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ClienteViews.as_view(), name = 'cliente'),
    path('login/', LoginView.as_view(), name = 'login')
]

