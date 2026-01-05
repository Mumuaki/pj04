from django import forms
from .models import Machine, Maintenance, Complaint

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = '__all__'
        widgets = {
            'date_shipment': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        from apps.users.models import CustomUser
        self.fields['client'].queryset = CustomUser.objects.filter(role='client')
        self.fields['service_company'].queryset = CustomUser.objects.filter(role='service')

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = '__all__'
        labels = {
            'machine': 'Заводской №',
        }
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        
        if user:
            if getattr(user, 'is_manager', False) or user.is_superuser:
                pass
            elif getattr(user, 'is_service', False):
                self.fields['machine'].queryset = Machine.objects.filter(service_company=user)
            elif getattr(user, 'is_client', False):
                self.fields['machine'].queryset = Machine.objects.filter(client=user)
            else:
                self.fields['machine'].queryset = Machine.objects.none()
        
        if user:
            from apps.users.models import CustomUser
            if getattr(user, 'is_manager', False) or user.is_superuser:
                self.fields['service_company'].queryset = CustomUser.objects.filter(role='service')
            elif getattr(user, 'is_service', False):
                self.fields['service_company'].queryset = CustomUser.objects.filter(id=user.id)
            elif getattr(user, 'is_client', False):
                service_companies_ids = Machine.objects.filter(client=user).values_list('service_company_id', flat=True).distinct()
                self.fields['service_company'].queryset = CustomUser.objects.filter(
                    id__in=list(service_companies_ids) + [user.id]
                )
                
                # Переопределено отображение (label) для текущего пользователя (клиента)
                # Чтобы в списке вместо имени (например, "Клиент Иванов") отображалось "Самостоятельно"
                original_label_from_instance = self.fields['service_company'].label_from_instance

                def custom_label_from_instance(obj):
                    if obj.id == user.id:
                        return "Самостоятельно"
                    return original_label_from_instance(obj)

                self.fields['service_company'].label_from_instance = custom_label_from_instance
            else:
                self.fields['service_company'].queryset = CustomUser.objects.none()
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})
    
    def clean(self):
        cleaned_data = super().clean()
        machine = cleaned_data.get('machine')
        event_date = cleaned_data.get('event_date')
        service_type = cleaned_data.get('service_type')
        
        # Проверка на дубликаты (машина + дата + вид ТО)
        if machine and event_date and service_type:
            queryset = Maintenance.objects.filter(
                machine=machine,
                event_date=event_date,
                service_type=service_type
            )
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                self.add_error(None, 'Запись о ТО с такими параметрами (машина, дата, вид ТО) уже существует в системе.')
        
        return cleaned_data

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        exclude = ['downtime']
        labels = {
            'machine': 'Заводской №',
        }
        widgets = {
            'failure_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'recovery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        
        if user:
            if getattr(user, 'is_manager', False) or user.is_superuser:
                pass
            elif getattr(user, 'is_service', False):
                self.fields['machine'].queryset = Machine.objects.filter(service_company=user)
            elif getattr(user, 'is_client', False):
                self.fields['machine'].queryset = Machine.objects.filter(client=user)
            else:
                self.fields['machine'].queryset = Machine.objects.none()
        
        if user:
            from apps.users.models import CustomUser
            if getattr(user, 'is_manager', False) or user.is_superuser:
                 self.fields['service_company'].queryset = CustomUser.objects.filter(role='service')
            elif getattr(user, 'is_service', False):
                 self.fields['service_company'].queryset = CustomUser.objects.filter(id=user.id)
            elif getattr(user, 'is_client', False):
                 service_companies_ids = Machine.objects.filter(client=user).values_list('service_company_id', flat=True).distinct()
                 self.fields['service_company'].queryset = CustomUser.objects.filter(id__in=service_companies_ids)
            else:
                 self.fields['service_company'].queryset = CustomUser.objects.none()
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})
