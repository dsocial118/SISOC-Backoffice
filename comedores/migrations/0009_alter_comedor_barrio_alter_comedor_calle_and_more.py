# Generated by Django 4.2.16 on 2025-01-02 14:05

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("configuraciones", "0004_provincia_alter_localidad_options_and_more"),
        ("comedores", "0008_alter_espaciococina_abastecimiento_combustible"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comedor",
            name="barrio",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="comedor",
            name="calle",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="comedor",
            name="codigo_postal",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1000),
                    django.core.validators.MaxValueValidator(999999),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="comedor",
            name="comienzo",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1900),
                    django.core.validators.MaxValueValidator(2025),
                ],
                verbose_name="Año en el que comenzó a funcionar",
            ),
        ),
        migrations.AlterField(
            model_name="comedor",
            name="localidad",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="configuraciones.localidad",
            ),
        ),
        migrations.AlterField(
            model_name="comedor",
            name="municipio",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="configuraciones.municipio",
            ),
        ),
        migrations.AlterField(
            model_name="comedor",
            name="numero",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="comedor",
            name="partido",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="referente",
            name="apellido",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="Apellido del referente",
            ),
        ),
        migrations.AlterField(
            model_name="referente",
            name="celular",
            field=models.BigIntegerField(
                blank=True, null=True, verbose_name="Celular del referente"
            ),
        ),
        migrations.AlterField(
            model_name="referente",
            name="documento",
            field=models.BigIntegerField(
                blank=True, null=True, verbose_name="Documento del referente"
            ),
        ),
        migrations.AlterField(
            model_name="referente",
            name="mail",
            field=models.EmailField(
                blank=True, max_length=254, null=True, verbose_name="Mail del referente"
            ),
        ),
        migrations.AlterField(
            model_name="referente",
            name="nombre",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="Nombre del referente",
            ),
        ),
    ]
