from datetime import timedelta
from django.utils import timezone
from django.forms import CharField, ChoiceField
from django.test import TestCase

from task_manager_app.forms import WorkerSearchForm, TaskSearchForm, TaskAssignForm, CustomUserCreationForm, ProjectForm, \
    TeamForm
from task_manager_app.models import Position, Task, Team, Project, TaskType, Worker


class WorkerSearchFormTest(TestCase):

    def test_form_valid_with_correct_data(self):
        form_data = {
            "search_field": "username",
            "search_value": "john"
        }
        form = WorkerSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["search_field"], "username")
        self.assertEqual(form.cleaned_data["search_value"], "john")

    def test_form_valid_with_blank_data(self):
        form = WorkerSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_wrong_search_field(self):
        form_data = {
            "search_field": "nonexistent",
            "search_value": "test"
        }
        form = WorkerSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("search_field", form.errors)

    def test_field_types(self):
        form = WorkerSearchForm()
        self.assertIn("search_field", form.fields)
        self.assertIn("search_value", form.fields)
        self.assertEqual(form.fields["search_field"].__class__.__name__, "ChoiceField")
        self.assertEqual(form.fields["search_value"].__class__.__name__, "CharField")


class TestTaskSearchForm(TestCase):

    def setUp(self):
        self.valid_priorities = [choice[0] for choice in Task._meta.get_field('priority').choices]

    def test_form_valid_with_correct_data(self):
        form_data = {
            "name": "Deploy",
            "project_name": "Website Redesign",
            "task_type": "Testing",
            "priority": self.valid_priorities[0],
        }
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["priority"], self.valid_priorities[0])

    def test_form_valid_with_blank_data(self):
        form = TaskSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_priority(self):
        form_data = {
            "priority": "INVALID_PRIORITY"
        }
        form = TaskSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("priority", form.errors)

    def test_field_types(self):
        form = TaskSearchForm()
        self.assertIsInstance(form.fields["name"], CharField)
        self.assertIsInstance(form.fields["project_name"], CharField)
        self.assertIsInstance(form.fields["task_type"], CharField)
        self.assertIsInstance(form.fields["priority"], ChoiceField)

    def test_priority_choices_include_blank(self):
        form = TaskSearchForm()
        choices = form.fields["priority"].choices
        self.assertIn(('', 'All priorities'), choices)
        for val in self.valid_priorities:
            self.assertIn((val, dict(Task._meta.get_field('priority').choices)[val]), choices)

    def test_form_accepts_various_combinations(self):
        test_cases = [
            {"name": "Task A"},
            {"project_name": "Alpha"},
            {"task_type": "Bug"},
            {"priority": "CRITICAL"},
            {"name": "T", "project_name": "P"},
            {"priority": ""},
            {},  # Empty form
        ]

        for i, data in enumerate(test_cases):
            with self.subTest(i=i, data=data):
                form = TaskSearchForm(data=data)
                self.assertTrue(form.is_valid(), f"Form should be valid for data: {data}")


class TaskAssignFormTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.worker1 = Worker.objects.create_user(username="worker1", password="pass", position=self.position)
        self.worker2 = Worker.objects.create_user(username="worker2", password="pass", position=self.position)
        self.worker_outside = Worker.objects.create_user(username="outside", password="pass", position=self.position)

        self.team = Team.objects.create(name="Team A", leader=self.worker1)
        self.team.members.set([self.worker1, self.worker2])

        self.project = Project.objects.create(
            name="Project X",
            description="Description",
            deadline=timezone.now() + timedelta(days=5),
            priority="MEDIUM_PRIORITY",
        )
        self.project.teams.add(self.team)

        self.task_type = TaskType.objects.create(name="Dev")

        self.task = Task.objects.create(
            name="Task 1",
            description="Task description",
            deadline=timezone.now() + timedelta(days=1),
            priority="HIGH_PRIORITY",
            task_type=self.task_type,
            project=self.project,
        )

    def test_form_valid_with_project_team_members(self):
        form_data = {"assignees": [self.worker1.id, self.worker2.id]}
        form = TaskAssignForm(data=form_data, instance=self.task)
        self.assertTrue(form.is_valid())

    def test_form_excludes_non_team_members(self):
        form = TaskAssignForm(instance=self.task)
        self.assertNotIn(self.worker_outside, form.fields["assignees"].queryset)
        self.assertIn(self.worker1, form.fields["assignees"].queryset)

    def test_form_not_allows_empty_assignees(self):
        form = TaskAssignForm(data={"assignees": []}, instance=self.task)
        self.assertFalse(form.is_valid())


class CustomUserCreationFormTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")

    def test_form_is_valid_with_correct_data(self):
        form_data = {
            "username": "newuser",
            "email": "new@example.com",
            "position": self.position.id,
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_without_position(self):
        form_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
            # position is missing
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("position", form.errors)

    def test_form_invalid_if_username_exists(self):
        Worker.objects.create_user(username="existinguser", password="pass123", position=self.position)
        form_data = {
            "username": "existinguser",
            "email": "another@example.com",
            "position": self.position.id,
            "password1": "AnotherPass123!",
            "password2": "AnotherPass123!",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)


class ProjectFormTests(TestCase):

    def setUp(self):
        self.team1 = Team.objects.create(name="Team A")
        self.team2 = Team.objects.create(name="Team B")

    def test_project_form_valid_data(self):
        data = {
            "name": "New Project",
            "description": "Project description",
            "deadline": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
            "priority": "CRITICAL",
            "teams": [self.team1.id, self.team2.id]
        }
        form = ProjectForm(data)
        self.assertTrue(form.is_valid())

    def test_project_form_invalid_without_name(self):
        data = {
            "description": "Missing name",
            "deadline": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
            "priority": "CRITICAL",
            "teams": [self.team1.id]
        }
        form = ProjectForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_deadline_initial_formatting(self):
        deadline = timezone.now() + timedelta(days=1)
        project = Project(name="Demo", description="desc", deadline=deadline, priority="LOW_PRIORITY")
        form = ProjectForm(instance=project)
        self.assertEqual(form.initial["deadline"], deadline.strftime("%Y-%m-%dT%H:%M"))


class TeamFormTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.worker1 = Worker.objects.create_user(username="Auser1", password="pass", position=self.position)
        self.worker2 = Worker.objects.create_user(username="user2", password="pass", position=self.position)

    def test_valid_data(self):
        form_data = {
            "name": "Team Rocket",
            "leader": self.worker1.id,
            "members": [self.worker1.id, self.worker2.id]
        }
        form = TeamForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_leader_not_in_members(self):
        form_data = {
            "name": "Team Alpha",
            "leader": self.worker1.id,
            "members": [self.worker2.id]
        }
        form = TeamForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_name(self):
        form_data = {
            "name": "",
            "leader": self.worker1.id,
            "members": [self.worker1.id]
        }
        form = TeamForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_members_are_ordered_by_position_name(self):
        pos = Position.objects.create(name="Z")
        worker_last = Worker.objects.create_user(username="a_user", password="pass", position=pos)

        form = TeamForm()
        members_queryset = list(form.fields["members"].queryset)

        self.assertEqual(members_queryset, [self.worker1, self.worker2, worker_last])

