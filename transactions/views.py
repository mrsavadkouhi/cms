import datetime

import openpyxl as openpyxl
from bootstrap_modal_forms.generic import BSModalCreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView, FormView, ListView

from accounts.models import Profile
from centers.models import Center, Project, ProjectPack, Task
from dashboard.json_mixin import JSONDeleteView
from dashboard.mixins import PaginatedFilteredListView, RoleMixin
from .forms import TransactionAttachmentForm

from .models import Transaction, ProjectPackTransaction, TRANSACTION_TITTLES, ProjectTransaction, TaskTransaction, TransactionAttachment


# equipments
class CenterTransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transaction_list.html'

    def get_queryset(self):
        return Transaction.objects.filter(center_id=self.request.resolver_match.kwargs['center_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['the_center'] = Center.objects.get(id=self.request.resolver_match.kwargs['center_pk'])
        context['in_center'] = True
        return context


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transaction_list.html'


class TransactionDeleteView(LoginRequiredMixin, RoleMixin, JSONDeleteView):
    model = Transaction


class TransactionAttachmentCreateView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'attach_form.html'
    model = TransactionAttachment
    form_class = TransactionAttachmentForm

    def get_success_url(self):
        # if you are passing 'pk' from 'urls' to 'DeleteView' for company
        # capture that 'pk' as companyid and pass it to 'reverse_lazy()' function
        transaction = Transaction.objects.get(id=self.kwargs['pk'])
        return reverse_lazy('transactions:center_transaction_list', kwargs={'center_pk': transaction.center.id})


class AjaxHandler(TemplateView):
    def is_sorted(self, tmp):
        flag = True
        i = 1
        while i < len(tmp):
            if tmp[i] < tmp[i - 1]:
                flag = False
                return flag
            i += 1
        return flag

    def get(self, request, *args, **kwargs):
        request_type = request.GET.get('request_type')
        data = {'error': 0}

        if request_type == 'projectpack_create_financial_statement':
            projectpack_id = int(request.GET.get('projectpack_id'))
            projectpack = ProjectPack.objects.get(id=projectpack_id)

            prepayment = int(request.GET.get('prepayment'))
            instalment_num = int(request.GET.get('instalment_num'))

            if projectpack.payment == 0:
                data = {'error': 2}
                return JsonResponse(data)

            if (projectpack.payment-prepayment) < 0:
                data = {'error': 1}
                return JsonResponse(data)

            now = datetime.datetime.now()
            try:
                fivadayslater = datetime.datetime(year=now.year,month=now.month,day=now.day+5)
            except:
                try:
                    fivadayslater = datetime.datetime(year=now.year, month=now.month+1, day=4)
                except:
                    fivadayslater = datetime.datetime(year=now.year+1, month=1, day=4)

            ProjectPackTransaction.objects.create(project_pack=projectpack, center=projectpack.center, tittle=TRANSACTION_TITTLES[0][0], value=prepayment,sequence_number=0,due_date=fivadayslater,due_flag=True)

            if (projectpack.payment-prepayment) == 0:
                pass
            else:
                instalment_value = (projectpack.payment-prepayment)/instalment_num
                for i in range(instalment_num):
                    try:
                        onemonthafterthat = datetime.datetime(year=fivadayslater.year, month=fivadayslater.month+i+1, day=fivadayslater.day)
                    except:
                        onemonthafterthat = datetime.datetime(year=now.year + 1, month=i+1, day=fivadayslater.day)
                    ProjectPackTransaction.objects.create(project_pack=projectpack, center=projectpack.center, tittle=TRANSACTION_TITTLES[1][0], value=instalment_value,sequence_number=i+1,due_date=onemonthafterthat)

            projectpack.created_financial_statement = True
            projectpack.save()

        if request_type == 'project_create_financial_statement':
            project_id = int(request.GET.get('project_id'))
            prepayment = int(request.GET.get('prepayment'))
            project = Project.objects.get(id=project_id)

            paragraph_dues = request.GET.get('paragraph_dues').split(';')[:-1]
            paragraph_num = int(request.GET.get('paragraph_num'))
            if paragraph_num == 0:
                data = {'error': 3}
                return JsonResponse(data)

            if not self.is_sorted(paragraph_dues):
                data = {'error': 4}
                return JsonResponse(data)

            if project.payment == 0:
                data = {'error': 2}
                return JsonResponse(data)

            if prepayment > 0:
                ProjectTransaction.objects.create(project=project, center=project.center, tittle=TRANSACTION_TITTLES[0][0], value=prepayment, sequence_number=0, due_flag=True)

            paragraph_value = (project.payment - prepayment)/paragraph_num
            for i in range(paragraph_num):
                ProjectTransaction.objects.create(project=project, center=project.center, tittle=TRANSACTION_TITTLES[2][0], value=paragraph_value,sequence_number=i+1,due_progress=paragraph_dues[i])

            project.created_financial_statement = True
            project.save()

        if request_type == 'task_create_financial_statement':
            task_id = int(request.GET.get('task_id'))
            task = Task.objects.get(id=task_id)

            paragraph_num = int(request.GET.get('paragraph_num'))
            if paragraph_num == 0:
                data = {'error': 3}
                return JsonResponse(data)

            if task.payment == 0:
                data = {'error': 2}
                return JsonResponse(data)

            now = datetime.datetime.now()
            paragraph_value = task.payment/paragraph_num
            for i in range(paragraph_num):
                try:
                    onemonthafterthat = datetime.datetime(year=now.year, month=now.month+i+1, day=now.day)
                except:
                    onemonthafterthat = datetime.datetime(year=now.year + 1, month=i+1, day=now.day)
                TaskTransaction.objects.create(task=task, center=task.project.center, tittle=TRANSACTION_TITTLES[2][0], value=paragraph_value,sequence_number=i+1,due_date=onemonthafterthat)

            task.created_financial_statement = True
            task.save()

        if request_type == 'pay_financial_statement':
            transaction_id = int(request.GET.get('transaction_id'))
            transaction = Transaction.objects.get(id=transaction_id)

            try:
                projectpack = transaction.project_pack
                projectpack.usable_fund = transaction.value
                projectpack.paid += transaction.value
                projectpack.save()

                # transaction.due_flag = False
                # transaction.save()
                try:
                    next_projectpack_transaction = projectpack.projectpacktransaction_set.get(sequence_number=transaction.sequence_number + 1)
                    next_projectpack_transaction.due_flag = True
                    next_projectpack_transaction.save()
                except:
                    pass
            except:
                try:
                    project = transaction.project
                    value = transaction.value
                    usable_fund = project.project_pack.usable_fund
                    if value <= usable_fund:
                        project.project_pack.usable_fund -= value
                        project.project_pack.save()
                        project.usable_fund += value
                        project.paid += value
                        project.save()

                        # transaction.due_flag = False
                        # transaction.save()

                        try:
                            next_project_transaction = project.projecttransaction_set.get(sequence_number=transaction.sequence_number + 1)
                            next_project_transaction.due_flag = True
                            next_project_transaction.save()
                        except:
                            pass


                    else:
                        data = {'error': 1}
                        return JsonResponse(data)
                except:
                    task = transaction.task
                    value = transaction.value
                    usable_fund = task.project.usable_fund
                    if value <= usable_fund:
                        task.project.usable_fund -= value
                        task.project.save()
                        task.paid += transaction.value
                        task.save()
                    else:
                        data = {'error': 2}
                        return JsonResponse(data)

            now = datetime.datetime.now()
            transaction.paid_at = now
            transaction.due_flag = False
            transaction.save()

        return JsonResponse(data)
