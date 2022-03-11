import datetime

import jdatetime
import openpyxl
from django import forms

from accounts.models import Profile
from .models import Center, Project, Task, SubTask, TaskAttachment, STATUS_TYPES, SubTaskAttachment, ProjectPack, \
    ProjectAttachment, ProjectPackAttachment
from bootstrap_modal_forms.forms import BSModalModelForm


class CenterForm(forms.ModelForm):
    manager = forms.ModelChoiceField(queryset=Profile.objects.all())
    employees = forms.ModelMultipleChoiceField(queryset=Profile.objects.all(),required=False)

    class Meta:
        model = Center
        fields = '__all__'
        field_order = ['name', 'description', 'manager', 'employees']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()

        profile = instance.manager
        center = Center.objects.get(name='مرکز پیشفرض')
        center.employees.remove(profile)
        instance.employees.add(profile)

        return self.instance


class ProjectImportForm(forms.Form):
    excel_file = forms.FileField()

    def clean(self):
        cleaned_data = super().clean()

        excel_file = cleaned_data['excel_file']

        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb["Sheet1"]

        excel_data = list()
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            excel_data.append(row_data)

        for row in excel_data[1:]:
            manager_name = row[2]
            manager_name = manager_name.split(' ')
            manger_first_name = manager_name[0]
            if len(manager_name) == 2:
                manger_last_name = manager_name[1]
            else:
                manger_last_name = row[2][len(manager_name)+3:]

            center_name = row[3]

            started_at = row[4]
            if started_at == 'None':
                started_at = ''
            else:
                started_at = datetime.datetime.strptime(started_at, "%Y-%m-%d %H:%M:%S")

            to_be_finished = row[5]
            if to_be_finished == 'None':
                to_be_finished = ''
            else:
                to_be_finished = datetime.datetime.strptime(to_be_finished, "%Y-%m-%d %H:%M:%S")

            finished_at = row[8]
            if finished_at == 'None':
                finished_at = ''
            else:
                finished_at = datetime.datetime.strptime(finished_at, "%Y-%m-%d %H:%M:%S")

            payment = row[6]
            if payment:
                payment = int(payment)
            else:
                payment = 0

            paid = row[7]
            if paid:
                paid = int(paid)
            else:
                paid = 0

            status = row[9]

            try:
                center = Center.objects.get(name=center_name)
                manager = Profile.objects.get(user__first_name=manger_first_name,user__last_name=manger_last_name)
                Project.objects.create(name=row[0], description=row[1], manager=manager, center=center, started_at=started_at, finished_at=finished_at, to_be_finished=to_be_finished, payment=payment, paid=paid, status=status)
            except:
                pass

        return cleaned_data


class TaskImportForm(forms.Form):
    excel_file = forms.FileField()

    def clean(self):
        cleaned_data = super().clean()

        excel_file = cleaned_data['excel_file']

        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb["Sheet1"]

        excel_data = list()
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            excel_data.append(row_data)

        for row in excel_data[1:]:
            employee_name = row[3]
            employee_name = employee_name.split(' ')
            employee_first_name = employee_name[0]
            if len(employee_name) == 2:
                employee_last_name = employee_name[1]
            else:
                employee_last_name = row[2][len(employee_name)+3:]

            project_name = row[2]

            started_at = row[5]
            if started_at == 'None':
                started_at = ''
            else:
                started_at = datetime.datetime.strptime(started_at, "%Y-%m-%d %H:%M:%S")

            to_be_finished = row[6]
            if to_be_finished == 'None':
                to_be_finished = ''
            else:
                to_be_finished = datetime.datetime.strptime(to_be_finished, "%Y-%m-%d %H:%M:%S")

            finished_at = row[9]
            if finished_at == 'None':
                finished_at = ''
            else:
                finished_at = datetime.datetime.strptime(finished_at, "%Y-%m-%d %H:%M:%S")

            weight = row[4]
            if weight:
                weight = int(weight)
            else:
                weight = 1

            payment = row[7]
            if payment:
                payment = int(payment)
            else:
                payment = 0

            paid = row[8]
            if paid:
                paid = int(paid)
            else:
                paid = 0

            status = row[10]

            try:
                project = Project.objects.get(name=project_name)
                employee = Profile.objects.get(user__first_name=employee_first_name, user__last_name=employee_last_name)
                Task.objects.create(name=row[0], description=row[1], weight=weight, employee=employee, project=project, started_at=started_at, finished_at=finished_at, to_be_finished=to_be_finished, payment=payment, paid=paid, status=status)
            except:
                pass

        return cleaned_data


