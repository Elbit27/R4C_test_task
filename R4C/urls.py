from django.contrib import admin
from django.urls import path
from robots.views import RobotCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots/create/', RobotCreateView.as_view(), name='robot-create'),
]
