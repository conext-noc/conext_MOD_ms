from django.urls import path
from .views import MOD, MODDashboard

urlpatterns = [
    path("", MOD.as_view()),
    path("mod-dashboard", MODDashboard.as_view()),
]
