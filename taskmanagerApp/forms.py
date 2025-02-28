from django import forms
from django.contrib.auth.forms import UserCreationForm

from taskmanagerApp.models import Worker, Position


class WorkerSearchForm(forms.Form):
    SEARCH_CHOICES = [
        ("username", "Username"),
        ("position", "Position"),
    ]

    search_field = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Select Search field"
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
