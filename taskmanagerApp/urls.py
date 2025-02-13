from django.urls import path
from taskmanagerApp.views import index, PositionListView, WorkerListView
from .views import TaskListView

urlpatterns = [
    path("", index, name='index'),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("positions/", PositionListView.as_view(), name="position-list"),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
]
app_name = "taskManagerApp"
