from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("health/", views.health_check, name="health_check"),
    path("api/users/", views.UserListView.as_view(), name="user-list"),
    path("api/meetings/", views.MeetingListView.as_view(), name="meeting-list"),
    path("api/meetings/create/", views.MeetingCreateView.as_view(), name="meeting-create"),
    path(
        "api/meetings/<uuid:meeting_id>/delete/",
        views.MeetingDeleteView.as_view(),
        name="meeting-delete",
    ),
    path("meeting/", views.meeting, name="meeting"),
]
