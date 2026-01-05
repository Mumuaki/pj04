from django.db.models import Q
from .models import Machine, Maintenance, Complaint
from apps.users.models import CustomUser

def get_filtered_machines(user, params):
    """Возвращает отфильтрованный QuerySet машин в зависимости от роли и GET-параметров."""
    if not user.is_authenticated:
        return Machine.objects.none()

    queryset = Machine.objects.select_related(
        'technique_model', 'engine_model', 'transmission_model',
        'drive_axle_model', 'steering_axle_model', 'client', 'service_company'
    ).order_by('-date_shipment')

    # Фильтрация по ролям
    if user.is_staff or user.is_superuser or getattr(user, 'is_manager', False):
        pass
    elif getattr(user, 'is_service', False):
        queryset = queryset.filter(service_company=user)
    elif getattr(user, 'is_client', False):
        queryset = queryset.filter(client=user)
    else:
        return Machine.objects.none()

    # Фильтры
    if val := params.get('technique_model'):
        queryset = queryset.filter(technique_model_id=val)
    if val := params.get('engine_model'):
        queryset = queryset.filter(engine_model_id=val)
    if val := params.get('transmission_model'):
        queryset = queryset.filter(transmission_model_id=val)
    if val := params.get('drive_axle_model'):
        queryset = queryset.filter(drive_axle_model_id=val)
    if val := params.get('steering_axle_model'):
        queryset = queryset.filter(steering_axle_model_id=val)

    return queryset

def get_filtered_maintenances(user, params):
    """Возвращает отфильтрованный QuerySet ТО."""
    if not user.is_authenticated:
        return Maintenance.objects.none()

    queryset = Maintenance.objects.select_related(
        'machine', 'service_type', 'service_company'
    ).order_by('-event_date')

    # Фильтрация по ролям
    if user.is_staff or user.is_superuser or getattr(user, 'is_manager', False):
        pass
    elif getattr(user, 'is_service', False):
        queryset = queryset.filter(machine__service_company=user)
    elif getattr(user, 'is_client', False):
        queryset = queryset.filter(machine__client=user)
    else:
        return Maintenance.objects.none()

    # Фильтры
    if val := params.get('service_type'):
        queryset = queryset.filter(service_type_id=val)
    if val := params.get('car_serial_to'):
        queryset = queryset.filter(machine__serial_number__icontains=val)
    if val := params.get('service_company_to'):
        queryset = queryset.filter(service_company_id=val)

    return queryset

def get_filtered_complaints(user, params):
    """Возвращает отфильтрованный QuerySet рекламаций."""
    if not user.is_authenticated:
        return Complaint.objects.none()

    queryset = Complaint.objects.select_related(
        'machine', 'failure_node', 'recovery_method', 'service_company'
    ).order_by('-failure_date')

    # Фильтрация по ролям
    if user.is_staff or user.is_superuser or getattr(user, 'is_manager', False):
        pass
    elif getattr(user, 'is_service', False):
        queryset = queryset.filter(machine__service_company=user)
    elif getattr(user, 'is_client', False):
        queryset = queryset.filter(machine__client=user)
    else:
        return Complaint.objects.none()

    # Фильтры
    if val := params.get('failure_node'):
        queryset = queryset.filter(failure_node_id=val)
    if val := params.get('recovery_method'):
        queryset = queryset.filter(recovery_method_id=val)
    if val := params.get('service_company_complaint'):
        queryset = queryset.filter(service_company_id=val)

    return queryset

def get_machines_for_filter(user):
    """Возвращает список машин для выпадающего списка фильтра ТО."""
    if user.is_superuser or getattr(user, 'is_manager', False):
        return Machine.objects.all().order_by('serial_number')
    elif getattr(user, 'is_service', False):
        return Machine.objects.filter(service_company=user).order_by('serial_number')
    elif getattr(user, 'is_client', False):
        return Machine.objects.filter(client=user).order_by('serial_number')
    return Machine.objects.none()

def get_service_companies_for_filter(user):
    """Возвращает список сервисных компаний, доступных пользователю."""
    if getattr(user, 'is_client', False):
        client_machines = Machine.objects.filter(client=user)
        service_company_ids = client_machines.values_list('service_company', flat=True).distinct()
        return CustomUser.objects.filter(id__in=service_company_ids)
    elif getattr(user, 'is_service', False):
        return CustomUser.objects.filter(id=user.id)
    else:
        return CustomUser.objects.filter(role='service')
