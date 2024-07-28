import json
import uuid

import boto3
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import Attendance, Meeting, User


def health_check(request):
    return JsonResponse({"status": "success"})


def index(request):
    return render(request, "index.html")

def meeting(request):
    meeting_id = request.GET.get('meetingId')
    user_id = request.GET.get('userId')

    meeting = Meeting.objects.get(meeting_id=meeting_id)
    attendee = Attendance.objects.get(meeting=meeting, user__user_id=user_id)

    return render(request, "meeting.html", {
        'meeting': json.dumps(meeting.response),
        'attendee': json.dumps(attendee.response),
    })


@method_decorator(csrf_exempt, name="dispatch")
class UserListView(View):
    def get(self, request):
        users = list(User.objects.values())
        return JsonResponse(users, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class MeetingListView(View):
    def get(self, request):
        meetings = Meeting.objects.annotate(
            created_by_name=F("created_by__name"),
        )
        meetings_list = []
        for meeting in meetings:
            attendees_list = []
            for attendee in Attendance.objects.filter(meeting=meeting):
                attendee_dict = {
                    "user_id": str(attendee.user.user_id),
                    "name": attendee.user.name,
                }
                attendees_list.append(attendee_dict)
            meeting_dict = {
                "meeting_id": str(meeting.meeting_id),
                "title": meeting.title,
                "created_by_id": meeting.created_by_id,
                "created_by_name": meeting.created_by_name,
                "created_at": meeting.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_by_id": meeting.updated_by_id,
                "attendees": attendees_list,
            }
            meetings_list.append(meeting_dict)
        return JsonResponse(meetings_list, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class MeetingCreateView(View):
    def post(self, request):
        meeting_data = json.loads(request.body)
        created_by_id = meeting_data.get("created_by")
        if not created_by_id or created_by_id == "undefined":
            return JsonResponse(
                {"status": "error", "message": "Invalid user_id"}, status=400
            )
        try:
            created_by = User.objects.get(user_id=created_by_id)
        except User.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "User does not exist"}, status=400
            )
        attendees_ids = meeting_data.get("participants")
        if not attendees_ids or "undefined" in attendees_ids:
            return JsonResponse(
                {"status": "error", "message": "Invalid attendees_ids"}, status=400
            )
        try:
            attendees = User.objects.filter(user_id__in=attendees_ids)
        except User.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Attendee does not exist"}, status=400
            )
        client = boto3.client("chime-sdk-meetings")
        meeting_id = str(uuid.uuid4())
        response = client.create_meeting(
            ClientRequestToken=str(uuid.uuid4()),
            MediaRegion="ap-northeast-1",
            MeetingHostId=meeting_id,
            ExternalMeetingId=meeting_id,
        )
        meeting_data_model = {
            "title": meeting_data.get("title"),
            "meeting_id": meeting_id,
            "created_by": created_by,
            "updated_by": created_by,
            "response": response,
        }
        meeting = Meeting.objects.create(**meeting_data_model)
        for attendee in attendees:
            attendee_response = client.create_attendee(
                MeetingId=response["Meeting"]["MeetingId"],
                ExternalUserId=str(attendee.user_id),
            )
            Attendance.objects.create(
                user=attendee,
                meeting=meeting,
                response=attendee_response,
            )
        return JsonResponse(
            {"status": "success", "meeting_id": str(meeting.meeting_id)}
        )


@method_decorator(csrf_exempt, name="dispatch")
class MeetingDeleteView(View):
    def delete(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, meeting_id=meeting_id)
        client = boto3.client("chime-sdk-meetings")
        client.delete_meeting(MeetingId=str(meeting.meeting_id))
        Attendance.objects.filter(meeting=meeting).delete()
        meeting.delete()
        return JsonResponse({"status": "success"})
