from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from task_manager_app.models import Task, Project, Team, Position, TaskType
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class IndexViewTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.user = User.objects.create_user(
            username="testuser", password="pass", position=self.position
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("taskmanager:index"))
        self.assertNotEqual(response.status_code, 200)

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.get(reverse("taskmanager:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/index.html")


class ProjectListViewTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Manager")
        self.user = User.objects.create_user(
            username="user", password="pass", position=self.position
        )

    def test_login_required(self):
        response = self.client.get(reverse("taskManagerApp:project-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_view_with_login(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse("taskManagerApp:project-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "TMapp/project-list.html")


class TaskListViewTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Analyst")
        self.user = User.objects.create_user(
            username="testuser", password="pass", position=self.position
        )
        self.task_type = TaskType.objects.create(name="Bug")
        self.project = Project.objects.create(
            name="Test Project",
            description="A test project",
            deadline=timezone.now() + timedelta(days=2),
            priority="HIGH_PRIORITY",
        )
        self.task = Task.objects.create(
            name="Test Task",
            description="Testing",
            deadline=timezone.now() + timedelta(days=1),
            priority="HIGH_PRIORITY",
            task_type=self.task_type,
            project=self.project,
        )
        self.task.assignees.add(self.user)

    def test_task_list_requires_login(self):
        response = self.client.get(reverse("taskmanager:task-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_task_list_view(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.get(reverse("taskmanager:task-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "TMapp/task-list.html")


class TaskCreateViewTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.user = User.objects.create_user(
            username="creator", password="pass", position=self.position
        )
        self.team = Team.objects.create(name="Team Alpha", leader=self.user)
        self.team.members.add(self.user)
        self.project = Project.objects.create(
            name="My Project",
            description="Desc",
            deadline=timezone.now() + timedelta(days=3),
            priority="CRITICAL",
        )
        self.project.teams.add(self.team)
        self.task_type = TaskType.objects.create(name="Feature")

    def test_get_create_view(self):
        self.client.login(username="creator", password="pass")
        url = reverse("taskmanager:task-create")
        response = self.client.get(
            url + f"?project_id={self.project.id}&team_id={self.team.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "TMapp/task_form.html")


class WorkerListViewTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="QA")
        self.user = User.objects.create_user(
            username="worker", password="pass", position=self.position
        )

    def test_requires_login(self):
        response = self.client.get(reverse("taskmanager:worker-list"))
        self.assertNotEqual(response.status_code, 200)

    def test_logged_in_worker_list(self):
        self.client.login(username="worker", password="pass")
        response = self.client.get(reverse("taskmanager:worker-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "TMapp/worker-list.html")
