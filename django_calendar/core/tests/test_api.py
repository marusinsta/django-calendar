from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.models import Calendar, Event
from core.serializers import CalendarSerializer, EventSerializer
from user.models import CustomUser
from user.tests.test_api import create_user, authenticate_client, get_user_token


def create_calendar(name, owner, users):
    calendar = Calendar.objects.create(name=name, owner=owner)
    for user in users:
        calendar.users.add(user)
    calendar.save()
    return calendar


def create_event(name, calendar, description="test description", timestamp="2025-01-01T00:00:00Z"):
    event = Event.objects.create(name=name, calendar=calendar, description=description, timestamp=timestamp)
    return event


class CalendarTestCase(APITestCase):
    def setUp(self):
        self.client1 = APIClient()
        self.client2 = APIClient()
        authenticate_client(self.client1, get_user_token(create_user("test1", "test")))
        self.user1 = CustomUser.objects.get(username="test1")
        authenticate_client(self.client2, get_user_token(create_user("test2", "test")))
        self.user2 = CustomUser.objects.get(username="test2")

    def test_create_calendar_one_user(self):
        new_calendar = {
            "name": "test-calendar"
        }
        expected = {
            "id": 1,
            "name": new_calendar["name"],
            "owner": self.user1.username,
            "users": [self.user1.username]
        }
        response = self.client1.post(reverse("calendars-list"), data=new_calendar, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data, expected)

    def test_create_calendar_different_owner(self):
        new_calendar = {
            "name": "test-calendar",
            "owner": self.user2.username
        }
        response = self.client1.post(reverse("calendars-list"), data=new_calendar, format='json')
        self.assertEquals(response.data["owner"], self.user1.username)

    def test_create_calendar_multiple_users(self):
        new_calendar = {
            "name": "test-calendar",
            "owner": self.user1.username,
            "users": [self.user2.username, self.user1.username]
        }
        response = self.client1.post(reverse("calendars-list"), data=new_calendar, format='json')
        self.assertEquals(sorted(response.data["users"]), sorted([self.user1.username, self.user2.username]))

    def test_get_calendar_list(self):
        calendars1 = []
        for i in range(3):
            calendars1.append(create_calendar("calendar_" + str(i), self.user1, [self.user1]))
        calendars2 = []
        for i in range(4):
            calendars2.append(create_calendar("calendar_" + str(i), self.user2, [self.user2]))
        shared_calendar = create_calendar("calendar", self.user2, [self.user1, self.user2])
        calendars1.append(shared_calendar)
        calendars2.append(shared_calendar)
        response1 = self.client1.get(reverse("calendars-list"))
        response2 = self.client2.get(reverse("calendars-list"))
        self.assertEquals(CalendarSerializer(calendars1, many=True).data, response1.data)
        self.assertEquals(CalendarSerializer(calendars2, many=True).data, response2.data)

    def test_calendar_add_user(self):
        calendar = create_calendar("calendar", self.user1, [self.user1])
        self.assertTrue(self.user2 not in calendar.users.all())
        response = self.client1.post(reverse("add-users", kwargs={"pk": calendar.id}),
                                     {"users": [self.user2.username]}, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user2 in calendar.users.all())

    def test_calendar_delete_user(self):
        calendar = create_calendar("calendar", self.user1, [self.user1, self.user2])
        self.assertTrue(self.user2 in calendar.users.all())
        response = self.client1.post(reverse("remove-users", kwargs={"pk": calendar.id}),
                                     {"users": [self.user2.username]}, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user2 not in calendar.users.all())

    def test_calendar_delete_owner(self):
        calendar = create_calendar("calendar", self.user1, [self.user1, self.user2])
        response = self.client1.post(reverse("remove-users", kwargs={"pk": calendar.id}),
                                     {"users": [self.user1.username]}, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.user1 in calendar.users.all())

    def test_calendar_patch_users(self):
        calendar = create_calendar("calendar", self.user1, [self.user1])
        response = self.client1.patch(reverse('calendars-detail', kwargs={"pk": calendar.id}),
                                      {"users": [self.user2.username]}, format='json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.user2 not in calendar.users.all())

    def test_calendar_change_owner_user_in_users(self):
        calendar = create_calendar("calendar", self.user1, [self.user1, self.user2])
        self.assertEquals(calendar.owner.id, self.user1.id)
        response = self.client1.patch(reverse('calendars-detail', kwargs={"pk": calendar.id}),
                                      {"owner": self.user2.username}, format='json')
        calendar = Calendar.objects.get(id=calendar.id)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(calendar.owner.id, self.user2.id)

    def test_calendar_change_owner_user_not_in_users(self):
        calendar = create_calendar("calendar", self.user1, [self.user1])
        self.assertEquals(calendar.owner.id, self.user1.id)
        response = self.client1.patch(reverse('calendars-detail', kwargs={"pk": calendar.id}),
                                      {"owner": self.user2.username}, format='json')
        calendar = Calendar.objects.get(id=calendar.id)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(calendar.owner.id, self.user1.id)


class EventTestCase(APITestCase):
    def setUp(self):
        self.client1 = APIClient()
        self.client2 = APIClient()
        authenticate_client(self.client1, get_user_token(create_user("test1", "test")))
        self.user1 = CustomUser.objects.get(username="test1")
        authenticate_client(self.client2, get_user_token(create_user("test2", "test")))
        self.user2 = CustomUser.objects.get(username="test2")
        self.calendar = create_calendar("calendar", self.user1, [self.user1])

    def test_create_event_calendar_exists(self):
        new_event = {
            "name": "event",
            "description": "test event",
            "calendar": self.calendar.id,
            "timestamp": "2025-01-01T00:00"
        }
        expected = {
            "id": 1,
            "calendar": self.calendar.id,
            "name": new_event["name"],
            "description": new_event["description"],
            "timestamp": "2025-01-01T00:00:00Z"
        }
        response = self.client1.post(reverse("events-list"), data=new_event, format="json")
        self.assertTrue(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data, expected)

    def test_create_event_calendar_does_not_exist(self):
        new_event = {
            "name": "event",
            "description": "test event",
            "calendar": 10,
            "timestamp": "2025-01-01T00:00"
        }
        response = self.client1.post(reverse("events-list"), data=new_event, format="json")
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(Event.objects.filter(name="event").count(), 0)

    def test_event_list(self):
        calendar1 = create_calendar("calendar1", self.user1, [self.user1])
        calendar2 = create_calendar("calendar2", self.user2, [self.user2])
        calendar_shared = create_calendar("calendar shared", self.user1, [self.user1, self.user2])
        user1_events = []
        user2_events = []
        for i in range(2):
            new_event = create_event("event" + str(i), calendar1)
            user1_events.append(new_event)
        for i in range(3):
            new_event = create_event("event" + str(i), calendar2)
            user2_events.append(new_event)
        shared_event = create_event("event shared", calendar_shared)
        user1_events.append(shared_event)
        user2_events.append(shared_event)
        response1 = self.client1.get(reverse("events-list"))
        response2 = self.client2.get(reverse("events-list"))
        self.assertEquals(response1.data, EventSerializer(user1_events, many=True).data)
        self.assertEquals(response2.data, EventSerializer(user2_events, many=True).data)
