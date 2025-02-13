from django import forms


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
