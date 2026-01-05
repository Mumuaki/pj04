from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponseForbidden
from .models import (
    Machine, Maintenance, Complaint,
    TechniqueModel, EngineModel, TransmissionModel, 
    DriveAxleModel, SteeringAxleModel, ServiceType,
    FailureNode, RecoveryMethod
)
from django.core.paginator import Paginator
from .serializers import MachineSerializer, MaintenanceSerializer, ComplaintSerializer
from apps.users.models import CustomUser
from .forms import MachineForm, MaintenanceForm, ComplaintForm
from .mixins import RoleBasedAccessMixin


class MachineViewSet(viewsets.ModelViewSet):
    """API endpoint для просмотра и редактирования машин."""
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    permission_classes = [IsAuthenticated]


class MaintenanceViewSet(viewsets.ModelViewSet):
    """API endpoint для ТО."""
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAuthenticated]


class ComplaintViewSet(viewsets.ModelViewSet):
    """API endpoint для Рекламаций."""
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]


from .services import (
    get_filtered_machines, get_filtered_maintenances, get_filtered_complaints,
    get_machines_for_filter, get_service_companies_for_filter
)

class IndexView(ListView):
    model = Machine
    template_name = 'index.html'
    context_object_name = 'machines'
    paginate_by = 5

    def get_queryset(self):
        return get_filtered_machines(self.request.user, self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Логика поиска по заводскому номеру (для неавторизованных)
        serial_number = self.request.GET.get('serial_number')
        if serial_number:
            try:
                context['search_result'] = Machine.objects.get(serial_number=serial_number)
                context['search_performed'] = True
            except Machine.DoesNotExist:
                context['search_result'] = None
                context['search_performed'] = True
                context['not_found_message'] = "Данных о машине с таким заводским номером нет в системе"
        
        if self.request.user.is_authenticated:
            # Списки для фильтров
            context['machines_filter_list'] = get_machines_for_filter(self.request.user)
            companies_qs = get_service_companies_for_filter(self.request.user)
            context['complaint_filter_service_companies'] = companies_qs
            context['maintenance_filter_service_companies'] = companies_qs

            # Пагинация для ТО
            m_queryset = get_filtered_maintenances(self.request.user, self.request.GET)
            m_paginator = Paginator(m_queryset, 5)
            context['maintenances'] = m_paginator.get_page(self.request.GET.get('page_m'))
            
            # Пагинация для Рекламаций
            c_queryset = get_filtered_complaints(self.request.user, self.request.GET)
            c_paginator = Paginator(c_queryset, 5)
            context['complaints'] = c_paginator.get_page(self.request.GET.get('page_c'))
            
            # Справочники
            context['technique_models'] = TechniqueModel.objects.all()
            context['engine_models'] = EngineModel.objects.all()
            context['transmission_models'] = TransmissionModel.objects.all()
            context['drive_axle_models'] = DriveAxleModel.objects.all()
            context['steering_axle_models'] = SteeringAxleModel.objects.all()
            context['service_types'] = ServiceType.objects.all()
            context['failure_nodes'] = FailureNode.objects.all()
            context['recovery_methods'] = RecoveryMethod.objects.all()
            context['service_companies'] = CustomUser.objects.filter(role='service') # Общий список для справочников

        return context


class MachineDetailView(RoleBasedAccessMixin, DetailView):
    """Детальная страница машины."""
    model = Machine
    template_name = 'service/details/machine_detail.html'
    context_object_name = 'machine'


class MaintenanceDetailView(RoleBasedAccessMixin, DetailView):
    """Детальная страница ТО."""
    model = Maintenance
    template_name = 'service/details/maintenance_detail.html'
    context_object_name = 'maintenance'


class ComplaintDetailView(RoleBasedAccessMixin, DetailView):
    """Детальная страница рекламации."""
    model = Complaint
    template_name = 'service/details/complaint_detail.html'
    context_object_name = 'complaint'

# --- Views для создания записей (CreateViews) ---

class MachineCreateView(LoginRequiredMixin, CreateView):
    model = Machine
    form_class = MachineForm
    template_name = 'service/forms/machine_form.html'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        # Только Менеджер может добавлять машины
        if not getattr(request.user, 'is_manager', False) and not request.user.is_superuser:
            return HttpResponseForbidden("У вас нет прав для добавления машин.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление новой машины'
        return context


class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'service/forms/maintenance_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Клиент, Сервис и Менеджер могут добавлять ТО
        # (Проверка IsAuthenticated уже есть в родителе, доп. проверок не требуется, т.к. разрешено всем ролям)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление записи о ТО'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем пользователя в форму
        return kwargs
    
    def get_success_url(self):
        # Редирект на главную страницу с параметром для открытия вкладки ТО
        return reverse_lazy('index') + '?tab=maintenance'


class MaintenanceUpdateView(LoginRequiredMixin, RoleBasedAccessMixin, UpdateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'service/forms/maintenance_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование записи о ТО'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('index') + '?tab=maintenance'


class MaintenanceDeleteView(LoginRequiredMixin, RoleBasedAccessMixin, DeleteView):
    model = Maintenance
    template_name = 'service/forms/maintenance_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('index') + '?tab=maintenance'


class ComplaintCreateView(LoginRequiredMixin, CreateView):
    model = Complaint
    form_class = ComplaintForm
    template_name = 'service/forms/complaint_form.html'
    def get_success_url(self):
        return reverse_lazy('index') + '?tab=complaints'

    def dispatch(self, request, *args, **kwargs):
        # Сервис и Менеджер могут добавлять Рекламации. Клиент - НЕТ.
        user = request.user
        if not (getattr(user, 'is_service', False) or getattr(user, 'is_manager', False) or user.is_superuser):
             return render(request, 'service/permissions/complaint_denied.html', {
                 'message': "У вас нет прав для создания рекламаций"
             })
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оформление рекламации'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем пользователя в форму
        return kwargs


class ComplaintUpdateView(LoginRequiredMixin, RoleBasedAccessMixin, UpdateView):
    model = Complaint
    form_class = ComplaintForm
    template_name = 'service/forms/complaint_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование рекламации'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('index') + '?tab=complaints'


class ComplaintDeleteView(LoginRequiredMixin, RoleBasedAccessMixin, DeleteView):
    model = Complaint
    template_name = 'service/forms/complaint_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('index') + '?tab=complaints'
