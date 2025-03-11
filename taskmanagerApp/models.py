from django.contrib.auth.models import AbstractUser
from django.db import models

PRIORITY_CHOICES = (
    ("CRITICAL", "Critical"),
    ("ESSENTIAL", "Essential"),
    ("HIGH_PRIORITY", "High Priority"),
    ("MEDIUM_PRIORITY", "Medium Priority"),
    ("LOW_PRIORITY", "Low Priority"),
)


class Position(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name="workers")

    class Meta:
        verbose_name = "driver"
        verbose_name_plural = "drivers"

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


class TaskType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    deadline = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=100, choices=PRIORITY_CHOICES)
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE)
    assignees = models.ManyToManyField(Worker, related_name="assigned_tasks")
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    leader = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, related_name="led_teams")
    members = models.ManyToManyField(Worker, related_name="teams")

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    deadline = models.DateTimeField()
    priority = models.CharField(max_length=100, choices=PRIORITY_CHOICES)
    teams = models.ManyToManyField(Team, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


