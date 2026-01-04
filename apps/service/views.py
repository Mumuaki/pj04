from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from .models import (
    Machine, Maintenance, Complaint,
    TechniqueModel, EngineModel, TransmissionModel, 
    DriveAxleModel, SteeringAxleModel, ServiceType,
    FailureNode, RecoveryMethod
)
from .serializers import MachineSerializer, MaintenanceSerializer, ComplaintSerializer
from apps.users.models import CustomUser
from .forms import MachineForm, MaintenanceForm, ComplaintForm


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


class IndexView(ListView):
    model = Machine
    template_name = 'index.html'
    context_object_name = 'machines'

    def get_queryset(self):
        """Определяем, какие машины показывать в таблице (для авторизованных)."""
        user = self.request.user
        
        if not user.is_authenticated:
            return Machine.objects.none()
        
        queryset = Machine.objects.all()
        
        # Фильтрация по ролям
        if user.is_staff or user.is_superuser or getattr(user, 'is_manager', False):
            pass  # Видит все
        elif getattr(user, 'is_service', False):
            queryset = queryset.filter(service_company=user)
        elif getattr(user, 'is_client', False):
            queryset = queryset.filter(client=user)
        else:
            queryset = Machine.objects.none()
        
        # Применяем фильтры из GET-параметров
        technique_model = self.request.GET.get('technique_model')
        if technique_model:
            queryset = queryset.filter(technique_model_id=technique_model)
        
        engine_model = self.request.GET.get('engine_model')
        if engine_model:
            queryset = queryset.filter(engine_model_id=engine_model)
        
        transmission_model = self.request.GET.get('transmission_model')
        if transmission_model:
            queryset = queryset.filter(transmission_model_id=transmission_model)
        
        drive_axle_model = self.request.GET.get('drive_axle_model')
        if drive_axle_model:
            queryset = queryset.filter(drive_axle_model_id=drive_axle_model)
        
        steering_axle_model = self.request.GET.get('steering_axle_model')
        if steering_axle_model:
            queryset = queryset.filter(steering_axle_model_id=steering_axle_model)
        
        return queryset

    def get_maintenance_queryset(self):
        """Получение отфильтрованного списка ТО."""
        user = self.request.user
        
        if not user.is_authenticated:
            return Maintenance.objects.none()
        
        queryset = Maintenance.objects.select_related('machine', 'service_type', 'service_company')
        
        # Фильтрация по ролям
        if user.is_staff or user.is_superuser or getattr(user, 'is_manager', False):
            pass  # Видит все
        elif getattr(user, 'is_service', False):
            queryset = queryset.filter(machine__service_company=user)
        elif getattr(user, 'is_client', False):
            queryset = queryset.filter(machine__client=user)
        else:
            queryset = Maintenance.objects.none()
        
        # Применяем фильтры
        service_type = self.request.GET.get('service_type')
        if service_type:
            queryset = queryset.filter(service_type_id=service_type)
        
        car_serial_to = self.request.GET.get('car_serial_to')
        if car_serial_to:
            queryset = queryset.filter(machine__serial_number__icontains=car_serial_to)
        
        service_company_to = self.request.GET.get('service_company_to')
        if service_company_to:
            queryset = queryset.filter(service_company_id=service_company_to)
        
        return queryset

    def get_complaints_queryset(self):
        """Получение отфильтрованного списка рекламаций."""
        user = self.request.user
        
        if not user.is_authenticated:
            return Complaint.objects.none()
        
        queryset = Complaint.objects.select_related(
            'machine', 'failure_node', 'recovery_method', 'service_company'
        )
        
        # Фильтрация по ролям
        if user.is_staff or user.is_superuser or getattr(user, 'is_manager', False):
            pass  # Видит все
        elif getattr(user, 'is_service', False):
            queryset = queryset.filter(machine__service_company=user)
        elif getattr(user, 'is_client', False):
            queryset = queryset.filter(machine__client=user)
        else:
            queryset = Complaint.objects.none()
        
        # Применяем фильтры
        failure_node = self.request.GET.get('failure_node')
        if failure_node:
            queryset = queryset.filter(failure_node_id=failure_node)
        
        recovery_method = self.request.GET.get('recovery_method')
        if recovery_method:
            queryset = queryset.filter(recovery_method_id=recovery_method)
        
        service_company_complaint = self.request.GET.get('service_company_complaint')
        if service_company_complaint:
            queryset = queryset.filter(service_company_id=service_company_complaint)
        
        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем данные для всех вкладок и фильтров."""
        context = super().get_context_data(**kwargs)
        
        # Логика поиска по заводскому номеру (для неавторизованных)
        serial_number = self.request.GET.get('serial_number')
        if serial_number:
            try:
                found_machine = Machine.objects.get(serial_number=serial_number)
                context['search_result'] = found_machine
                context['search_performed'] = True
            except Machine.DoesNotExist:
                context['search_result'] = None
                context['search_performed'] = True
                context['not_found_message'] = "Данных о машине с таким заводским номером нет в системе"
        
        # Данные для авторизованных пользователей
        if self.request.user.is_authenticated:
            # Данные для вкладок
            context['maintenances'] = self.get_maintenance_queryset()
            context['complaints'] = self.get_complaints_queryset()
            
            # Справочники для фильтров
            context['technique_models'] = TechniqueModel.objects.all()
            context['engine_models'] = EngineModel.objects.all()
            context['transmission_models'] = TransmissionModel.objects.all()
            context['drive_axle_models'] = DriveAxleModel.objects.all()
            context['steering_axle_models'] = SteeringAxleModel.objects.all()
            context['service_types'] = ServiceType.objects.all()
            context['failure_nodes'] = FailureNode.objects.all()
            context['recovery_methods'] = RecoveryMethod.objects.all()
            context['service_companies'] = CustomUser.objects.filter(role='service')
        
        return context


class MachineDetailView(DetailView):
    """Детальная страница машины."""
    model = Machine
    template_name = 'service/machine_detail.html'
    context_object_name = 'machine'


class MaintenanceDetailView(DetailView):
    """Детальная страница ТО."""
    model = Maintenance
    template_name = 'service/maintenance_detail.html'
    context_object_name = 'maintenance'


class ComplaintDetailView(DetailView):
    """Детальная страница рекламации."""
    model = Complaint
    template_name = 'service/complaint_detail.html'
    context_object_name = 'complaint'

# --- Views для создания записей (CreateViews) ---

class MachineCreateView(LoginRequiredMixin, CreateView):
    model = Machine
    form_class = MachineForm
    template_name = 'service/machine_form.html'
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
    template_name = 'service/maintenance_form.html'

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


class ComplaintCreateView(LoginRequiredMixin, CreateView):
    model = Complaint
    form_class = ComplaintForm
    template_name = 'service/complaint_form.html'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        # Сервис и Менеджер могут добавлять Рекламации. Клиент - НЕТ.
        user = request.user
        if not (getattr(user, 'is_service', False) or getattr(user, 'is_manager', False) or user.is_superuser):
             return HttpResponseForbidden("У вас нет прав для создания рекламаций.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оформление рекламации'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем пользователя в форму
        return kwargs

