from django.urls import path

from taskmanagerApp.views import PositionListView, WorkerListView, WorkerDetailView, TaskDetailView, \
    RegisterView, WorkerDeleteView, ProjectListView, ProjectCreateView, ProjectDeleteView, ProjectDetailView, \
    ProjectUpdateView, ProjectTeamsView, TeamUpdateView, TeamCreateView, remove_team_from_project, TaskCreateView, \
    TaskUpdateView, TaskAssignView, TaskDeleteView, IndexView, mark_task_completed, TaskListView, WorkerUpdateView, \
    TeamDeleteView

urlpatterns = [
    path("", IndexView.as_view(), name='index'),
    path("register/", RegisterView.as_view(), name="register"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    path("tasks/<int:pk>/assign/", TaskAssignView.as_view(), name="task-assign"),
    path("tasks/<int:pk>/complete/", mark_task_completed, name="task-complete"),
    path("positions/", PositionListView.as_view(), name="position-list"),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path("workers/<int:pk>/", WorkerDetailView.as_view(), name="worker-detail"),
    path("workers/<int:pk>/update", WorkerUpdateView.as_view(), name="worker-update"),
    path("workers/<int:pk>/delete/", WorkerDeleteView.as_view(), name="worker-delete"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("projects/create/", ProjectCreateView.as_view(), name="project-create"),
    path("projects/<int:pk>/delete/", ProjectDeleteView.as_view(), name="project-delete"),
    path("projects/<int:pk>/update/", ProjectUpdateView.as_view(), name="project-update"),
    path("projects/<int:pk>/teams/", ProjectTeamsView.as_view(), name="project-teams"),
    path("teams/<int:pk>/update/", TeamUpdateView.as_view(), name="team-update"),
    path("teams/<int:pk>/delete/", TeamDeleteView.as_view(), name="team-delete"),
    path("teams/create/", TeamCreateView.as_view(), name="team-create"),
    path("projects/<int:project_id>/teams/<int:team_id>/remove/", remove_team_from_project,
         name="remove-team-from-project"),

]
app_name = "taskManagerApp"
