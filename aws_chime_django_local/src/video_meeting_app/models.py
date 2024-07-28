# Create your models here.
import uuid

from django.db import models


class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Meeting(models.Model):
    meeting_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    attendees = models.ManyToManyField(
        User, through="Attendance", related_name="meetings"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_meetings"
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="updated_meetings"
    )
    response = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        editable=False,
        help_text="Response from Chime API",
    )


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    response = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        editable=False,
        help_text="Response from Chime API",
    )

    def __str__(self):
        return f"{self.user.name} - {self.meeting.title}"
