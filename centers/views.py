import datetime
import json
import math
import numpy as np

from numpy import log as ln

import jdatetime
import openpyxl as openpyxl
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView, FormView, ListView

from accounts.models import Profile
from dashboard.json_mixin import JSONDeleteView, JSONUpdateView
from dashboard.mixins import PaginatedFilteredListView, RoleMixin
from transactions.models import ProjectPackTransaction

from .models import Center, Project, Task, SubTask, TaskAttachment, SubTaskAttachment, ProjectPack, ProjectAttachment, \
    ProjectPackAttachment
from .forms import CenterForm, ProjectForm, TaskForm, SubTaskForm, ProjectImportForm, TaskImportForm, \
    TaskAttachmentForm, SubTaskAttachmentForm, ProjectPackForm, ProjectAttachmentForm, ProjectPackAttachmentForm, \
    ProjectPackUpdateForm, ProjectUpdateForm
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView


# centers
class CenterListView(LoginRequiredMixin, RoleMixin, PaginatedFilteredListView):
    model = Center
    template_name = 'centers/center_list.html'


class CenterCreateView(LoginRequiredMixin, RoleMixin, CreateView):
    model = Center
    template_name = 'centers/center_form.html'
    form_class = CenterForm
    success_url = reverse_lazy('centers:center_list')
    extra_context = {
        'tittle': 'افزودن',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profiles = Profile.objects.all()
        context['profiles'] = []
        for profile in profiles:
            if profile.center_set.count() == 0:
                context['profiles'].append(profile)

        centermanagers = Profile.objects.filter(permissions__code__in=['center'])
        # centermanagers = Profile.objects.filter(Q(is_centermanager=True) | Q(is_supermanager=True))
        context['center_managers'] = []
        for profile in centermanagers:
            try:
                Center.objects.get(manager=profile)
            except:
                context['center_managers'].append(profile)

        return context


class CenterDetailsView(LoginRequiredMixin, RoleMixin, DetailView):
    model = Center
    template_name = 'centers/center_detail.html'


class CenterUpdateForm(LoginRequiredMixin, RoleMixin, UpdateView):
    model = Center
    template_name = 'centers/center_form.html'
    form_class = CenterForm
    success_url = reverse_lazy('centers:center_list')
    extra_context = {
        'tittle': 'ویرایش',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        center = Center.objects.get(id=self.request.resolver_match.kwargs['pk'])

        profiles = Profile.objects.all()
        context['profiles'] = []
        for profile in profiles:
            if profile.center_set.count() == 0:
                context['profiles'].append(profile)

        centermanagers = Profile.objects.filter(permissions__code__in=['center'])
        # centermanagers = Profile.objects.filter(Q(is_centermanager=True) | Q(is_supermanager=True))
        context['center_managers'] = []
        for profile in centermanagers:
            if profile.center_set.count() == 0:
                context['center_managers'].append(profile)

        center = Center.objects.get(id=self.request.resolver_match.kwargs['pk'])
        for profile in center.employees.all():
            context['profiles'].append(profile)
        context['center_managers'].append(center.manager)

        return context


class CenterDeleteView(LoginRequiredMixin, RoleMixin, JSONDeleteView):
    model = Center


# project packs
class CenterProjectPackListView(LoginRequiredMixin, ListView):
    model = ProjectPack
    template_name = 'projectpacks/projectpack_list.html'

    def get_queryset(self):
        return ProjectPack.objects.filter(center_id=self.request.resolver_match.kwargs['center_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['the_center'] = Center.objects.get(id=self.request.resolver_match.kwargs['center_pk'])
        context['in_center'] = True
        return context


class ProjectPackListView(LoginRequiredMixin, RoleMixin, PaginatedFilteredListView):
    model = ProjectPack
    template_name = 'projectpacks/projectpack_list.html'


class CenterProjectPackCreateView(LoginRequiredMixin, RoleMixin, CreateView):
    model = ProjectPack
    template_name = 'projectpacks/projectpack_form.html'
    form_class = ProjectPackForm
    # success_url = reverse_lazy('centers:projectpack_list')
    extra_context = {
        'tittle': 'افزودن',
    }

    def get_success_url(self):
        # if you are passing 'pk' from 'urls' to 'DeleteView' for company
        # capture that 'pk' as companyid and pass it to 'reverse_lazy()' function
        # project = SubTask.objects.get(id=self.kwargs['pk']).task.project
        return reverse_lazy('centers:center_projectpack_list', kwargs={'center_pk': self.kwargs['center_pk'] })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['centers'] = Center.objects.filter(id=self.request.user.profile.get_user_center)
        context['the_center'] = Center.objects.get(id=self.request.user.profile.get_user_center)
        context['in_center'] = True
        context['profiles'] = Profile.objects.all()
        context['projectpack_managers'] = Profile.objects.filter(permissions__code__in=['projectpack'])
        context['projectpack_monitoring_managers'] = Profile.objects.filter(permissions__code__in=['projectpack_monitoring'])
        return context


class ProjectPackCreateView(LoginRequiredMixin, RoleMixin, CreateView):
    model = ProjectPack
    template_name = 'projectpacks/projectpack_form.html'
    form_class = ProjectPackForm
    success_url = reverse_lazy('centers:projectpack_list')
    extra_context = {
        'tittle': 'افزودن',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['centers'] = Center.objects.all()
        context['in_center'] = False
        context['profiles'] = Profile.objects.all()
        context['projectpack_managers'] = Profile.objects.filter(permissions__code__in=['projectpack'])
        context['projectpack_monitoring_managers'] = Profile.objects.filter(permissions__code__in=['projectpack_monitoring'])
        return context


class ProjectPackAttachmentCreateView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'projectpacks/attach_form.html'
    model = ProjectPackAttachment
    form_class = ProjectPackAttachmentForm

    def get_success_url(self):
        # if you are passing 'pk' from 'urls' to 'DeleteView' for company
        # capture that 'pk' as companyid and pass it to 'reverse_lazy()' function
        # project = Project.objects.get(id=self.kwargs['pk'])
        return reverse_lazy('centers:projectpack_details', kwargs={'pk': self.kwargs['pk']})


class ProjectPackAttachmentDeleteView(LoginRequiredMixin, RoleMixin, JSONDeleteView):
    model = ProjectPackAttachment


class ProjectPackDetailsView(LoginRequiredMixin, RoleMixin, DetailView):
    model = ProjectPack
    template_name = 'projectpacks/projectpack_detail.html'


class CenterProjectPackUpdateView(LoginRequiredMixin, RoleMixin, UpdateView):
    model = ProjectPack
    template_name = 'projectpacks/projectpack_form.html'
    form_class = ProjectPackUpdateForm
    # success_url = reverse_lazy('centers:projectpack_list')
    extra_context = {
        'tittle': 'افزودن',
    }

    def get_success_url(self):
        # if you are passing 'pk' from 'urls' to 'DeleteView' for company
        # capture that 'pk' as companyid and pass it to 'reverse_lazy()' function
        # project = SubTask.objects.get(id=self.kwargs['pk']).task.project
        return reverse_lazy('centers:center_projectpack_list', kwargs={'center_pk': self.kwargs['center_pk'] })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['centers'] = Center.objects.filter(id=self.request.user.profile.get_user_center)
        context['the_center'] = Center.objects.get(id=self.request.user.profile.get_user_center)
        context['in_center'] = True
        context['profiles'] = Profile.objects.all()
        context['projectpack_managers'] = Profile.objects.filter(permissions__code__in=['projectpack'])
        context['projectpack_monitoring_managers'] = Profile.objects.filter(permissions__code__in=['projectpack_monitoring'])
        return context


class ProjectPackUpdateView(LoginRequiredMixin, RoleMixin, UpdateView):
    model = ProjectPack
    template_name = 'projectpacks/projectpack_form.html'
    form_class = ProjectPackUpdateForm
    success_url = reverse_lazy('centers:projectpack_list')
    extra_context = {
        'tittle': 'ویرایش',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['centers'] = Center.objects.all()
        context['in_center'] = False
        context['profiles'] = Profile.objects.all()
        context['projectpack_managers'] = Profile.objects.filter(permissions__code__in=['projectpack'])
        context['projectpack_monitoring_managers'] = Profile.objects.filter(permissions__code__in=['projectpack_monitoring'])
        return context


class ProjectPackDeleteView(LoginRequiredMixin, RoleMixin, JSONDeleteView):
    model = ProjectPack


# projects
class ProjectPackProjectListView(LoginRequiredMixin, RoleMixin, PaginatedFilteredListView):
    model = Project
    template_name = 'projects/project_list.html'

    def get_queryset(self):
        return Project.objects.filter(project_pack_id=self.request.resolver_match.kwargs['projectpack_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['the_projectpack'] = ProjectPack.objects.get(id=self.request.resolver_match.kwargs['projectpack_pk'])
        return context


class ProjectPackProjectCreateView(LoginRequiredMixin, RoleMixin, CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    form_class = ProjectForm
    # success_url = reverse_lazy('centers:project_list')
    extra_context = {
        'tittle': 'افزودن',
    }

    def get_success_url(self):
        return reverse_lazy('centers:projectpack_project_list', kwargs={'projectpack_pk': self.object.project_pack.id })


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projectpack = ProjectPack.objects.get(id=self.request.resolver_match.kwargs['projectpack_pk'])
        context['projectpacks'] = ProjectPack.objects.filter(id=self.request.resolver_match.kwargs['projectpack_pk'])
        context['the_projectpack'] = projectpack
        context['in_projectpack'] = True
        context['centers'] = [projectpack.center]
        context['center'] = projectpack.center
        context['profiles'] = Profile.objects.all()
        context['project_managers'] = Profile.objects.filter(center__in=[projectpack.center],permissions__code__in=['project'])
        context['project_monitoring_managers'] = Profile.objects.filter(center__in=[projectpack.center],permissions__code__in=['project_monitoring'])
        return context


class ProjectCreateView(LoginRequiredMixin, RoleMixin, CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    form_class = ProjectForm
    success_url = reverse_lazy('centers:project_list')
    extra_context = {
        'tittle': 'افزودن',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['centers'] = Center.objects.filter(id=self.request.user.profile.get_user_center)
        context['in_center'] = False
        context['profiles'] = Profile.objects.all()
        context['project_managers'] = Profile.objects.filter(
            Q(is_projectmanager=True) | Q(is_centermanager=True) | Q(is_supermanager=True)).distinct()
        return context


class ProjectBulkCreateView(LoginRequiredMixin, RoleMixin, FormView):
    template_name = 'projects/project_import.html'
    form_class = ProjectImportForm
    success_url = reverse_lazy('centers:project_list')
    extra_context = {
        'tittle': 'project',
    }


class TaskBulkCreateView(LoginRequiredMixin, RoleMixin, FormView):
    template_name = 'projects/project_import.html'
    form_class = TaskImportForm
    success_url = reverse_lazy('centers:project_list')
    extra_context = {
        'tittle': 'task',
    }


class ProjectAttachmentCreateView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'projects/attach_form.html'
    model = ProjectAttachment
    form_class = ProjectAttachmentForm

    def get_success_url(self):
        # if you are passing 'pk' from 'urls' to 'DeleteView' for company
        # capture that 'pk' as companyid and pass it to 'reverse_lazy()' function
        # project = Project.objects.get(id=self.kwargs['pk'])
        return reverse_lazy('centers:projectpack_project_details', kwargs={'pk': self.kwargs['pk'],'projectpack_pk': self.kwargs['projectpack_pk']})


class ProjectAttachmentDeleteView(LoginRequiredMixin, RoleMixin, JSONDeleteView):
    model = ProjectAttachment


class ProjectPackProjectDetailsView(LoginRequiredMixin, RoleMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = Project.objects.get(id=self.kwargs['pk'])

        if project.started_at:
            context['gone_days'] = (datetime.datetime.now().timestamp() - project.started_at.timestamp()) / 86400
        else:
            context['gone_days'] = 0
        context['remained_days'] = (project.to_be_finished.timestamp() - datetime.datetime.now().timestamp()) / 86400

        project.recalculate_progress()
        project.recalculate_weightless_progress()

        if project.started_at:
            total_duration = (project.to_be_finished.timestamp() - project.started_at.timestamp()) / 86400
            context['done_days'] = project.progress*total_duration/100
            context['programmed_remained_days'] = total_duration*(100-project.progress)/100

            years = []
            months = {'1': 'فروردین', '2': 'اردیبهشت', '3': 'خرداد', '4': 'تیر', '5': 'مرداد', '6': 'شهریور',
                      '7': 'مهر',
                      '8': 'آبان', '9': 'آذر', '10': 'دی', '11': 'بهمن', '12': 'اسفند'}
            days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16',
                    '17',
                    '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

            first_year = jdatetime.date.fromgregorian(date=project.started_at.date()).year
            last_year = jdatetime.datetime.now().year
            for i in range(first_year, last_year + 1):
                years.append(i)

            context['now'] = datetime.datetime.now
            context['years'] = years
            context['months'] = months
            context['days'] = days

            total_weight = 0
            for task in project.task_set.all():
                total_weight += task.weight

            duration = project.to_be_finished - project.started_at
            hours = duration.total_seconds() / 3600
            days = duration.total_seconds() / (3600 * 24)
            months = duration.total_seconds() / (3600 * 24 * 30)

            context['to_be_progressed_dayly'] = [0]*24
            dayly = total_weight / hours
            for i in range(24):
                x = round(np.log(dayly)*(i-12), 5)
                context['to_be_progressed_dayly'][i] = round(1/(1+np.power(math.e, -x)), 5)

            context['to_be_progressed_monthly'] = [0] * 31
            monthly = total_weight / days
            for i in range(31):
                x = round(0.1*np.log(monthly)*(i-15), 5)
                context['to_be_progressed_monthly'][i] = round(1/(1+np.power(math.e, -x)), 5)

            context['to_be_progressed_yearly'] = [0] * 12
            yearly = total_weight / months
            for i in range(12):
                x = round(np.log(np.log(yearly))*(i-5), 5)
                context['to_be_progressed_yearly'][i] = round(1/(1+np.power(math.e, -x)), 5)

        else:
            context['done_days'] = 0
            context['programmed_remained_days'] = context['remained_days']

        return context


class ProjectPackProjectUpdateForm(LoginRequiredMixin, RoleMixin, UpdateView):
    model = Project
    template_name = 'projects/project_form.html'
    form_class = ProjectUpdateForm
    # success_url = reverse_lazy('centers:project_list')
    extra_context = {
        'tittle': 'ویرایش',
    }

    def get_success_url(self):
        return reverse_lazy('centers:projectpack_project_list', kwargs={'projectpack_pk': self.object.project_pack.id })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projectpack = ProjectPack.objects.get(id=self.request.resolver_match.kwargs['projectpack_pk'])
        context['projectpacks'] = ProjectPack.objects.filter(id=self.request.resolver_match.kwargs['projectpack_pk'])
        context['the_projectpack'] = projectpack
        context['in_projectpack'] = True
        context['centers'] = [projectpack.center]
        context['center'] = projectpack.center
        context['profiles'] = Profile.objects.all()
        context['project_managers'] = Profile.objects.filter(center__in=[projectpack.center],
                                                             permissions__code__in=['project'])
        context['project_monitoring_managers'] = Profile.objects.filter(center__in=[projectpack.center],
                                                                        permissions__code__in=['project_monitoring'])
        return context


class ProjectPackProjectDeleteView(LoginRequiredMixin, RoleMixin, JSONDeleteView):
    model = Project


class TaskUpdateView(LoginRequiredMixin, BSModalUpdateView):
    template_name = 'tasks/task_form.html'
    model = Task
    form_class = TaskForm
    # success_url = reverse_lazy('centers:task_list')

    def get_success_url(self):
        # if you are passing 'pk' from 'urls' to 'DeleteView' for company
        # capture that 'pk' as companyid and pass it to 'reverse_lazy()' function
        project = self.object.project
        return reverse_lazy('centers:task_list', kwargs={'pk_project': project.id})


class TaskAttachmentCreateView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'tasks/attach_form.html'
    model = TaskAttachment
    form_class = TaskAttachmentForm

    def get_success_url(self):
        # if you are passing 'pk' from 'urls' to 'DeleteView' for company
        # capture that 'pk' as companyid and pass it to 'reverse_lazy()' function
        project = Task.objects.get(id=self.kwargs['pk']).project
        return reverse_lazy('centers:task_list', kwargs={'pk_project': project.id})


class SubTaskUpdateView(LoginRequiredMixin, BSModalUpdateView):
    template_name = 'tasks/subtask_form.html'
    model = SubTask
    form_class = SubTaskForm
    # success_url = reverse_lazy('centers:task_list')

    def get_success_url(self):
        # if you are passing 'pk' from 'urls' to 'DeleteView' for company
        # capture that 'pk' as companyid and pass it to 'reverse_lazy()' function
        project = self.object.task.project
        return reverse_lazy('centers:task_list', kwargs={'pk_project': project.id})


class SubTaskAttachmentCreateView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'tasks/attach_form.html'
    model = SubTaskAttachment
    form_class = SubTaskAttachmentForm

    def get_success_url(self):
        # if you are passing 'pk' from 'urls' to 'DeleteView' for company
        # capture that 'pk' as companyid and pass it to 'reverse_lazy()' function
        project = SubTask.objects.get(id=self.kwargs['pk']).task.project
        return reverse_lazy('centers:task_list', kwargs={'pk_project': project.id})


# tasks
class TaskListView(LoginRequiredMixin, PaginatedFilteredListView):
    model = Task
    template_name = 'tasks/task_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = Project.objects.get(id=self.kwargs['pk_project'])
        subtasks = SubTask.objects.filter(task__project_id=project.id)

        context['now'] = datetime.datetime.now()

        context['employees'] = project.employees.all()
        context['project_id'] = project.id
        context['project'] = project

        context['task_to_do'] = project.task_set.filter(status='to_do')
        context['subtask_to_do'] = subtasks.filter(status='to_do')

        context['task_inprogress'] = project.task_set.filter(status__exact='inprogress')
        context['subtask_inprogress'] = subtasks.filter(status__exact='inprogress')

        context['task_completed'] = project.task_set.filter(status__exact='completed')
        context['subtask_completed'] = subtasks.filter(status__exact='completed')

        context['task_verified'] = project.task_set.filter(status__exact='verified')
        context['subtask_verified'] = subtasks.filter(status__exact='verified')

        return context


class TaskDeleteView(LoginRequiredMixin, RoleMixin, JSONDeleteView):
    model = Task


class SubTaskDeleteView(LoginRequiredMixin, RoleMixin, JSONDeleteView):
    model = SubTask


class AjaxHandler(TemplateView):
    def lineChart_dayly(self, project, year, month, day, data):
        total_weight = 0
        for task in project.task_set.all():
            total_weight += task.weight
        duration = project.to_be_finished - project.started_at
        hours = duration.total_seconds() / 3600
        dayly = total_weight / hours

        data['progressed'] = [0] * 24
        for hour in range(0, 24):
            try:
                first = jdatetime.datetime(year, month, day, hour).togregorian()
            except:
                try:
                    day = 30
                    first = jdatetime.datetime(year, month, day, hour).togregorian()
                except:
                    day = 29
                    first = jdatetime.datetime(year, month, day, hour).togregorian()
            try:
                last = jdatetime.datetime(year, month, day, hour + 1).togregorian()
            except:
                try:
                    last = jdatetime.datetime(year, month, day + 1).togregorian()
                except:
                    try:
                        last = jdatetime.datetime(year, month + 1, 1).togregorian()
                    except:
                        last = jdatetime.datetime(year + 1, 1, 1).togregorian()

            for task in project.task_set.filter(finished_at__range=[first, last]):
                try:
                    data['progressed'][hour - 1] += task.weight
                except:
                    pass

            if data['progressed'][hour - 1]:
                x = np.log(data['progressed'][hour - 1]) * (hour - 12)
                data['progressed'][hour - 1] = round(1 / (1 + np.power(math.e, -x)), 5)
            else:
                x = np.log(dayly) * (hour - 12)
                data['progressed'][hour - 1] = round(1 / (1 + np.power(math.e, -x)), 5)

        # for i in range(1,24):
        #     data['progressed'][i] += data['progressed'][i-1]

    def lineChart_monthly(self, project, year, month, data):
        total_weight = 0
        for task in project.task_set.all():
            total_weight += task.weight
        duration = project.to_be_finished - project.started_at
        days = duration.total_seconds() / (3600 * 24)
        monthly = total_weight / days

        data['progressed'] = [0] * 31
        for day in range(1, 32):
            try:
                first = jdatetime.date(year, month, day).togregorian()
            except:
                break
            try:
                last = jdatetime.date(year, month, day + 1).togregorian()
            except:
                try:
                    last = jdatetime.date(year, month + 1, 1).togregorian()
                except:
                    last = jdatetime.date(year + 1, 1, 1).togregorian()

            for task in project.task_set.filter(finished_at__range=[first, last]):
                try:
                    data['progressed'][day - 1] += task.weight
                except:
                    pass

            if data['progressed'][day - 1]:
                x = 0.1*np.log(data['progressed'][day - 1]) * (day - 15)
                data['progressed'][day - 1] = round(1 / (1 + np.power(math.e, -x)), 5)
            else:
                x = 0.1*np.log(monthly) * (day - 15)
                data['progressed'][day - 1] = round(1 / (1 + np.power(math.e, -x)), 5)

        # for i in range(1,31):
        #     data['progressed'][i] += data['progressed'][i-1]

    def lineChart_yearly(self, project, year, data):
        total_weight = 0
        for task in project.task_set.all():
            total_weight += task.weight
        duration = project.to_be_finished - project.started_at
        months = duration.total_seconds() / (3600 * 24 * 30)
        yearly = total_weight / months

        data['progressed'] = [0] * 12
        for month in range(1, 13):
            first = jdatetime.date(year, month, 1).togregorian()
            try:
                last = jdatetime.date(year, month + 1, 1).togregorian()
            except:
                last = jdatetime.date(year + 1, 1, 1).togregorian()

            for task in project.task_set.filter(finished_at__range=[first, last]):
                try:
                    data['progressed'][month - 1] += task.weight
                except:
                    pass

            if data['progressed'][month - 1]:
                x = np.log(np.log(data['progressed'][month - 1])) * (month - 5)
                data['progressed'][month - 1] = round(1 / (1 + np.power(math.e, -x)), 5)
            else:
                x = np.log(yearly) * (month - 5)
                data['progressed'][month - 1] = round(1 / (1 + np.power(math.e, -x)), 5)

        # for i in range(1,12):
        #     data['progressed'][i] += data['progressed'][i-1]

    def get(self, request, *args, **kwargs):
        request_type = request.GET.get('request_type')
        data = {'error': 0}

        if request_type == 'project_lineChart':
            project_id = request.GET.get('project_id')
            ymd = request.GET.get('ymd')
            year = int(request.GET.get('year'))
            project = Project.objects.get(id=project_id)

            if ymd == 'y':
                self.lineChart_yearly(project, year, data)
            elif ymd == 'm':
                month = int(request.GET.get('month'))
                self.lineChart_monthly(project, year, month, data)
            elif ymd == 'd':
                month = int(request.GET.get('month'))
                day = int(request.GET.get('day'))
                self.lineChart_dayly(project, year, month, day, data)

        if request_type == 'projectpack_suppliment_time':
            projectpack_id = request.GET.get('projectpack_id')
            time_supplement_days = int(request.GET.get('time_supplement_days'))
            time_supplement_description = request.GET.get('time_supplement_description')

            projectpack = ProjectPack.objects.get(id=projectpack_id)
            # projectpack.time_supplemented = True
            projectpack.time_supplement_days += time_supplement_days

            if projectpack.time_supplement_description == None:
                'for ' + str(time_supplement_days) + ' days: ' + time_supplement_description + ', '
            else:
                projectpack.time_supplement_description += 'for '+ str(time_supplement_days) + ' days: ' + time_supplement_description + ', '

            new_date = projectpack.to_be_finished
            new_date += datetime.timedelta(days=time_supplement_days)

            projectpack.to_be_finished = new_date
            projectpack.save()

        if request_type == 'project_suppliment_time':
            project_id = request.GET.get('project_id')
            time_supplement_days = int(request.GET.get('time_supplement_days'))
            time_supplement_description = request.GET.get('time_supplement_description')

            project = Project.objects.get(id=project_id)
            # project.time_supplemented = True
            project.time_supplement_days += time_supplement_days

            if project.time_supplement_description == None:
                'for ' + str(time_supplement_days) + ' days: ' + time_supplement_description + ', '
            else:
                project.time_supplement_description += 'for '+ str(time_supplement_days) + ' days: ' + time_supplement_description + ', '


            new_date = project.to_be_finished
            new_date += datetime.timedelta(days=time_supplement_days)

            project.to_be_finished = new_date
            project.save()

        if request_type == 'profile_password_change':
            profile_id = request.GET.get('profile_id')
            new_password = request.GET.get('new_password')
            profile = Profile.objects.get(id=profile_id)
            profile.user.set_password(new_password)
            profile.user.save()

        if request_type == 'task_payment':
            task_id = request.GET.get('task_id')
            payment = request.GET.get('payment')
            task = Task.objects.get(id=task_id)
            if task.paid + int(payment) > task.payment:
                data['error'] = 1
                return JsonResponse(data)
            task.paid += int(payment)
            task.save()
            if task.project.paid + int(payment) > task.project.payment:
                data['error'] = 2
                return JsonResponse(data)
            task.project.paid += int(payment)
            task.project.save()

        if request_type == 'task_edit':
            task_id = request.GET.get('task_id')
            payment = int(request.GET.get('payment'))
            task = Task.objects.get(id=task_id)
            project = task.project
            sum = 0
            for tsk in project.task_set.all():
                if tsk != task:
                    sum += task.payment
            if (project.payment-sum)>=payment:
                task.payment = payment
                task.save()
            else:
                data['error'] = 3
                return JsonResponse(data)

        if request_type == 'task_create':
            project_id = request.GET.get('project_id')
            task_name = request.GET.get('task_name')
            if task_name:
                Task.objects.create(name=task_name, project=Project.objects.get(id=project_id))

        if request_type == 'task_status_update':
            task_id = request.GET.get('task_id')
            task_new_status = request.GET.get('task_new_status')
            task = Task.objects.get(id=task_id)
            task.status = task_new_status
            task.save(update_fields=['status'])

        if request_type == 'subtask_create':
            task_id = request.GET.get('task_id')
            subtask_name = request.GET.get('subtask_name')

            task = Task.objects.get(id=task_id)
            if subtask_name:
                subtask = SubTask.objects.create(name=subtask_name, task=task)
                subtask.employee = task.employee
                subtask.save()

        if request_type == 'subtask_status_update':
            subtask_id = request.GET.get('subtask_id')
            subtask_new_status = request.GET.get('subtask_new_status')
            subtask = SubTask.objects.get(id=subtask_id)
            subtask.status = subtask_new_status
            subtask.save(update_fields=['status'])

        return JsonResponse(data)
