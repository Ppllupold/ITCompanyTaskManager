from django.db.models import Count
from django.db.models.functions import Lower
from django.shortcuts import render
from django.views import generic

from taskmanagerApp.models import Task, Position


def index(request):
    return render(request, "home/index.html")


class TaskListView(generic.ListView):
    model = Task
    template_name = "TMapp/task-list.html"

    def get_queryset(self):
        queryset = Task.objects.filter(is_completed=False).select_related("task_type")
        sort_param = self.request.GET.get("sort", "priority")

        if sort_param == "task_type":
            return queryset.order_by("task_type__name")
        return queryset.order_by("priority")


class PositionListView(generic.ListView):
    model = Position
    template_name = "TMapp/position-list.html"

    def get_queryset(self):
        queryset = Position.objects.annotate(worker_count=Count("workers"))

        sort_param = self.request.GET.get("sort", "name")
        if sort_param == "worker_count":
            return queryset.order_by(sort_param)
        return queryset.order_by(Lower("name"))
