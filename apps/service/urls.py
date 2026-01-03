from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MachineViewSet, MaintenanceViewSet, ComplaintViewSet

router = DefaultRouter()
router.register(r'machines', MachineViewSet)
router.register(r'maintenances', MaintenanceViewSet)
router.register(r'complaints', ComplaintViewSet)

urlpatterns = [
    path('', include(router.urls)),
]