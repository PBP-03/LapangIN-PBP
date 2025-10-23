# Generated migration to add deskripsi, gambar, alasan_penolakan to Mitra
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_alter_mitra_nama_alter_mitra_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='mitra',
            name='deskripsi',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mitra',
            name='gambar',
            field=models.ImageField(upload_to='mitra_gambar/', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mitra',
            name='alasan_penolakan',
            field=models.TextField(blank=True, null=True),
        ),
    ]
