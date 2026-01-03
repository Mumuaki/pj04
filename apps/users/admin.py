from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Поля, которые видны в списке пользователей
    list_display = ['username', 'email', 'role', 'name', 'is_staff']
    
    # Добавляем поле role и name в форму редактирования пользователя
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'name')}),
    )
    
    # Добавляем эти же поля в форму создания пользователя
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'name')}),
    )
    
    list_filter = ('role', 'is_staff', 'is_active')