class ProjectPackAttachmentForm(BSModalModelForm):
    projectpack_id = forms.IntegerField(label='دسته پروژه', required=True)
    file = forms.FileField(label='پیوست', required=True)
    description = forms.CharField(label='توضیحات', required=False)

    class Meta:
        model = ProjectPackAttachment
        fields = ['file', 'description']
        # fields = '__all__'
        field_order = ['file', 'description']

    # def clean(self):
    #     cleaned_data = super().clean()
    #     return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        projectpack = ProjectPack.objects.get(id=self.cleaned_data['projectpack_id'])
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()
        projectpack.attachments.add(instance)
        if instance.description == 'فرم متمم زمانی':
            projectpack.time_supplement_form_uploaded = True
            projectpack.save()
        return self.instance


class ProjectPackForm(forms.ModelForm):
    # description = forms.CharField(required=False)
    center = forms.ModelChoiceField(queryset=Center.objects.all())
    manager = forms.ModelChoiceField(queryset=Profile.objects.all())
    monitoring_manager = forms.ModelChoiceField(queryset=Profile.objects.all())
    # employees = forms.ModelMultipleChoiceField(queryset=Profile.objects.all(),required=False)
    # to_be_finished = forms.DateTimeField(required=False)

    class Meta:
        model = ProjectPack
        fields = ['name', 'code', 'description', 'payment', 'center', 'to_be_started', 'to_be_finished', 'manager','monitoring_manager']
        # fields = '__all__'
        field_order = ['name', 'code', 'description', 'payment', 'center', 'to_be_started','to_be_finished', 'manager','monitoring_manager']

    # def clean(self):
    #     cleaned_data = super().clean()
    #     return cleaned_data
    #
    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     if commit:
    #         # If committing, save the instance and the m2m data immediately.
    #         self.instance.save()
    #         self._save_m2m()
    #     return self.instance


class ProjectPackUpdateForm(forms.ModelForm):
    # description = forms.CharField(required=False)
    center = forms.ModelChoiceField(queryset=Center.objects.all())
    manager = forms.ModelChoiceField(queryset=Profile.objects.all())
    monitoring_manager = forms.ModelChoiceField(queryset=Profile.objects.all())
    # employees = forms.ModelMultipleChoiceField(queryset=Profile.objects.all(),required=False)
    # to_be_finished = forms.DateTimeField(required=False)

    class Meta:
        model = ProjectPack
        fields = ['name','code', 'description', 'payment', 'center', 'manager','monitoring_manager']
        # fields = '__all__'
        field_order = ['name','code', 'description', 'payment', 'center', 'manager','monitoring_manager']

    def clean(self):
        cleaned_data = super().clean()

        instance = self.instance
        if not instance.created_financial_statement:
            payment = int(cleaned_data.get('payment'))

            project_payment_sum = 0
            for project in instance.project_set.all():
                project_payment_sum += project.payment
            if payment < project_payment_sum:
                    raise forms.ValidationError("مبلغ وارد شده از مجموع مبالغ پروژه ها کمتر است.")

        return cleaned_data


class ProjectAttachmentForm(BSModalModelForm):
    project_id = forms.IntegerField(label='پروژه', required=True)
    file = forms.FileField(label='پیوست', required=True)
    description = forms.CharField(label='توضیحات', required=False)

    class Meta:
        model = ProjectAttachment
        fields = ['file', 'description']
        # fields = '__all__'
        field_order = ['file', 'description']

    # def clean(self):
    #     cleaned_data = super().clean()
    #     return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        project = Project.objects.get(id=self.cleaned_data['project_id'])
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()
        project.attachments.add(instance)
        if instance.description == 'فرم متمم زمانی':
            project.time_supplement_form_uploaded = True
            project.save()
        return self.instance


