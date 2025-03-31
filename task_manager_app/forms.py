from django import forms
from django.contrib.auth.forms import UserCreationForm

from task_manager_app.models import Worker, Position, Project, Team, Task


class WorkerSearchForm(forms.Form):
    SEARCH_CHOICES = [
        ("username", "Username"),
        ("position", "Position"),
    ]

    search_field = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label=""
    )

    search_value = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter search value"}),
        label=""
    )


class TaskSearchForm(forms.Form):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Task name"}),
        label="Task Name"
    )

    project_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Project name"}),
        label="Project Name"
    )

    task_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Task type"}),
        label="Task Type"
    )

    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'All priorities')] + list(Task._meta.get_field('priority').choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Priority"
    )


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description", "deadline", "priority", "task_type", "assignees"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter task name"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Enter task description"}),
            "deadline": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "task_type": forms.Select(attrs={"class": "form-select"}),
            "assignees": forms.SelectMultiple(attrs={"class": "form-control selectpicker", "data-live-search": "true"}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        team = kwargs.pop('team', None)
        is_update = kwargs.pop("is_update", False)

        super().__init__(*args, **kwargs)

        if is_update:
            self.fields.pop("assignees")

        if team is not None and hasattr(team, "members"):
            self.fields["assignees"].queryset = team.members.all()
        elif project is not None and hasattr(project, "teams"):
            self.fields["assignees"].queryset = Worker.objects.filter(teams__in=project.teams.all()).distinct()

        if self.instance and self.instance.deadline:
            self.initial["deadline"] = self.instance.deadline.strftime("%Y-%m-%dT%H:%M")


class TaskAssignForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["assignees"]
        widgets = {
            "assignees": forms.SelectMultiple(attrs={"class": "form-control selectpicker", "data-live-search": "true"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.project:
            self.fields["assignees"].queryset = Worker.objects.filter(
                teams__in=self.instance.project.teams.all()
            ).distinct()


class CustomUserCreationForm(UserCreationForm):
    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),
        required=True,
        empty_label="Select Position",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    username = forms.CharField(
        label="",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
        error_messages={"unique": "This username is already taken. Please choose another one."}
    )
    email = forms.EmailField(
        label="",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Email address"})
    )
    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"})
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm Password"})
    )

    class Meta:
        model = Worker
        fields = ("position", "email",) + UserCreationForm.Meta.fields


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "deadline", "priority", "teams"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter project name"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Enter project description"}),
            "deadline": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "teams": forms.SelectMultiple(attrs={"class": "form-select", "size": "4"}),
        }
        labels = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.deadline:
            self.initial["deadline"] = self.instance.deadline.strftime("%Y-%m-%dT%H:%M")


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "members", "leader"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter team name"}),
            "members": forms.SelectMultiple(attrs={"class": "form-control selectpicker", "data-live-search": "true"}),
            "leader": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["members"].queryset = self.fields["members"].queryset.order_by("position__name")


