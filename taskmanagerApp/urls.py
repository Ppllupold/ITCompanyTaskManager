from django.urls import path
from taskmanagerApp.views import index, PositionListView
from .views import TaskListView

urlpatterns = [
    path("", index, name='index'),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("positions/", PositionListView.as_view(), name="position-list"),
]
app_name = "taskManagerApp"