class ProjectForm(forms.ModelForm):
    # description = forms.CharField(required=False)
    center = forms.ModelChoiceField(queryset=Center.objects.all())
    project_pack = forms.ModelChoiceField(queryset=ProjectPack.objects.all())
    manager = forms.ModelChoiceField(queryset=Profile.objects.all())
    monitoring_manager = forms.ModelChoiceField(queryset=Profile.objects.all())
    employees = forms.ModelMultipleChoiceField(queryset=Profile.objects.all(),required=False)
    # to_be_finished = forms.DateTimeField(required=False)

    class Meta:
        model = Project
        fields = ['name', 'description', 'payment', 'center','project_pack', 'to_be_finished', 'manager','monitoring_manager', 'employees']
        # fields = '__all__'
        field_order = ['name', 'description', 'payment', 'center','project_pack', 'to_be_finished', 'manager','monitoring_manager', 'employees']

    # def is_valid(self):
    #     valid = super(ProjectForm, self).is_valid()
    #     if len(self.errors)==1 and self.errors['payment']:
    #         return True
    #     else:
    #         if self.errors['payment']:
    #             self.errors.pop('payment')
    #         return valid

    def clean(self):
        cleaned_data = super().clean()

        # payment = ''.join(self.data.get('payment').split(','))
        # cleaned_data['payment'] = payment

        project_pack = cleaned_data.get('project_pack')
        to_be_finished = cleaned_data.get('to_be_finished')

        if to_be_finished > project_pack.to_be_finished:
            raise forms.ValidationError("تاریخ پایان پروژه نباید دیرتر از پایان دسته پروژه باشد.")

        payment = int(cleaned_data.get('payment'))

        if payment > project_pack.payment:
            raise forms.ValidationError("مبلغ وارد شده از مبلغ دسته پروژه بیشتر است.")

        other_project_payment_sum = 0
        for project in project_pack.project_set.all():
                other_project_payment_sum += project.payment
        if project_pack.payment < other_project_payment_sum + payment:
            raise forms.ValidationError(
                "مبلغ وارد شده با مجموع بالغ پروژه های دیگر دسته پروژه همخوانی ندارد. لطفا مبلغ کمتری را وارد نمایید.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # if not instance.created_financial_statement:
        #     payment = instance.payment
        #
        #     if payment > instance.project_pack.payment:
        #             raise forms.ValidationError("مبلغ وارد شده از مبلغ دسته پروژه بیشتر است.")
        #
        #     other_project_payment_sum = 0
        #     for project in instance.project_pack.project_set.all():
        #         if project != instance:
        #             other_project_payment_sum += project.payment
        #     if instance.project_pack.payment < other_project_payment_sum + payment:
        #         raise forms.ValidationError("مبلغ وارد شده با مجموع بالغ پروژه های دیگر دسته پروژه همخوانی ندارد. لطفا مبلغ کمتری را وارد نمایید.")
        #

        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()
        return self.instance


class ProjectUpdateForm(forms.ModelForm):
    # description = forms.CharField(required=False)
    center = forms.ModelChoiceField(queryset=Center.objects.all())
    project_pack = forms.ModelChoiceField(queryset=ProjectPack.objects.all())
    manager = forms.ModelChoiceField(queryset=Profile.objects.all())
    monitoring_manager = forms.ModelChoiceField(queryset=Profile.objects.all())
    employees = forms.ModelMultipleChoiceField(queryset=Profile.objects.all(),required=False)
    # to_be_finished = forms.DateTimeField(required=False)

    class Meta:
        model = Project
        fields = ['name', 'description', 'payment', 'center','project_pack', 'manager','monitoring_manager', 'employees']
        # fields = '__all__'
        field_order = ['name', 'description', 'payment', 'center','project_pack', 'manager','monitoring_manager', 'employees']

    # def is_valid(self):
    #     valid = super(ProjectUpdateForm, self).is_valid()
    #     if len(self.errors)==1 and self.errors['payment']:
    #         return True
    #     else:
    #         if self.errors['payment']:
    #             self.errors.pop('payment')
    #         return valid

    def clean(self):
        cleaned_data = super().clean()

        instance = self.instance
        if not instance.created_financial_statement:
            # payment = ''.join(self.data.get('payment').split(','))
            # cleaned_data['payment'] = payment
            payment = int(cleaned_data.get('payment'))

            if payment > instance.project_pack.payment:
                    raise forms.ValidationError("مبلغ وارد شده از مبلغ دسته پروژه بیشتر است.")

            other_project_payment_sum = 0
            for project in instance.project_pack.project_set.all():
                if project != instance:
                    other_project_payment_sum += project.payment
            if instance.project_pack.payment < other_project_payment_sum + payment:
                raise forms.ValidationError("مبلغ وارد شده با مجموع بالغ پروژه های دیگر دسته پروژه همخوانی ندارد. لطفا مبلغ کمتری را وارد نمایید.")

            task_payment_sum = 0
            for task in instance.task_set.all():
                task_payment_sum += task.payment
            if payment < task_payment_sum:
                    raise forms.ValidationError("مبلغ وارد شده از مجموع مبالغ فعالیت ها کمتر است.")

        return cleaned_data
    #
    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     if commit:
    #         # If committing, save the instance and the m2m data immediately.
    #         self.instance.save()
    #         self._save_m2m()
    #     return self.instance


class TaskAttachmentForm(BSModalModelForm):
    task_id = forms.IntegerField(label='فعالیت', required=True)
    file = forms.FileField(label='پیوست', required=True)
    description = forms.CharField(label='توضیحات', required=False)

    class Meta:
        model = TaskAttachment
        fields = ['file', 'description']
        # fields = '__all__'
        field_order = ['file', 'description']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        task = Task.objects.get(id=self.cleaned_data['task_id'])
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()
        task.attachments.add(instance)
        return self.instance


class TaskForm(BSModalModelForm):
    # name = forms.CharField(label='نام', required=True)
    # description = forms.CharField(label='نام', required=False)
    employee = forms.ModelChoiceField(queryset=Profile.objects.all(),required=False)
    # payment = forms.IntegerField(label='مبلغ قرارداد')
    # weight = forms.IntegerField(label='وزن')
    to_be_finished = forms.DateTimeField(required=False)
    status = forms.ChoiceField(choices=STATUS_TYPES)
    # attachments = forms.ModelMultipleChoiceField(queryset=TaskAttachment.objects.all(), required=False)

    class Meta:
        model = Task
        fields = ['name', 'description', 'employee', 'weight', 'to_be_finished', 'status']
        # fields = '__all__'
        field_order = ['name', 'description', 'employee', 'weight', 'to_be_finished', 'status']

    def clean(self):
        cleaned_data = super().clean()

        instance = self.instance
        # if not instance.created_financial_statement:
        #     payment = int(cleaned_data.get('payment'))
        #
        #     if payment > instance.project.payment:
        #             raise forms.ValidationError("مبلغ وارد شده از مبلغ پروژه بیشتر است.")
        #
        #     other_task_payment_sum = 0
        #     for task in instance.project.task_set.all():
        #         if task != instance:
        #             other_task_payment_sum += task.payment
        #     if instance.project.payment < other_task_payment_sum + payment:
        #         raise forms.ValidationError("مبلغ وارد شده با مجموع بالغ فعالیت های دیگر پروژه همخوانی ندارد. لطفا مبلغ کمتری را وارد نمایید.")

        to_be_finished = cleaned_data.get('to_be_finished')
        if to_be_finished:
            if to_be_finished > instance.project.to_be_finished:
                raise forms.ValidationError("تاریخ پایان فعالیت نباید دیرتر از پایان پروژه باشد.")

        return cleaned_data


class SubTaskAttachmentForm(BSModalModelForm):
    subtask_id = forms.IntegerField(label='زیرفعالیت', required=True)
    file = forms.FileField(label='پیوست', required=True)
    description = forms.CharField(label='توضیحات', required=False)

    class Meta:
        model = SubTaskAttachment
        fields = ['file', 'description']
        # fields = '__all__'
        field_order = ['file', 'description']

    def save(self, commit=True):
        instance = super().save(commit=False)
        subtask = SubTask.objects.get(id=self.cleaned_data['subtask_id'])
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save()
            self._save_m2m()
        subtask.attachments.add(instance)
        return self.instance


class SubTaskForm(BSModalModelForm):
    name = forms.CharField(label='نام کاربری', required=True)
    description = forms.CharField(label='نام', required=False)
    employee = forms.ModelChoiceField(queryset=Profile.objects.all(),required=False)
    # task = forms.ModelChoiceField(queryset=Project.objects.all())
    # payment = forms.IntegerField(label='مبلغ قرارداد')
    # weight = forms.IntegerField(label='وزن')
    to_be_finished = forms.DateTimeField(required=False)
    status = forms.ChoiceField(choices=STATUS_TYPES)
    # attachments = forms.ModelMultipleChoiceField(queryset=TaskAttachment.objects.all(), required=False)

    class Meta:
        model = SubTask
        fields = ['name', 'description', 'employee', 'to_be_finished', 'status']
        # fields = '__all__'
        field_order = ['name', 'description', 'employee', 'to_be_finished', 'status']


    # def clean(self):
    #     cleaned_data = super().clean()
    #
    #     return cleaned_data