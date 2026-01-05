import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.service.models import FailureNode, RecoveryMethod

print("=" * 50)
print("УЗЛЫ ОТКАЗА (FailureNode)")
print("=" * 50)
nodes = FailureNode.objects.all()
if nodes:
    for node in nodes:
        print(f"ID: {node.id:2d} | Название: {node.name}")
else:
    print("Нет данных")

print("\n" + "=" * 50)
print("СПОСОБЫ ВОССТАНОВЛЕНИЯ (RecoveryMethod)")
print("=" * 50)
methods = RecoveryMethod.objects.all()
if methods:
    for method in methods:
        print(f"ID: {method.id:2d} | Название: {method.name}")
else:
    print("Нет данных")

print("\n" + "=" * 50)
print(f"Всего узлов отказа: {nodes.count()}")
print(f"Всего способов восстановления: {methods.count()}")
print("=" * 50)
