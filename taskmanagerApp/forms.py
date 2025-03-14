from django import forms
from django.contrib.auth.forms import UserCreationForm

from taskmanagerApp.models import Worker, Position, Project


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
    SEARCH_CHOICES = [
        ("task_name", "Task Name"),
        ("project_name", "Project Name"),
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
