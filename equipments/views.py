import datetime

import openpyxl as openpyxl
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView, FormView, ListView

from accounts.models import Profile
from centers.models import Center, Project
from dashboard.json_mixin import JSONDeleteView
from dashboard.mixins import PaginatedFilteredListView, RoleMixin

from .models import Equipment, EQUIPMENT_TYPES, Rent, EquipmentType
from .forms import EquipmentForm


# equipments
class CenterEquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'equipment_list.html'
    extra_context = {
        'in_center': True,
    }

    def get_queryset(self):
        return Equipment.objects.filter(owner_id=self.request.resolver_match.kwargs['center_pk'])


class RentListView(LoginRequiredMixin, ListView):
    model = Rent
    template_name = 'rent_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment = Equipment.objects.get(id=self.request.resolver_match.kwargs['pk'])
        context['object_list'] = Rent.objects.filter(equipment=equipment)
        context['equipment_id'] = equipment.id
        context['equipment_name'] = equipment.name
        return context


class TypeListView(LoginRequiredMixin, ListView):
    model = EquipmentType
    template_name = 'type_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        types = EquipmentType.objects.all()
        data = []
        for type in types:
            total_costs = 0
            hours = 0
            equipments = type.equipment_set.all()
            for equipment in equipments:
                rents = equipment.rent_set.all()
                for rent in rents:
                    if not rent.is_reservation:
                        total_costs += rent.total_price
                        hours += rent.total_hours

            days = hours//24
            months = days//30
            years = months//12
            try:
                daily_cost = total_costs/days
            except:
                daily_cost = 'تعداد داده های ناکافی'
            try:
                monthly_cost = total_costs/months
            except:
                monthly_cost = 'تعداد داده های ناکافی'
            try:
                yearly_cost = total_costs/years
            except:
                yearly_cost = 'تعداد داده های ناکافی'

            data.append((type.name, daily_cost, monthly_cost, yearly_cost, total_costs, hours))

        context['object_list'] = data
        return context


class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'equipment_list.html'


class CenterEquipmentCreateView(LoginRequiredMixin, RoleMixin, CreateView):
    model = Equipment
    template_name = 'equipment_form.html'
    form_class = EquipmentForm
    success_url = reverse_lazy('equipments:equipment_list')
    extra_context = {
        'tittle': 'افزودن',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['centers'] = Center.objects.filter(id=self.request.resolver_match.kwargs['center_pk'])
        context['in_center'] = True
        context['types'] = EquipmentType.objects.all()

        return context


class EquipmentCreateView(LoginRequiredMixin, RoleMixin, CreateView):
    model = Equipment
    template_name = 'equipment_form.html'
    form_class = EquipmentForm
    success_url = reverse_lazy('equipments:equipment_list')
    extra_context = {
        'tittle': 'افزودن',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['centers'] = Center.objects.all()
        context['types'] = EquipmentType.objects.all()

        return context


class EquipmentDetailsView(LoginRequiredMixin, RoleMixin, DetailView):
    model = Equipment
    template_name = 'equipment_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object.check_if_out_of_rent()

        context['events'] = Rent.objects.filter(equipment_id=self.request.resolver_match.kwargs['pk'])
        context['projects'] = Project.objects.all()
        context['employees'] = Profile.objects.all()
        context['centers'] = Center.objects.all()

        profile = self.request.user.profile
        context['center'] = profile.center_set.first()

        return context


class EquipmentUpdateForm(LoginRequiredMixin, RoleMixin, UpdateView):
    model = Equipment
    template_name = 'equipment_form.html'
    form_class = EquipmentForm
    success_url = reverse_lazy('equipments:equipment_list')
    extra_context = {
        'tittle': 'ویرایش',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['centers'] = Center.objects.all()

        context['types'] = EquipmentType.objects.all()

        return context


class EquipmentDeleteView(LoginRequiredMixin, RoleMixin, JSONDeleteView):
    model = Equipment


class AjaxHandler(TemplateView):
    def get(self, request, *args, **kwargs):
        request_type = request.GET.get('request_type')
        data = {'error': 0}

        if request_type =='create_equipmenttype':
            name = request.GET.get('name')
            description = request.GET.get('description')
            EquipmentType.objects.get_or_create(name=name, description=description)

        if request_type =='delete_equipmenttype':
            equipmenttype_id = int(request.GET.get('equipmenttype_id'))
            equipmenttype = EquipmentType.objects.get(id=equipmenttype_id)
            equipmenttype.delete()

        if request_type =='rent':
            equipment_id = request.GET.get('equipment_id')
            project_id = request.GET.get('project_id')
            center_id = request.GET.get('center_id')
            borrower_id = request.GET.get('borrower_id')
            rent_for = request.GET.get('rent_for')
            at = request.GET.get('at')
            to = request.GET.get('to')

            if at:
                at = datetime.datetime.strptime(at, "%Y-%m-%d %H:%M")
            if to:
                to = datetime.datetime.strptime(to, "%Y-%m-%d %H:%M")

            if at >= to:
                data['error'] = 3
                return JsonResponse(data)
            now = datetime.datetime.now()
            if now > at or now > to:
                data['error'] = 2
                return JsonResponse(data)

            equipment = Equipment.objects.get(id=equipment_id)
            rents = Rent.objects.filter(equipment=equipment).filter(Q(to__range=[at, to]) or Q(at__range=[at, to]) or Q(Q(at__gte=at,to__lte=at) and Q(at__gte=to,to__lte=to)))
            if rents.count():
                data['error'] = 1
                return JsonResponse(data)

            borrower = Profile.objects.get(id=borrower_id)
            center = Center.objects.get(id=center_id)
            project = Project.objects.get(id=project_id)

            if equipment.is_rented:
                Rent.objects.create(equipment=equipment, project=project, borrower=borrower, center=center, reserve_for=rent_for, at=at, to=to)
            else:
                Rent.objects.create(equipment=equipment, project=project, borrower=borrower, center=center, reserve_for=rent_for, at=at, to=to, is_reservation=False)

        return JsonResponse(data)
