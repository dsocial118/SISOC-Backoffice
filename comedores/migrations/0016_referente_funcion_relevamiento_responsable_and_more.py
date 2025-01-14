# Generated by Django 4.2.16 on 2025-01-10 15:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("comedores", "0015_alter_espaciococina_abastecimiento_combustible"),
    ]

    operations = [
        migrations.AddField(
            model_name="referente",
            name="funcion",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="Funcion del referente",
            ),
        ),
        migrations.AddField(
            model_name="relevamiento",
            name="responsable",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="comedores.referente",
            ),
        ),
        migrations.AddField(
            model_name="relevamiento",
            name="responsable_es_referente",
            field=models.BooleanField(default=False),
        ),
    ]
