# Generated by Django 4.2.16 on 2024-12-19 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("comedores", "0004_estadosintervencion_tipointervencion_valorcomida_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Territorial",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "gestionar_uid",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("nombre", models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name="relevamiento",
            name="relevador",
        ),
        migrations.AddField(
            model_name="relevamiento",
            name="estado",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="relevamiento",
            name="colaboradores",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="comedores.colaboradores",
            ),
        ),
        migrations.AlterField(
            model_name="relevamiento",
            name="compras",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="comedores.fuentecompras",
            ),
        ),
        migrations.AlterField(
            model_name="relevamiento",
            name="espacio",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="comedores.espacio",
            ),
        ),
        migrations.AlterField(
            model_name="relevamiento",
            name="fecha_visita",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="relevamiento",
            name="funcionamiento",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="comedores.funcionamientoprestacion",
            ),
        ),
        migrations.AlterField(
            model_name="relevamiento",
            name="prestacion",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="comedores.prestacion",
            ),
        ),
        migrations.AlterField(
            model_name="relevamiento",
            name="recursos",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="comedores.fuenterecursos",
            ),
        ),
        migrations.AddField(
            model_name="relevamiento",
            name="territorial",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="comedores.territorial",
            ),
        ),
    ]