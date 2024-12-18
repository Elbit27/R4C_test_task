from django.urls import path
from robots.views import RobotCreateView
from robots.utils import download_production_summary

urlpatterns = [
    path('create/', RobotCreateView.as_view(), name='robot-create'),
    path('download-production-summary/', download_production_summary, name='download_production_summary'),
]
