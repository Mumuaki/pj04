from django.contrib.auth.mixins import AccessMixin

class RoleBasedAccessMixin(AccessMixin):
    """
    Миксин для разграничения доступа к объектам на основе роли пользователя.
    Ограничивает QuerySet, чтобы пользователь мог взаимодействовать только 
    со 'своими' данными (связанными с его машинами).
    Работает для DetailView, UpdateView, DeleteView.
    """
    def get_queryset(self):
        # Получаем базовый queryset из View
        queryset = super().get_queryset()
        user = self.request.user

        # Если пользователь не авторизован, возвращаем пустой queryset
        # (хотя LoginRequiredMixin должен сработать раньше)
        if not user.is_authenticated:
            return queryset.none()

        # Менеджер и Суперпользователь видят всё
        if user.is_superuser or getattr(user, 'is_manager', False):
            return queryset

        # Определяем имя модели для выбора логики фильтрации
        model_name = queryset.model.__name__

        # Логика для Сервисной организации
        if getattr(user, 'is_service', False):
            if model_name == 'Machine':
                return queryset.filter(service_company=user)
            elif model_name in ['Maintenance', 'Complaint']:
                # Видят записи ТО и Рекламаций только для машин, которые они обслуживают
                return queryset.filter(machine__service_company=user)
        
        # Логика для Клиента
        elif getattr(user, 'is_client', False):
            if model_name == 'Machine':
                return queryset.filter(client=user)
            elif model_name in ['Maintenance', 'Complaint']:
                # Видят записи только своей техники
                return queryset.filter(machine__client=user)

        # Если роль не распознана или не имеет прав
        return queryset.none()
