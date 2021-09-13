from bootstrap_modal_forms.generic import BSModalCreateView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView, ListView

# ========  Auth  ========
from accounts.models import Profile
from centers.forms import SubTaskAttachmentForm, TaskAttachmentForm
from centers.models import Project, Center, SubTask, Task, SubTaskAttachment, TaskAttachment, ProjectPack
from dashboard.mixins import  PaginatedFilteredListView


class CustomLoginView(LoginView):
    def get_redirect_url(self):

        if self.request.user.is_superuser:
            return settings.CUSTOM_LOGIN_REDIRECT_URLS.superuser

        return super().get_redirect_url()


# ========  Dashboard ========
class MyTasks(LoginRequiredMixin, TemplateView):
    template_name = "tasks/mytask_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['to_do'] = []
        context['inprogress'] = []
        context['completed'] = []
        context['verified'] = []

        if self.request.user.is_superuser:
            return context

        profile = self.request.user.profile
        tasks = Task.objects.filter(employee=profile)
        subtasks = SubTask.objects.filter(employee=profile)

        context['employees'] = Profile.objects.filter(id=profile.id)

        context['to_do'] = list(subtasks.filter(status='to_do'))+list(tasks.filter(status='to_do'))
        context['inprogress'] = list(subtasks.filter(status='inprogress'))+list(tasks.filter(status='inprogress'))
        context['completed'] = list(subtasks.filter(status='completed'))+list(tasks.filter(status='completed'))
        context['verified'] = list(subtasks.filter(status='verified'))+list(tasks.filter(status='verified'))

        context['task_to_do'] = tasks.filter(status='to_do')
        context['subtask_to_do'] = subtasks.filter(status='to_do')

        context['task_inprogress'] = tasks.filter(status__exact='inprogress')
        context['subtask_inprogress'] = subtasks.filter(status__exact='inprogress')

        context['task_completed'] = tasks.filter(status__exact='completed')
        context['subtask_completed'] = subtasks.filter(status__exact='completed')

        context['task_verified'] = tasks.filter(status__exact='verified')
        context['subtask_verified'] = subtasks.filter(status__exact='verified')

        return context


class TaskAttachmentCreateView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'tasks/myattach_form.html'
    model = TaskAttachment
    form_class = TaskAttachmentForm
    success_url = reverse_lazy('dashboard:main')


class SubTaskAttachmentCreateView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'tasks/myattach_form.html'
    model = SubTaskAttachment
    form_class = SubTaskAttachmentForm
    success_url = reverse_lazy('dashboard:main')


class MyProjectPacks(LoginRequiredMixin,  ListView):
    model = ProjectPack
    template_name = 'myprojectpacks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile

        # if profile.has_perms(['projectpack']):
        #     context['managing_projectpacks'] = ProjectPack.objects.filter(manager=profile)
        # if profile.has_perms(['projectpack_monitoring']):
        #     context['monitoring_projectpacks'] = ProjectPack.objects.filter(monitoring_manager=profile)
        # if profile.has_perms(['project']):
        #     context['managing_projects'] = Project.objects.filter(manager=profile)
        # if profile.has_perms(['project_monitoring']):
        #     context['monitoring_projects'] = Project.objects.filter(monitoring_manager=profile)
        #
        # context['employed_projects'] = Project.objects.filter(employees__in=[profile])
        context['object'] = profile

        return context


class MyCeneter(LoginRequiredMixin, ListView):
    model = Center
    template_name = 'mycenter.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.request.user.profile.center_set.first()
        return context

