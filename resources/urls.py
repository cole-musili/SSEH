from django.urls import path
from . import views

app_name = "resources"

urlpatterns = [
    path("", views.resource_list, name="resource_list"),
    path("upload/", views.upload_resource, name="upload_resource"),
    path("<int:pk>/download/", views.download_resource, name="download_resource"),
    path("<int:pk>/delete/", views.delete_resource, name="delete_resource"),
]
