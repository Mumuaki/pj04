from django.contrib import admin
from apps.users.models import CustomUser
from .models import (
    TechniqueModel, EngineModel, TransmissionModel, DriveAxleModel, 
    SteeringAxleModel, ServiceType, FailureNode, RecoveryMethod,
    Machine, Maintenance, Complaint
)

# --- Справочники ---
admin.site.register(TechniqueModel)
admin.site.register(EngineModel)
admin.site.register(TransmissionModel)
admin.site.register(DriveAxleModel)
admin.site.register(SteeringAxleModel)
admin.site.register(ServiceType)
admin.site.register(FailureNode)
admin.site.register(RecoveryMethod)

# --- Основные сущности ---

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'technique_model', 'engine_model', 'client', 'service_company', 'formatted_date_shipment')
    list_display_links = ('serial_number',)
    list_filter = (
        'technique_model', 
        'engine_model', 
        'transmission_model', 
        'drive_axle_model', 
        'steering_axle_model',
        'client',
        'service_company'
    )
    
    search_fields = ('serial_number',)
    
    def formatted_date_shipment(self, obj):
        return obj.date_shipment.strftime('%d-%m-%Y') if obj.date_shipment else '-'
    formatted_date_shipment.short_description = 'Дата отгрузки'
    formatted_date_shipment.admin_order_field = 'date_shipment'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "client":
            kwargs["queryset"] = CustomUser.objects.filter(role='client')
        if db_field.name == "service_company":
            kwargs["queryset"] = CustomUser.objects.filter(role='service')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('machine', 'service_type', 'formatted_event_date', 'operating_hours', 'service_company', 'formatted_order_date')
    list_filter = ('service_type', 'machine', 'service_company')
    search_fields = ('order_number', 'machine__serial_number') 
    
    
    def formatted_event_date(self, obj):
        return obj.event_date.strftime('%d-%m-%Y') if obj.event_date else '-'
    formatted_event_date.short_description = 'Дата проведения ТО'
    formatted_event_date.admin_order_field = 'event_date'
    
    def formatted_order_date(self, obj):
        return obj.order_date.strftime('%d-%m-%Y') if obj.order_date else '-'
    formatted_order_date.short_description = 'Дата заказ-наряда'
    formatted_order_date.admin_order_field = 'order_date'


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('machine', 'failure_node', 'formatted_failure_date', 'formatted_recovery_date', 'downtime', 'service_company')
    list_filter = ('failure_node', 'recovery_method', 'service_company')
    search_fields = ('machine__serial_number',)
    
    def formatted_failure_date(self, obj):
        return obj.failure_date.strftime('%d-%m-%Y') if obj.failure_date else '-'
    formatted_failure_date.short_description = 'Дата отказа'
    formatted_failure_date.admin_order_field = 'failure_date'
    
    def formatted_recovery_date(self, obj):
        return obj.recovery_date.strftime('%d-%m-%Y') if obj.recovery_date else '-'
    formatted_recovery_date.short_description = 'Дата восстановления'
    formatted_recovery_date.admin_order_field = 'recovery_date'
