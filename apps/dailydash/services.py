from django.utils import timezone

from .models import Day, DayRoutineCheck, RoutineItem


def get_or_create_day(user, date):
    day, _ = Day.objects.get_or_create(user=user, date=date)
    if date >= timezone.localdate():
        for item in RoutineItem.objects.filter(user=user, active=True):
            DayRoutineCheck.objects.get_or_create(day=day, routine_item=item)
    return day
