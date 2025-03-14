from django.urls import path
from taskmanagerApp.views import index, PositionListView, WorkerListView, WorkerDetailView, TaskDetailView, \
    RegisterView, WorkerDeleteView, ProjectListView, ProjectCreateView, ProjectDeleteView, ProjectDetailView
from .views import TaskListView

urlpatterns = [
    path("", index, name='index'),
    path("register/", RegisterView.as_view(), name="register"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("positions/", PositionListView.as_view(), name="position-list"),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path("workers/<int:pk>/", WorkerDetailView.as_view(), name="worker-detail"),
    path("workers/<int:pk>/delete/", WorkerDeleteView.as_view(), name="worker-delete"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("projects/create/", ProjectCreateView.as_view(), name="project-create"),
    path("projects/<int:pk>/delete/", ProjectDeleteView.as_view(), name="project-delete"),
]
app_name = "taskManagerApp"
