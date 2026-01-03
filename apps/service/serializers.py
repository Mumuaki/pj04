from rest_framework import serializers
from .models import Machine, Maintenance, Complaint

class MachineSerializer(serializers.ModelSerializer):
    # Для отображения названий справочников вместо ID можно использовать StringRelatedField
    # или оставить ID, если фронтенд будет сам мапить данные.
    # Пока сделаем базовый вариант с ID для простоты записи данных.
    
    class Meta:
        model = Machine
        fields = '__all__'  # Отдаем все поля

class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = '__all__'

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = '__all__'