# Generated by Django 4.2.16 on 2025-01-06 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comedores", "0010_nomina"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="nomina",
            options={
                "ordering": ["-fecha"],
                "verbose_name": "Nomina",
                "verbose_name_plural": "Nominas",
            },
        ),
        migrations.RemoveField(
            model_name="nomina",
            name="fk_subintervencion",
        ),
        migrations.RemoveField(
            model_name="nomina",
            name="fk_tipo_intervencion",
        ),
        migrations.AddField(
            model_name="nomina",
            name="apellido",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="observacion",
            name="gestionar_uid",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="nomina",
            name="dni",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="nomina",
            name="nombre",
            field=models.TextField(blank=True, null=True),
        ),
    ]
