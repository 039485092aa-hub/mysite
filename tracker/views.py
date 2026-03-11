from django.shortcuts import render
from .models import WeekPlan, WorkoutLog


def home(request):
    weekplans = WeekPlan.objects.order_by("-week_start_date")[:10]
    logs = WorkoutLog.objects.order_by("-date")[:10]
    return render(request, "tracker/home.html", {"weekplans": weekplans, "logs": logs})