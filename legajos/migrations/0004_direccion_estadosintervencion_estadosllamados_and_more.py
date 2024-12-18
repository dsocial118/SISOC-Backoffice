# Generated by Django 4.0.2 on 2024-09-20 18:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('legajos', '0003_alter_dimensioneducacion_localidadinstitucion_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Direccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='EstadosIntervencion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'EstadosIntervencion',
                'verbose_name_plural': 'EstadosIntervenciones',
            },
        ),
        migrations.CreateModel(
            name='EstadosLlamados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'EstadoLlamado',
                'verbose_name_plural': 'EstadosLlamados',
            },
        ),
        migrations.CreateModel(
            name='TipoIntervencion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'TipoIntervencion',
                'verbose_name_plural': 'TiposIntervencion',
            },
        ),
        migrations.CreateModel(
            name='TipoLlamado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'TipoLlamado',
                'verbose_name_plural': 'TiposLammado',
            },
        ),
        migrations.CreateModel(
            name='SubTipoLlamado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('fk_tipo_llamado', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='legajos.tipollamado')),
            ],
            options={
                'verbose_name': 'SubTipoLlamado',
                'verbose_name_plural': 'SubTiposLlamado',
            },
        ),
        migrations.CreateModel(
            name='SubIntervencion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('fk_subintervencion', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='legajos.tipointervencion')),
            ],
            options={
                'verbose_name': 'SubIntervencion',
                'verbose_name_plural': 'SubIntervenciones',
            },
        ),
        migrations.CreateModel(
            name='Llamado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('observaciones', models.CharField(max_length=500)),
                ('fk_estado', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='legajos.estadosllamados')),
                ('fk_legajo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='legajos.legajos')),
                ('fk_subtipollamado', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='legajos.subtipollamado')),
                ('fk_tipo_llamado', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='legajos.tipollamado')),
                ('fk_usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Llamado',
                'verbose_name_plural': 'Llamados',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Intervencion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('fk_direccion', models.ManyToManyField(to='legajos.Direccion')),
                ('fk_estado', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='legajos.estadosintervencion')),
                ('fk_legajo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='legajos.legajos')),
                ('fk_subintervencion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='legajos.subintervencion')),
                ('fk_tipo_intervencion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='legajos.tipointervencion')),
                ('fk_usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Intervencion',
                'verbose_name_plural': 'Intervenciones',
                'ordering': ['-fecha'],
            },
        ),
        migrations.AddIndex(
            model_name='llamado',
            index=models.Index(fields=['fk_legajo'], name='legajos_lla_fk_lega_5a5e8f_idx'),
        ),
        migrations.AddIndex(
            model_name='intervencion',
            index=models.Index(fields=['fk_legajo'], name='legajos_int_fk_lega_41fc5f_idx'),
        ),
    ]
