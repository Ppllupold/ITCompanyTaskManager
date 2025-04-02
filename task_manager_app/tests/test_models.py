from django.test import TestCase
from django.contrib.auth import get_user_model
from task_manager_app.models import Position, TaskType, Task, Team, Project
from django.utils import timezone
from datetime import timedelta


class PositionModelTests(TestCase):
    def test_str_representation(self):
        position = Position.objects.create(name="Backend Developer")
        self.assertEqual(str(position), "Backend Developer")


class WorkerModelTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="QA")
        self.worker = get_user_model().objects.create_user(
            username="tester", password="testpass123", position=self.position
        )

    def test_str_representation(self):
        self.assertEqual(str(self.worker), "tester (QA)")

    def test_position_assignment(self):
        self.assertEqual(self.worker.position.name, "QA")


class TaskTypeModelTests(TestCase):
    def test_str_representation(self):
        task_type = TaskType.objects.create(name="Bugfix")
        self.assertEqual(str(task_type), "Bugfix")


class TaskModelTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="DevOps")
        self.worker = get_user_model().objects.create_user(
            username="deployr", password="pass1234", position=self.position
        )
        self.task_type = TaskType.objects.create(name="Deployment")
        self.project = Project.objects.create(
            name="Infra Upgrade",
            description="Upgrading to newer infra",
            deadline=timezone.now() + timedelta(days=10),
            priority="CRITICAL",
        )
        self.task = Task.objects.create(
            name="Setup CI/CD",
            description="Configure pipelines",
            deadline=timezone.now() + timedelta(days=5),
            is_completed=False,
            priority="HIGH_PRIORITY",
            task_type=self.task_type,
            project=self.project,
        )
        self.task.assignees.add(self.worker)

    def test_str_representation(self):
        self.assertEqual(str(self.task), "Setup CI/CD")

    def test_assignee_assignment(self):
        self.assertIn(self.worker, self.task.assignees.all())

    def test_mark_task_completed(self):
        self.task.is_completed = True
        self.task.save()
        self.assertTrue(Task.objects.get(id=self.task.id).is_completed)


class TeamModelTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Manager")
        self.leader = get_user_model().objects.create_user(
            username="boss", password="boss123", position=self.position
        )
        self.member = get_user_model().objects.create_user(
            username="member1", password="memberpass", position=self.position
        )
        self.team = Team.objects.create(name="Alpha Team", leader=self.leader)
        self.team.members.set([self.leader, self.member])

    def test_str_representation(self):
        self.assertEqual(str(self.team), "Alpha Team")

    def test_leader_is_in_members(self):
        self.assertIn(self.team.leader, self.team.members.all())


class ProjectModelTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name="Migration",
            description="Move to PostgreSQL",
            deadline=timezone.now() + timedelta(days=15),
            priority="ESSENTIAL",
        )

    def test_str_representation(self):
        self.assertEqual(str(self.project), "Migration")

    def test_project_defaults(self):
        self.assertFalse(self.project.is_completed)

    def test_created_at_auto_set(self):
        self.assertIsNotNone(self.project.created_at)
