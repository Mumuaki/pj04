from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MachineViewSet, MaintenanceViewSet, ComplaintViewSet,
    IndexView, MachineDetailView, MaintenanceDetailView, ComplaintDetailView, 
    MachineCreateView, MaintenanceCreateView, ComplaintCreateView
)

# Настройка роутера для API 
router = DefaultRouter()
router.register(r'machines', MachineViewSet)
router.register(r'maintenances', MaintenanceViewSet)
router.register(r'complaints', ComplaintViewSet)

urlpatterns = [
    # 1. Frontend: Главная страница
    path('', IndexView.as_view(), name='index'),

    # 2. Frontend: Создание записей (должно быть ПЕРЕД детальными страницами)
    path('create/machine/', MachineCreateView.as_view(), name='machine_create'),
    path('create/maintenance/', MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('create/complaint/', ComplaintCreateView.as_view(), name='complaint_create'),

    # 3. Frontend: Детальные страницы
    path('machine/<int:pk>/', MachineDetailView.as_view(), name='machine_detail'),
    path('maintenance/<int:pk>/', MaintenanceDetailView.as_view(), name='maintenance_detail'),
    path('complaint/<int:pk>/', ComplaintDetailView.as_view(), name='complaint_detail'),

    # 4. API: Выносим API под префикс 'api/', чтобы не мешал фронтенду
    path('api/', include(router.urls)), 
]
