import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.base import View

from centers.models import Project, Center
from dashboard.json_mixin import JSONCreateView, JSONDeleteView, JSONListView
from dashboard.mixins import PaginatedFilteredListView, RoleMixin
from .forms import *
from .models import Profile, UNINVERSITIES, MEASURES, DEGREES, SEXES, PERMISSIONS


# ========  Media File Access Controller ========
class MediaFileAccessController(View):
    def dispatch(self, request, *args, **kwargs):
        from django.http import HttpResponse
        if not request.user.is_authenticated:
            return HttpResponse("Login Required -- 401", status=401)

        # check if the user can access this media/static file and set `user_test_result` to `True` if so
        user_test_result = True
        if not user_test_result:
            return HttpResponse("You Have No Permission To Access This Page -- 403", status=403)

        return HttpResponse("OK", status=200)


# ========  Profile ========
class ProfileListView(LoginRequiredMixin, RoleMixin, PaginatedFilteredListView):
    model = Profile
    template_name = 'accounts/profile_list.html'


class CenterProfileListView(LoginRequiredMixin, RoleMixin, PaginatedFilteredListView):
    model = Profile
    template_name = 'accounts/profile_list.html'

    def get_queryset(self):
        center = Center.objects.get(id=self.request.resolver_match.kwargs['center_pk'])
        return center.employees.all()

    def get_context_data(self, **kwargs):
        kwargs['in_center'] = True
        kwargs['the_center'] = Center.objects.get(id=self.request.resolver_match.kwargs['center_pk'])
        return super().get_context_data(**kwargs)


class ProjectProfileListView(LoginRequiredMixin, RoleMixin, PaginatedFilteredListView):
    model = Profile
    template_name = 'accounts/profile_list.html'

    def get_queryset(self):
        project = Project.objects.get(id=self.request.resolver_match.kwargs['project_pk'])
        return project.employees.all()


class ProfileDetailsView(LoginRequiredMixin, RoleMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile_detail.html'

    # permission_required = ('accounts.view_profiles')


class CenterProfileCreateView(LoginRequiredMixin, RoleMixin, CreateView):
    model = Profile
    form_class = ProfileCreateForm
    template_name = 'accounts/profile_form.html'

    def get_success_url(self):
        return reverse_lazy('accounts:center_profile_list', kwargs={'center_pk': self.object.get_user_center})


    def get_context_data(self, **kwargs):
        kwargs['tittle'] = 'افزودن'
        kwargs['centers'] = Center.objects.filter(id=self.request.resolver_match.kwargs['center_pk'])
        kwargs['in_center'] = True
        kwargs['the_center'] = Center.objects.get(id=self.request.resolver_match.kwargs['center_pk'])
        kwargs['roles'] = PERMISSIONS
        kwargs['sexes'] = SEXES
        kwargs['degress'] = DEGREES
        kwargs['measures'] = MEASURES
        kwargs['universities'] = UNINVERSITIES
        kwargs['langs'] = Lang.objects.all()
        kwargs['softwares'] = Software.objects.all()
        kwargs['permissions'] = Permission.objects.all()
        return super().get_context_data(**kwargs)


class ProfileCreateView(LoginRequiredMixin, RoleMixin, CreateView):
    model = Profile
    form_class = ProfileCreateForm
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('accounts:profile_list')

    def get_context_data(self, **kwargs):
        kwargs['tittle'] = 'افزودن'
        kwargs['centers'] = Center.objects.all()
        kwargs['roles'] = PERMISSIONS
        kwargs['sexes'] = SEXES
        kwargs['degress'] = DEGREES
        kwargs['measures'] = MEASURES
        kwargs['universities'] = UNINVERSITIES
        kwargs['langs'] = Lang.objects.all()
        kwargs['softwares'] = Software.objects.all()
        kwargs['permissions'] = Permission.objects.all()
        return super().get_context_data(**kwargs)


class CenterProfileUpdateForm(LoginRequiredMixin, RoleMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_form.html'

    def get_success_url(self):
        return reverse_lazy('accounts:center_profile_list', kwargs={'center_pk': self.object.get_user_center})

    def get_context_data(self, **kwargs):
        kwargs['tittle'] = 'ویرایش'
        kwargs['centers'] = Center.objects.filter(id=self.request.resolver_match.kwargs['center_pk'])
        kwargs['in_center'] = True
        kwargs['the_center'] = Center.objects.get(id=self.request.resolver_match.kwargs['center_pk'])
        kwargs['roles'] = PERMISSIONS
        kwargs['sexes'] = SEXES
        kwargs['degress'] = DEGREES
        kwargs['measures'] = MEASURES
        kwargs['universities'] = UNINVERSITIES
        kwargs['langs'] = Lang.objects.all()
        kwargs['softwares'] = Software.objects.all()
        kwargs['permissions'] = Permission.objects.all()
        return super().get_context_data(**kwargs)


class ProfileUpdateForm(LoginRequiredMixin, RoleMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('accounts:profile_list')

    def get_context_data(self, **kwargs):
        kwargs['tittle'] = 'ویرایش'
        kwargs['centers'] = Center.objects.all()
        kwargs['roles'] = PERMISSIONS
        kwargs['sexes'] = SEXES
        kwargs['degress'] = DEGREES
        kwargs['measures'] = MEASURES
        kwargs['universities'] = UNINVERSITIES
        kwargs['langs'] = Lang.objects.all()
        kwargs['softwares'] = Software.objects.all()
        kwargs['permissions'] = Permission.objects.all()
        return super().get_context_data(**kwargs)


class ProfileDeleteView(LoginRequiredMixin, RoleMixin, JSONDeleteView):
    model = Profile

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.user.delete()
        self.object.delete()
        return self.render_to_response(self.get_context_data(success=True))