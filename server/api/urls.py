from django.urls import path
from . import views

urlpatterns = [
    # path("example", views.example_view, name="example_view"),
    path("test_user", views.test_user_view, name="test_user_view"),
]
