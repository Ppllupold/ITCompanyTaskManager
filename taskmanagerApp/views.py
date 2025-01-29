from django.shortcuts import render
from django.views import generic

from taskmanagerApp.models import Task


def index(request):
    return render(request, "home/index.html")


class TaskListView(generic.ListView):
    model = Task
    template_name = "TMapp/task-list.html"

    def get_queryset(self):
        task_list = Task.objects.filter(is_completed=False).select_related("task_type")
        return task_list
