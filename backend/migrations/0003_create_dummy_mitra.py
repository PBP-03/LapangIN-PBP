from django.db import migrations


def create_dummy_mitras(apps, schema_editor):
    Mitra = apps.get_model('backend', 'Mitra')
    Mitra.objects.create(nama='Mitra A', email='mitra.a@example.com', status='pending')
    Mitra.objects.create(nama='Mitra B', email='mitra.b@example.com', status='pending')
    Mitra.objects.create(nama='Mitra C', email='mitra.c@example.com', status='approved')


def reverse_func(apps, schema_editor):
    Mitra = apps.get_model('backend', 'Mitra')
    Mitra.objects.filter(email__in=['mitra.a@example.com', 'mitra.b@example.com', 'mitra.c@example.com']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_mitra'),
    ]

    operations = [
        migrations.RunPython(create_dummy_mitras, reverse_func),
    ]
