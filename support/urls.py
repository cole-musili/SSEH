from django.urls import path
from . import views

app_name = "support"

urlpatterns = [
    path("contact/", views.contact_admin, name="contact_admin"),
    path("contact/success/", views.contact_success, name="contact_success"),
    path("admin/inbox/", views.admin_inbox, name="admin_inbox"),
    path("admin/inbox/<int:pk>/reply/", views.reply_message, name="reply_message"),
]
