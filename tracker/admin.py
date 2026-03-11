from django.contrib import admin
from .models import WeekPlan, PlanDay, WorkoutLog


class PlanDayInline(admin.TabularInline):
    model = PlanDay
    extra = 0
    max_num = 7


@admin.register(WeekPlan)
class WeekPlanAdmin(admin.ModelAdmin):
    list_display = ("week_start_date", "title")
    search_fields = ("title",)
    date_hierarchy = "week_start_date"
    inlines = [PlanDayInline]


@admin.register(PlanDay)
class PlanDayAdmin(admin.ModelAdmin):
    list_display = ("week_plan", "weekday", "planned_workout")
    list_filter = ("weekday", "planned_workout")
    search_fields = ("week_plan__title",)


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ("date", "workout", "completed", "planned_day")
    list_filter = ("workout", "completed")
    search_fields = ("notes",)
    date_hierarchy = "date"