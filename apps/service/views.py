from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.views.generic import ListView
from .models import Machine, Maintenance, Complaint
from .serializers import MachineSerializer, MaintenanceSerializer, ComplaintSerializer

# --- API ViewSets ---

class MachineViewSet(viewsets.ModelViewSet):
    """
    API endpoint для просмотра и редактирования машин.
    """
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    permission_classes = [IsAuthenticated]

class MaintenanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint для ТО.
    """
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAuthenticated]

class ComplaintViewSet(viewsets.ModelViewSet):
    """
    API endpoint для Рекламаций.
    """
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]


# --- Frontend Views ---

class IndexView(ListView):
    model = Machine
    template_name = 'index.html'
    context_object_name = 'machines' # Список машин в шаблоне будет называться 'machines'

    def get_queryset(self):
        """
        Определяем, какие машины показывать в таблице (для авторизованных).
        """
        user = self.request.user
        
        # 1. Если пользователь не авторизован - список не нужен (только поиск)
        if not user.is_authenticated:
            return Machine.objects.none()
        
        # 2. Если Менеджер или Админ - видит все машины
        if user.is_staff or user.is_superuser or getattr(user, 'is_manager', False):
            return Machine.objects.all()
        
        # 3. Если Сервисная компания - видит машины, привязанные к ней
        if getattr(user, 'is_service', False):
            return Machine.objects.filter(service_company=user)
        
        # 4. Если Клиент - видит свои купленные машины
        if getattr(user, 'is_client', False):
            return Machine.objects.filter(client=user)
            
        # На всякий случай возвращаем пустой список
        return Machine.objects.none()

    def get_context_data(self, **kwargs):
        """
        Добавляем логику поиска по заводскому номеру (для всех).
        """
        context = super().get_context_data(**kwargs)
        
        # Получаем номер из GET-запроса (например ?serial_number=1234)
        serial_number = self.request.GET.get('serial_number')
        
        if serial_number:
            try:
                # Ищем конкретную машину
                found_machine = Machine.objects.get(serial_number=serial_number)
                context['search_result'] = found_machine
                context['search_performed'] = True
            except Machine.DoesNotExist:
                context['search_result'] = None
                context['search_performed'] = True
                context['not_found_message'] = "Данных о машине с таким заводским номером нет в системе"
        
        return context