from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.db.models.functions import Lower
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from taskmanagerApp.forms import WorkerSearchForm, CustomUserCreationForm, TaskSearchForm, ProjectForm, TeamForm, \
    TaskForm, TaskAssignForm
from taskmanagerApp.models import Task, Position, Worker, Project, Team


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
        project_id = self.request.GET.get("project_id")

        if project_id:
            queryset = queryset.filter(project_id=project_id)

        if search_form.is_valid():
            name = search_form.cleaned_data.get("name")
            project_name = search_form.cleaned_data.get("project_name")
            task_type = search_form.cleaned_data.get("task_type")
            priority = search_form.cleaned_data.get("priority")

            if name:
                queryset = queryset.filter(name__icontains=name)
            if project_name:
                queryset = queryset.filter(project__name__icontains=project_name)
            if task_type:
                queryset = queryset.filter(task_type__name__icontains=task_type)
            if priority:
                queryset = queryset.filter(priority=priority)

        if sort_param == "task_type":
            queryset = queryset.order_by("task_type__name")
        else:
            queryset = queryset.order_by("priority")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = TaskSearchForm(self.request.GET)
        return context


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "TMapp/task_form.html"
    success_url = reverse_lazy("taskmanager:task-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        project_id = self.request.GET.get('project_id')
        team_id = self.request.GET.get('team_id')

        if project_id:
            project = Project.objects.get(pk=project_id)
            kwargs['project'] = project

        if team_id:
            team = Team.objects.get(pk=team_id)
            kwargs['team'] = team

        return kwargs

    def form_valid(self, form):
        form.instance.project = getattr(self, 'project_instance', None)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_id"] = self.request.GET.get("project_id") or self.kwargs.get("pk")
        return context


class TaskUpdateView(LoginRequiredMixin, generic.edit.UpdateView):
    model = Task
    template_name = "TMapp/task_form.html"
    form_class = TaskForm

    def get_success_url(self):
        project_id = self.object.project.id
        return reverse_lazy("taskmanager:project-teams", kwargs={"pk": project_id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["is_update"] = True
        return kwargs


class TaskAssignView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskAssignForm
    template_name = "TMapp/task_assign.html"

    def get_success_url(self):
        return reverse_lazy("taskManagerApp:task-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])
        assignees = form.cleaned_data["assignees"]
        task.assignees.add(*assignees)
        return redirect("taskManagerApp:task-detail", pk=task.pk)


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
        team_id = self.request.GET.get("team_id")
        if team_id:
            queryset = queryset.filter(teams__id=team_id).distinct()

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


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Worker
    template_name = "TMapp/worker_confirm_delete.html"
    success_url = reverse_lazy("taskManagerApp:index")


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    template_name = "TMapp/project-list.html"
    queryset = (Project.objects.annotate(member_count=Count("teams__members", distinct=True))
                .prefetch_related("teams"))


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = "TMapp/project-detail.html"


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    template_name = "TMapp/project-create.html"
    form_class = ProjectForm
    success_url = reverse_lazy("taskManagerApp:project-list")


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    template_name = "TMapp/project-create.html"
    form_class = ProjectForm
    success_url = reverse_lazy("taskManagerApp:project-list")


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template_name = "TMapp/project_confirm_delete.html"
    success_url = reverse_lazy("taskManagerApp:project-list")


class ProjectTeamsView(generic.DetailView):
    model = Project
    template_name = "TMapp/project-teams-list.html"
    context_object_name = "project"


class TeamUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Team
    template_name = "TMapp/team_form.html"
    form_class = TeamForm

    def get_success_url(self):
        project = self.object.projects.first()
        return reverse_lazy("taskManagerApp:project-teams", kwargs={"pk": project.pk})


class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    template_name = "TMapp/team_form.html"
    form_class = TeamForm

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.members.set(form.cleaned_data["members"])
        form.instance.save()

        project_id = self.request.GET.get("project_id")
        if project_id:
            project = Project.objects.get(id=project_id)
            project.teams.add(self.object)
        return response

    def get_success_url(self):
        project_id = self.request.GET.get("project_id")
        if project_id:
            return reverse_lazy("taskmanager:project-teams", kwargs={"pk": project_id})
        return reverse_lazy("taskmanager:project-list")


def remove_team_from_project(request, project_id, team_id):
    project = get_object_or_404(Project, pk=project_id)
    team = get_object_or_404(Team, pk=team_id)
    if request.method == "POST":
        project.teams.remove(team)
    return redirect("taskmanager:project-teams", pk=project_id)


class RegisterView(generic.CreateView):
    model = Worker
    template_name = "registration/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
