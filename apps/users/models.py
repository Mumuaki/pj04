from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Роли пользователей
    CLIENT = 'client'
    SERVICE = 'service'
    MANAGER = 'manager'
    
    ROLE_CHOICES = (
        (CLIENT, 'Клиент'),
        (SERVICE, 'Сервисная организация'),
        (MANAGER, 'Менеджер'),
    )
    
    role = models.CharField(
        max_length=15, 
        choices=ROLE_CHOICES, 
        default=CLIENT, 
        verbose_name='Роль'
    )
    # Имя сервисной организации или клиента (если нужно отличающееся от username)
    name = models.CharField(max_length=255, blank=True, verbose_name='Имя / Название организации')

    def __str__(self):
        return self.name if self.name else self.username

    @property
    def is_manager(self):
        return self.role == self.MANAGER

    @property
    def is_service(self):
        return self.role == self.SERVICE

    @property
    def is_client(self):
        return self.role == self.CLIENT
