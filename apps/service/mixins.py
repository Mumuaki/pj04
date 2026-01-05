from django.contrib.auth.mixins import AccessMixin


class RoleBasedAccessMixin(AccessMixin):
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if user.is_superuser or getattr(user, 'is_manager', False):
            return queryset

        model_name = queryset.model.__name__

        if getattr(user, 'is_service', False):
            if model_name == 'Machine':
                return queryset.filter(service_company=user)
            elif model_name in ['Maintenance', 'Complaint']:
                return queryset.filter(machine__service_company=user)

        elif getattr(user, 'is_client', False):
            if model_name == 'Machine':
                return queryset.filter(client=user)
            elif model_name in ['Maintenance', 'Complaint']:
                return queryset.filter(machine__client=user)

        return queryset.none()
