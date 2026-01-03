from django.db import models
from django.conf import settings  # Ссылка на нашу кастомную модель User

# --- Абстрактный класс для Справочников (чтобы не дублировать код) ---
class BaseCatalog(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

# --- Справочники (см. Модель_данных.png и Машина_характеристики) ---
class TechniqueModel(BaseCatalog):
    class Meta:
        verbose_name = 'Модель техники'
        verbose_name_plural = 'Справочник: Модели техники'

class EngineModel(BaseCatalog):
    class Meta:
        verbose_name = 'Модель двигателя'
        verbose_name_plural = 'Справочник: Модели двигателей'

class TransmissionModel(BaseCatalog):
    class Meta:
        verbose_name = 'Модель трансмиссии'
        verbose_name_plural = 'Справочник: Модели трансмиссии'

class DriveAxleModel(BaseCatalog):
    class Meta:
        verbose_name = 'Модель ведущего моста'
        verbose_name_plural = 'Справочник: Модели ведущих мостов'

class SteeringAxleModel(BaseCatalog):
    class Meta:
        verbose_name = 'Модель управляемого моста'
        verbose_name_plural = 'Справочник: Модели управляемых мостов'

class ServiceType(BaseCatalog):
    class Meta:
        verbose_name = 'Вид ТО'
        verbose_name_plural = 'Справочник: Виды ТО'

class FailureNode(BaseCatalog):
    class Meta:
        verbose_name = 'Узел отказа'
        verbose_name_plural = 'Справочник: Узлы отказа'

class RecoveryMethod(BaseCatalog):
    class Meta:
        verbose_name = 'Способ восстановления'
        verbose_name_plural = 'Справочник: Способы восстановления'


# --- Основные сущности ---

class Machine(models.Model):
    # Данные из файла "Машина_характеристики_сущности.xlsx"
    serial_number = models.CharField(max_length=255, unique=True, verbose_name='Зав. № машины')
    technique_model = models.ForeignKey(TechniqueModel, on_delete=models.PROTECT, verbose_name='Модель техники')
    engine_model = models.ForeignKey(EngineModel, on_delete=models.PROTECT, verbose_name='Модель двигателя')
    engine_serial = models.CharField(max_length=255, verbose_name='Зав. № двигателя')
    transmission_model = models.ForeignKey(TransmissionModel, on_delete=models.PROTECT, verbose_name='Модель трансмиссии')
    transmission_serial = models.CharField(max_length=255, verbose_name='Зав. № трансмиссии')
    drive_axle_model = models.ForeignKey(DriveAxleModel, on_delete=models.PROTECT, verbose_name='Модель ведущего моста')
    drive_axle_serial = models.CharField(max_length=255, verbose_name='Зав. № ведущего моста')
    steering_axle_model = models.ForeignKey(SteeringAxleModel, on_delete=models.PROTECT, verbose_name='Модель управляемого моста')
    steering_axle_serial = models.CharField(max_length=255, verbose_name='Зав. № управляемого моста')
    
    supply_contract = models.CharField(max_length=255, blank=True, verbose_name='Договор поставки №, дата')
    date_shipment = models.DateField(verbose_name='Дата отгрузки с завода')
    consignee = models.CharField(max_length=255, verbose_name='Грузополучатель (конечный потребитель)')
    delivery_address = models.CharField(max_length=255, verbose_name='Адрес поставки (эксплуатации)')
    equipment = models.TextField(blank=True, verbose_name='Комплектация (доп. опции)')
    
    # Ссылки на пользователей
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='machines_client', verbose_name='Клиент')
    service_company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='machines_service', verbose_name='Сервисная компания')

    class Meta:
        verbose_name = 'Машина'
        verbose_name_plural = 'Машины'
        ordering = ['date_shipment']  # Сортировка по умолчанию

    def __str__(self):
        return f"{self.serial_number}"


class Maintenance(models.Model):
    # Данные из файла "ТО_характеристики_сущности.xlsx"
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='maintenances', verbose_name='Машина')
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT, verbose_name='Вид ТО')
    event_date = models.DateField(verbose_name='Дата проведения ТО')
    operating_hours = models.IntegerField(verbose_name='Наработка, м/час')
    order_number = models.CharField(max_length=255, verbose_name='№ заказ-наряда')
    order_date = models.DateField(verbose_name='Дата заказ-наряда')
    
    service_company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Организация, проводившая ТО')
    # В ТЗ есть поле "Организация, проводившая ТО" и "Сервисная компания". 
    # Часто это одно и то же, но по ТЗ это отдельные поля, хотя источник данных для обоих - справочник пользователей.
    # Реализуем как указано: исполнитель ТО.
    
    class Meta:
        verbose_name = 'Техническое обслуживание'
        verbose_name_plural = 'Технические обслуживания'
        ordering = ['event_date']  # Сортировка по умолчанию


class Complaint(models.Model):
    # Данные из файла "Рекламации_характеристики_сущности.xlsx"
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='complaints', verbose_name='Машина')
    failure_date = models.DateField(verbose_name='Дата отказа')
    operating_hours = models.IntegerField(verbose_name='Наработка, м/час')
    failure_node = models.ForeignKey(FailureNode, on_delete=models.PROTECT, verbose_name='Узел отказа')
    failure_description = models.TextField(verbose_name='Описание отказа')
    recovery_method = models.ForeignKey(RecoveryMethod, on_delete=models.PROTECT, verbose_name='Способ восстановления')
    spare_parts = models.TextField(blank=True, verbose_name='Используемые запасные части')
    recovery_date = models.DateField(verbose_name='Дата восстановления')
    
    # Время простоя - расчетное поле, но часто хранят в БД для фильтрации.
    # Можно реализовать как property модели или переопределить save(). Сделаем пока поле.
    downtime = models.IntegerField(verbose_name='Время простоя техники (дни)', blank=True, null=True)

    service_company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Сервисная компания')

    class Meta:
        verbose_name = 'Рекламация'
        verbose_name_plural = 'Рекламации'
        ordering = ['failure_date']  # Сортировка по умолчанию
    
    def save(self, *args, **kwargs):
        # Автоматический расчет времени простоя
        if self.recovery_date and self.failure_date:
            delta = self.recovery_date - self.failure_date
            self.downtime = delta.days
        super().save(*args, **kwargs)