# Generated by Django 4.0.2 on 2024-10-31 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('legajos', '0009_accion_actividadrealizada_agua_aportesjubilacion_and_more'),
        ('usuarios', '0003_rol_usuarios_rol'),
    ]

    operations = [
        migrations.CreateModel(
            name='CanalesVentas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Canal de Ventas',
                'verbose_name_plural': 'Canales de Ventas',
            },
        ),
        migrations.CreateModel(
            name='CantidadClientes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Cantidad de Clientes',
                'verbose_name_plural': 'Cantidades de Clientes',
            },
        ),
        migrations.CreateModel(
            name='CantidadCompetidores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Cantidad de Competidores',
                'verbose_name_plural': 'Cantidades de Competidores',
            },
        ),
        migrations.CreateModel(
            name='CantidadIntegrantes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Cantidad de Integrantes',
                'verbose_name_plural': 'Cantidades de Integrantes',
            },
        ),
        migrations.CreateModel(
            name='Comprador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Comprador',
                'verbose_name_plural': 'Compradores',
            },
        ),
        migrations.CreateModel(
            name='CondicionOcupacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Condición de Ocupación',
                'verbose_name_plural': 'Condiciones de Ocupación',
            },
        ),
        migrations.CreateModel(
            name='ConocimientoCompetidores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Conocimiento de Competidores',
                'verbose_name_plural': 'Conocimientos de Competidores',
            },
        ),
        migrations.CreateModel(
            name='DestinoMaterialesRecuperados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Destino de Materiales Recuperados',
                'verbose_name_plural': 'Destinos de Materiales Recuperados',
            },
        ),
        migrations.CreateModel(
            name='EstudiosAlcanzados',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Estudios Alcanzados',
                'verbose_name_plural': 'Estudios Alcanzados',
            },
        ),
        migrations.CreateModel(
            name='FijacionPrecios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Fijación de Precios',
                'verbose_name_plural': 'Fijaciones de Precios',
            },
        ),
        migrations.CreateModel(
            name='Genero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Género',
                'verbose_name_plural': 'Géneros',
            },
        ),
        migrations.CreateModel(
            name='IngresoPromedioFamiliar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Ingreso Promedio Familiar',
                'verbose_name_plural': 'Ingresos Promedio Familiar',
            },
        ),
        migrations.CreateModel(
            name='InteractuaCompetidores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Interacción con Competidores',
                'verbose_name_plural': 'Interacciones con Competidores',
            },
        ),
        migrations.CreateModel(
            name='LineaDeAccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('produccion_apoyo_tecnico', models.BooleanField(default=False)),
                ('produccion_maquinaria', models.BooleanField(default=False)),
                ('produccion_tecnologias', models.BooleanField(default=False)),
                ('produccion_entrega', models.BooleanField(default=False)),
                ('comercializacion_fortalecimiento_institucional', models.BooleanField(default=False)),
                ('comercializacion_apoyo_tecnologico', models.BooleanField(default=False)),
                ('comercializacion_habilidades_blandas', models.BooleanField(default=False)),
                ('comercializacion_desarrollo_local', models.BooleanField(default=False)),
                ('comercializacion_fortalecimiento_unidades', models.BooleanField(default=False)),
                ('circular_fortalecimiento', models.BooleanField(default=False)),
                ('circular_practicas_sostenibles', models.BooleanField(default=False)),
                ('circular_materiales_reciclados', models.BooleanField(default=False)),
                ('circular_reduccion_residuos', models.BooleanField(default=False)),
                ('fundamentacion', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='LugarComercializacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Lugar de Comercialización',
                'verbose_name_plural': 'Lugares de Comercialización',
            },
        ),
        migrations.CreateModel(
            name='MedioPlanificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Medio de Planificación',
                'verbose_name_plural': 'Medios de Planificación',
            },
        ),
        migrations.CreateModel(
            name='ModalidadCicloProductivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Modalidad de Ciclo Productivo',
                'verbose_name_plural': 'Modalidades de Ciclo Productivo',
            },
        ),
        migrations.CreateModel(
            name='ModalidadComercializacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Modalidad de Comercialización',
                'verbose_name_plural': 'Modalidades de Comercialización',
            },
        ),
        migrations.CreateModel(
            name='ModalidadCompras',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Modalidad de Compras',
                'verbose_name_plural': 'Modalidades de Compras',
            },
        ),
        migrations.CreateModel(
            name='Objetivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Objetivo',
                'verbose_name_plural': 'Objetivos',
            },
        ),
        migrations.CreateModel(
            name='OcupacionHorasSemanales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Ocupación Horas Semanales',
                'verbose_name_plural': 'Ocupaciones Horas Semanales',
            },
        ),
        migrations.CreateModel(
            name='PlataformaComunicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Plataforma de Comunicación',
                'verbose_name_plural': 'Plataformas de Comunicación',
            },
        ),
        migrations.CreateModel(
            name='PlazoCompraCredito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Plazo de Compra a Crédito',
                'verbose_name_plural': 'Plazos de Compra a Crédito',
            },
        ),
        migrations.CreateModel(
            name='RedSocial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Red Social',
                'verbose_name_plural': 'Redes Sociales',
            },
        ),
        migrations.CreateModel(
            name='Rubro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Rubro',
                'verbose_name_plural': 'Rubros',
            },
        ),
        migrations.CreateModel(
            name='TipoActividad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Tipo de Actividad',
                'verbose_name_plural': 'Tipos de Actividad',
            },
        ),
        migrations.CreateModel(
            name='TipoComunidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Tipo de Comunidad',
                'verbose_name_plural': 'Tipos de Comunidad',
            },
        ),
        migrations.CreateModel(
            name='TipoDispositivosMoviles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Tipo de Dispositivos Móviles',
                'verbose_name_plural': 'Tipos de Dispositivos Móviles',
            },
        ),
        migrations.CreateModel(
            name='TipoInmueble',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Tipo de Inmueble',
                'verbose_name_plural': 'Tipos de Inmueble',
            },
        ),
        migrations.CreateModel(
            name='TipoInternet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Tipo de Internet',
                'verbose_name_plural': 'Tipos de Internet',
            },
        ),
        migrations.CreateModel(
            name='TipoOcupacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Tipo de Ocupación',
                'verbose_name_plural': 'Tipos de Ocupación',
            },
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('estado', models.CharField(blank=True, default='Pendiente', max_length=255)),
                ('tipo_anexo', models.CharField(choices=[('SOCIO_PRODUCTIVO', 'Socio Productivo'), ('FORMACION', 'Formación')], max_length=255)),
                ('creador', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='creador', to='usuarios.usuarios')),
                ('modificador', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modificador', to='usuarios.usuarios')),
            ],
        ),
        migrations.CreateModel(
            name='Presupuesto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_actividad', models.CharField(max_length=255)),
                ('tipo_producto', models.CharField(max_length=255)),
                ('nombre_producto', models.CharField(max_length=255)),
                ('cantidad_producto', models.PositiveBigIntegerField()),
                ('costo_unitario', models.PositiveBigIntegerField()),
                ('destinatarios_indirectos', models.PositiveBigIntegerField()),
                ('linea_de_accion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.lineadeaccion')),
            ],
        ),
        migrations.CreateModel(
            name='PersoneriaPersona',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.CharField(max_length=255)),
                ('localidad', models.CharField(max_length=255)),
                ('codigo_postal', models.PositiveBigIntegerField()),
                ('proyecto_nombre', models.CharField(max_length=255)),
                ('proyecto_costo', models.PositiveBigIntegerField()),
                ('pertenece_comunidad_indigena', models.BooleanField(default=False)),
                ('comunidad_indigena', models.CharField(blank=True, max_length=255, null=True)),
                ('nobre_completo', models.CharField(max_length=255)),
                ('dni', models.PositiveBigIntegerField()),
                ('fecha_nacimiento', models.DateField()),
                ('cuil', models.PositiveBigIntegerField()),
                ('domicilio_real', models.CharField(max_length=255)),
                ('mail', models.EmailField(max_length=254)),
                ('telefono', models.PositiveBigIntegerField()),
                ('provincia', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='legajos.legajoprovincias')),
                ('proyecto_objetivo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.objetivo')),
                ('proyecto_rubro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.rubro')),
                ('proyecto_tipo_actividad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='persona_tipo_actividad', to='provincias.tipoactividad')),
            ],
            options={
                'verbose_name': 'Persona',
                'verbose_name_plural': 'Personas',
            },
        ),
        migrations.CreateModel(
            name='PersoneriaOrganizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.CharField(max_length=255)),
                ('localidad', models.CharField(max_length=255)),
                ('codigo_postal', models.PositiveBigIntegerField()),
                ('proyecto_nombre', models.CharField(max_length=255)),
                ('proyecto_costo', models.PositiveBigIntegerField()),
                ('pertenece_comunidad_indigena', models.BooleanField(default=False)),
                ('comunidad_indigena', models.CharField(blank=True, max_length=255, null=True)),
                ('nombre', models.CharField(max_length=255)),
                ('tipo', models.CharField(max_length=255)),
                ('fecha_creacion', models.DateField()),
                ('numero_personeria_juridica', models.CharField(max_length=255)),
                ('fecha_otorgamiento', models.DateField()),
                ('cuit', models.PositiveBigIntegerField()),
                ('domicilio_legal', models.CharField(max_length=255)),
                ('mail', models.EmailField(max_length=254)),
                ('telefono', models.PositiveBigIntegerField()),
                ('autoridad_nombre_completo', models.CharField(max_length=255)),
                ('autoridad_dni', models.PositiveBigIntegerField()),
                ('autoridad_cuit', models.PositiveBigIntegerField()),
                ('autoridad_rol', models.CharField(max_length=255)),
                ('practicas_regenerativas', models.BooleanField(default=False)),
                ('provincia', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='legajos.legajoprovincias')),
                ('proyecto_objetivo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.objetivo')),
                ('proyecto_rubro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.rubro')),
                ('proyecto_tipo_actividad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='organizacion_tipo_actividad', to='provincias.tipoactividad')),
            ],
            options={
                'verbose_name': 'Organización',
                'verbose_name_plural': 'Organizaciones',
            },
        ),
        migrations.CreateModel(
            name='Observacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observacion', models.TextField()),
                ('proyecto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='provincias.proyecto')),
            ],
            options={
                'verbose_name': 'Observación',
                'verbose_name_plural': 'Observaciones',
            },
        ),
        migrations.CreateModel(
            name='DiagnosticoPersona',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banco', models.BooleanField(default=False)),
                ('banco_nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('cuenta_digital', models.BooleanField(default=False)),
                ('financiamiento', models.BooleanField(default=False)),
                ('financiamiento_nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('ingresos_mensuales', models.PositiveBigIntegerField()),
                ('egresos_mensuales', models.PositiveBigIntegerField()),
                ('ganancias_mensuales', models.PositiveBigIntegerField()),
                ('internet', models.BooleanField(default=False)),
                ('dispositivos_conectados', models.PositiveBigIntegerField()),
                ('computadora', models.BooleanField(default=False)),
                ('redes_sociales', models.BooleanField(default=False)),
                ('ventas_destinadas_turismo', models.BooleanField(default=False)),
                ('recicladores_urbanos', models.BooleanField(default=False)),
                ('recicladores_equipados', models.BooleanField(default=False)),
                ('clasificacion_residuos', models.BooleanField(default=False)),
                ('optimizacion_recursos', models.BooleanField(default=False)),
                ('financiamiento_sostenible', models.BooleanField(default=False)),
                ('estrategia_comercializacion', models.BooleanField(default=False)),
                ('tecnologias_mejorar_eficiencia', models.BooleanField(default=False)),
                ('tecnologias_cuales', models.CharField(max_length=255)),
                ('ocupacion_sosten_hogar', models.BooleanField(default=False)),
                ('beneficiario_social', models.BooleanField(default=False)),
                ('beneficio_social', models.CharField(max_length=255)),
                ('familia_adultos', models.PositiveBigIntegerField()),
                ('familia_menores', models.PositiveBigIntegerField()),
                ('canales_ventas', models.ManyToManyField(to='provincias.CanalesVentas')),
                ('cantidad_clientes', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.cantidadclientes')),
                ('cantidad_competidores', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.cantidadcompetidores')),
                ('comprador', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.comprador')),
                ('conocimiento_competidores', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.conocimientocompetidores')),
                ('destino_materiales_recuperados', models.ManyToManyField(to='provincias.DestinoMaterialesRecuperados')),
                ('estudios_alcanzados', models.ManyToManyField(to='provincias.EstudiosAlcanzados')),
                ('familia_ingreso_promedio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.ingresopromediofamiliar')),
                ('fijacion_precios', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.fijacionprecios')),
                ('interactua_compentidores', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.interactuacompetidores')),
                ('lugar_comercializacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.lugarcomercializacion')),
                ('medio_planificacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.medioplanificacion')),
                ('modalidad_ciclo_productivo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.modalidadcicloproductivo')),
                ('modalidad_comercializacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.modalidadcomercializacion')),
                ('modalidad_compras', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.modalidadcompras')),
                ('ocupacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.tipoocupacion')),
                ('ocupacion_condicion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.condicionocupacion')),
                ('ocupacion_horas_semanales', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.ocupacionhorassemanales')),
                ('plataforma_comunicacion', models.ManyToManyField(to='provincias.PlataformaComunicacion')),
                ('plazo_compra_credito', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.plazocompracredito')),
                ('redes_sociales_cuales', models.ManyToManyField(to='provincias.RedSocial')),
                ('rubro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.rubro')),
                ('tipo_actividad', models.ManyToManyField(to='provincias.TipoActividad')),
                ('tipo_dispositivos_moviles', models.ManyToManyField(to='provincias.TipoDispositivosMoviles')),
                ('tipo_inmueble', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.tipoinmueble')),
                ('tipo_internet', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.tipointernet')),
            ],
            options={
                'verbose_name': 'Diagnóstico de Persona',
                'verbose_name_plural': 'Diagnósticos de Personas',
            },
        ),
        migrations.CreateModel(
            name='DiagnosticoOrganizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banco', models.BooleanField(default=False)),
                ('banco_nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('cuenta_digital', models.BooleanField(default=False)),
                ('financiamiento', models.BooleanField(default=False)),
                ('financiamiento_nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('ingresos_mensuales', models.PositiveBigIntegerField()),
                ('egresos_mensuales', models.PositiveBigIntegerField()),
                ('ganancias_mensuales', models.PositiveBigIntegerField()),
                ('internet', models.BooleanField(default=False)),
                ('dispositivos_conectados', models.PositiveBigIntegerField()),
                ('computadora', models.BooleanField(default=False)),
                ('redes_sociales', models.BooleanField(default=False)),
                ('ventas_destinadas_turismo', models.BooleanField(default=False)),
                ('recicladores_urbanos', models.BooleanField(default=False)),
                ('recicladores_equipados', models.BooleanField(default=False)),
                ('clasificacion_residuos', models.BooleanField(default=False)),
                ('optimizacion_recursos', models.BooleanField(default=False)),
                ('financiamiento_sostenible', models.BooleanField(default=False)),
                ('estrategia_comercializacion', models.BooleanField(default=False)),
                ('tecnologias_mejorar_eficiencia', models.BooleanField(default=False)),
                ('tecnologias_cuales', models.CharField(max_length=255)),
                ('mision_vision', models.TextField()),
                ('composicion_equipo', models.CharField(max_length=255)),
                ('directorio', models.BooleanField(default=False)),
                ('personal_tecnico', models.BooleanField(default=False)),
                ('personal_especializado', models.BooleanField(default=False)),
                ('canales_ventas', models.ManyToManyField(to='provincias.CanalesVentas')),
                ('cantidad_clientes', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.cantidadclientes')),
                ('cantidad_competidores', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.cantidadcompetidores')),
                ('cantidad_integrantes', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.cantidadintegrantes')),
                ('comprador', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.comprador')),
                ('conocimiento_competidores', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.conocimientocompetidores')),
                ('destino_materiales_recuperados', models.ManyToManyField(to='provincias.DestinoMaterialesRecuperados')),
                ('fijacion_precios', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.fijacionprecios')),
                ('genero_mayoria', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.genero')),
                ('interactua_compentidores', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.interactuacompetidores')),
                ('lugar_comercializacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.lugarcomercializacion')),
                ('medio_planificacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.medioplanificacion')),
                ('modalidad_ciclo_productivo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.modalidadcicloproductivo')),
                ('modalidad_comercializacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.modalidadcomercializacion')),
                ('modalidad_compras', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.modalidadcompras')),
                ('plataforma_comunicacion', models.ManyToManyField(to='provincias.PlataformaComunicacion')),
                ('plazo_compra_credito', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.plazocompracredito')),
                ('redes_sociales_cuales', models.ManyToManyField(to='provincias.RedSocial')),
                ('rubro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.rubro')),
                ('tipo_actividad', models.ManyToManyField(to='provincias.TipoActividad')),
                ('tipo_comunidad', models.ManyToManyField(to='provincias.TipoComunidad')),
                ('tipo_dispositivos_moviles', models.ManyToManyField(to='provincias.TipoDispositivosMoviles')),
                ('tipo_inmueble', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.tipoinmueble')),
                ('tipo_internet', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.tipointernet')),
            ],
            options={
                'verbose_name': 'Diagnóstico de Organización',
                'verbose_name_plural': 'Diagnósticos de Organizaciones',
            },
        ),
        migrations.CreateModel(
            name='DestinatarioDirecto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('apellido', models.CharField(max_length=255)),
                ('dni', models.PositiveBigIntegerField()),
                ('linea_de_accion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destinatarios', to='provincias.lineadeaccion')),
            ],
        ),
        migrations.CreateModel(
            name='AnexoSocioProductivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('personeria', models.CharField(choices=[('ORGANIZACION', 'Organización'), ('PERSONA', 'Persona')], max_length=255)),
                ('media', models.FileField(upload_to='anexos/socioproductivos/')),
                ('documentacion', models.FileField(upload_to='anexos/socioproductivos/')),
                ('diagnostico_organizacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.diagnosticoorganizacion')),
                ('diagnostico_persona', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.diagnosticopersona')),
                ('linea_de_accion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.lineadeaccion')),
                ('organizacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.personeriaorganizacion')),
                ('persona', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='provincias.personeriapersona')),
                ('proyecto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='provincias.proyecto')),
            ],
            options={
                'verbose_name': 'Anexo socio productivo',
                'verbose_name_plural': 'Anexos socio productivo',
            },
        ),
        migrations.CreateModel(
            name='AnexoFormacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proyecto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='provincias.proyecto')),
            ],
        ),
    ]
