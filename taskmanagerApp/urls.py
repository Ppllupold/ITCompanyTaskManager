from django.urls import path
from taskmanagerApp.views import index
from .views import TaskListView
urlpatterns = [
    path("", index, name='index'),
    path("tasks/", TaskListView.as_view(), name="task-list"),
]
app_name = "taskManager"