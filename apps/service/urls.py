from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ComplaintCreateView,
    ComplaintDeleteView,
    ComplaintDetailView,
    ComplaintUpdateView,
    ComplaintViewSet,
    IndexView,
    MachineCreateView,
    MachineDetailView,
    MachineViewSet,
    MaintenanceCreateView,
    MaintenanceDeleteView,
    MaintenanceDetailView,
    MaintenanceUpdateView,
    MaintenanceViewSet,
)

router = DefaultRouter()
router.register(r'machines', MachineViewSet)
router.register(r'maintenances', MaintenanceViewSet)
router.register(r'complaints', ComplaintViewSet)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('create/machine/', MachineCreateView.as_view(), name='machine_create'),
    path('create/maintenance/', MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('create/complaint/', ComplaintCreateView.as_view(), name='complaint_create'),
    path('machine/<int:pk>/', MachineDetailView.as_view(), name='machine_detail'),
    path('maintenance/<int:pk>/', MaintenanceDetailView.as_view(), name='maintenance_detail'),
    path('maintenance/<int:pk>/update/', MaintenanceUpdateView.as_view(), name='maintenance_update'),
    path('maintenance/<int:pk>/delete/', MaintenanceDeleteView.as_view(), name='maintenance_delete'),
    path('complaint/<int:pk>/', ComplaintDetailView.as_view(), name='complaint_detail'),
    path('complaint/<int:pk>/update/', ComplaintUpdateView.as_view(), name='complaint_update'),
    path('complaint/<int:pk>/delete/', ComplaintDeleteView.as_view(), name='complaint_delete'),
    path('api/', include(router.urls)),
]
