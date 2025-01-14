# Generated by Django 4.2.16 on 2025-01-13 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comedores", "0012_nomina_fk_sexo"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tipodecomedor",
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
                ("nombre", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name": "Tipodecomedor",
                "verbose_name_plural": "Tipodecomedor",
                "ordering": ["id"],
            },
        ),
    ]
