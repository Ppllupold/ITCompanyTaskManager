from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.db.models.functions import Lower
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from taskmanagerApp.forms import WorkerSearchForm, CustomUserCreationForm, TaskSearchForm
from taskmanagerApp.models import Task, Position, Worker, Project


@login_required(login_url='login')
def index(request):
    return render(request, "home/index.html")


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "TMapp/task-list.html"

    def get_queryset(self):
        queryset = Task.objects.filter(is_completed=False).select_related("task_type", "project")
        search_form = TaskSearchForm(self.request.GET)
        sort_param = self.request.GET.get("sort", "priority")

        if search_form.is_valid():
            search_field = search_form.cleaned_data["search_field"]
            search_value = search_form.cleaned_data["search_value"]

            if search_field == "task_name":
               queryset = queryset.filter(name__icontains=search_value)
            elif search_field == "project_name":
                queryset = queryset.filter(project__name__icontains=search_value)

        if sort_param == "task_type":
            return queryset.order_by("task_type__name")
        return queryset.order_by("priority")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = TaskSearchForm(self.request.GET)
        return context


class PositionListView(LoginRequiredMixin, generic.ListView):
    model = Position
    template_name = "TMapp/position-list.html"

    def get_queryset(self):
        queryset = Position.objects.annotate(worker_count=Count("workers"))

        sort_param = self.request.GET.get("sort", "name")
        if sort_param == "worker_count":
            return queryset.order_by(sort_param)
        return queryset.order_by(Lower("name"))


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    template_name = "TMapp/worker-list.html"

    def get_queryset(self):

        queryset = (
            Worker.objects.annotate(task_count=Count("assigned_tasks",
                                                     filter=Q(assigned_tasks__is_completed=False)),
                                    team_count=Count("teams")).
            select_related("position").
            prefetch_related("assigned_tasks", "teams")
        )
        search_form = WorkerSearchForm(self.request.GET)
        sort_param = self.request.GET.get("sort")
        if search_form.is_valid():
            search_field = search_form.cleaned_data["search_field"]
            search_value = search_form.cleaned_data["search_value"]

            if search_field == "position":
                queryset = queryset.filter(position__name__icontains=search_value)
            elif search_field == "username":
                queryset = queryset.filter(username__icontains=search_value)

        if sort_param == "task_count":
            queryset = queryset.order_by("task_count")
        elif sort_param == "team_count":
            queryset = queryset.order_by("-team_count")
        else:
            queryset.order_by("username")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["searchForm"] = WorkerSearchForm(self.request.GET)
        return context


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = "TMapp/task-detail.html"


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker
    template_name = "TMapp/worker-detail.html"
    queryset = Worker.objects.annotate(
        task_count=Count("assigned_tasks"),
        team_count=Count("teams"),
    ).select_related("position").prefetch_related("assigned_tasks", "teams")


class WorkerDeleteView(generic.DeleteView):
    model = Worker
    template_name = "TMapp/worker_confirm_delete.html"
    success_url = reverse_lazy("taskManagerApp:index")


class RegisterView(generic.CreateView):
    model = Worker
    template_name = "registration/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
