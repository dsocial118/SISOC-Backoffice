# Generated by Django 4.0.2 on 2024-11-07 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legajos', '0009_accion_actividadrealizada_agua_aportesjubilacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vinculofamiliar',
            name='inverso',
            field=models.CharField(default='-', max_length=255),
            preserve_default=False,
        ),
    ]
