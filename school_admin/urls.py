from django.urls import path
from . import views

app_name = "school_admin"

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('create-grade/', views.create_grade, name='create_grade'),
    path('create-stream/', views.create_stream, name='create_stream'),
    path('assign-teacher/', views.assign_teacher, name='assign_teacher'),

    path("teachers/", views.teacher_records, name="teacher_records"),
    path("teachers/create/", views.create_teacher, name="create_teacher"),

    path("teacher-records/", views.teacher_record_list, name="teacher_record_list"),
    path("teacher-records/create/", views.create_teacher_record, name="create_teacher_record"),
    path("teachers/<int:pk>/", views.teacher_detail, name="teacher_detail"),


    # 👇 New Timetable routes
   path("timetable/",         views.timetable_list,   name="timetable_list"),
   path("timetable/create/",  views.timetable_create, name="timetable_create"),
   path("timetable/<int:pk>/edit/", views.timetable_edit, name="timetable_edit"),
   path("timetable/stream/<int:stream_id>/", views.timetable_stream_view, name="timetable_stream_view"),



   path("academic-years/", views.academic_year_list, name="academic_year_list"),
   path("academic-years/new/", views.academic_year_create, name="academic_year_create"),
   path("terms/", views.term_list, name="term_list"),
   path("terms/new/", views.term_create, name="term_create"),
   path("profile/", views.profile_settings, name="profile_settings"),

   path('manage-users/', views.manage_user_status, name='manage_user_status'), 



]
