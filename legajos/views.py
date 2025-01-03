import calendar  # pylint: disable=too-many-lines
import json

# Configurar el locale para usar el idioma español
import locale
import logging
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models, transaction
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from configuraciones.models import (
    Alertas,
    CategoriaAlertas,
    Circuito,
    Dimension,
    Asentamiento,
    Departamento,
    Localidad,
    Municipio,
    Provincia,
    Organismos,
    Programas,
)
from legajos.choices import EMOJIS_BANDERAS
from legajos.forms import (
    DimensionEconomiaForm,
    DimensionEducacionForm,
    DimensionFamiliaForm,
    DimensionSaludForm,
    DimensionTrabajoForm,
    DimensionViviendaForm,
    IntervencionForm,
    LegajoGrupoHogarForm,
    LegajosAlertasForm,
    LegajosArchivosForm,
    LegajosDerivacionesForm,
    LegajosForm,
    LegajosUpdateForm,
    LlamadoForm,
    NuevoLegajoFamiliarForm,
)
from legajos.models import (
    ActividadRealizada,
    Agua,
    AportesJubilacion,
    AreaCurso,
    AsisteEscuela,
    CantidadAmbientes,
    CentrosSalud,
    CondicionDe,
    ContextoCasa,
    Desague,
    DimensionEconomia,
    DimensionEducacion,
    DimensionFamilia,
    DimensionSalud,
    DimensionTrabajo,
    DimensionVivienda,
    DuracionTrabajo,
    EstadoDerivacion,
    EstadoNivelEducativo,
    EstadoRelacion,
    Frecuencia,
    Gas,
    Grado,
    HistorialLegajoAlertas,
    Inodoro,
    InstitucionesEducativas,
    Intervencion,
    LegajoAlertas,
    LegajoGrupoFamiliar,
    LegajoGrupoHogar,
    Legajos,
    LegajosArchivos,
    LegajosDerivaciones,
    Llamado,
    ModoContratacion,
    MotivoNivelIncompleto,
    Nacionalidad,
    NivelEducativo,
    NoBusquedaLaboral,
    SubIntervencion,
    SubTipoLlamado,
    TiempoBusquedaLaboral,
    TipoConstruccionVivienda,
    TipoGestion,
    TipoLlamado,
    TipoPisosVivienda,
    TipoPosesionVivienda,
    TipoTechoVivienda,
    TipoVivienda,
    Turno,
    VinculoFamiliar,
)
from usuarios.mixins import PermisosMixin
from usuarios.utils import recortar_imagen

locale.setlocale(locale.LC_ALL, "es_AR.UTF-8")

logger = logging.getLogger("django")

ROL_ADMIN = "usuarios.rol_admin"

# region ############################################################### LEGAJOS


def load_municipios(request):
    provincia_id = request.GET.get("provincia_id")
    municipios = Municipio.objects.filter(fk_provincia=provincia_id)
    return JsonResponse(list(municipios.values("id", "nombre")), safe=False)


def load_localidad(request):
    municipio_id = request.GET.get("municipio_id")
    departamento_id = request.GET.get("departamento_id")

    if municipio_id:
        localidades = Localidad.objects.filter(fk_municipio=municipio_id)
    else:
        localidades = Localidad.objects.filter(fk_departamento=departamento_id)
    return JsonResponse(list(localidades.values("id", "nombre")), safe=False)


def load_departamento(request):
    provincia_id = request.GET.get("provincia_id")
    departamentos = Departamento.objects.filter(fk_provincia=provincia_id)
    return JsonResponse(list(departamentos.values("id", "nombre")), safe=False)


def load_asentamiento(request):
    municipio_id = request.GET.get("municipio_id")
    departamento_id = request.GET.get("departamento_id")

    if municipio_id:
        asentamientos = Asentamiento.objects.filter(fk_localidad=municipio_id)
    else:
        asentamientos = Asentamiento.objects.filter(fk_departamento=departamento_id)
    return JsonResponse(list(asentamientos.values("id", "nombre")), safe=False)


class LegajosReportesListView(ListView):
    template_name = "legajos/legajos_reportes.html"
    model = LegajosDerivaciones

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        organismos = cache.get("organismos")
        if not organismos:
            organismos = Organismos.objects.all().values("id", "nombre")
            cache.set("organismos", organismos, 60)

        programas = cache.get("programas")
        if not programas:
            programas = Programas.objects.all().values("id", "nombre")
            cache.set("programas", programas, 60)

        estados = cache.get("estados_derivacion")
        if not estados:
            estados = EstadoDerivacion.objects.all().values("id", "estado")
            cache.set("estados_derivacion", estados, 60)

        context["organismos"] = organismos
        context["programas"] = programas
        context["estados"] = estados
        return context

    def get_queryset(self):
        nombre_completo_legajo = self.request.GET.get("busqueda")
        data_organismo = self.request.GET.get("data_organismo")
        data_programa = self.request.GET.get("data_programa")
        data_estado = self.request.GET.get("data_estado")
        data_fecha_desde = self.request.GET.get("data_fecha_derivacion")

        filters = Q()

        if data_programa:
            filters &= Q(fk_programa=data_programa)
        if data_organismo:
            filters &= Q(fk_organismo=data_organismo)
        if nombre_completo_legajo:
            filters &= (
                Q(fk_legajo__nombre__icontains=nombre_completo_legajo)
                | Q(fk_legajo__apellido__icontains=nombre_completo_legajo)
                | Q(fk_legajo__documento__icontains=nombre_completo_legajo)
            )
        if data_estado:
            filters &= Q(estado=data_estado)
        if data_fecha_desde:
            filters &= Q(fecha_creado__gte=data_fecha_desde)

        object_list = (
            LegajosDerivaciones.objects.filter(filters)
            .select_related("fk_programa", "fk_organismo", "fk_legajo")
            .distinct()
        )

        if not object_list.exists():
            messages.warning(self.request, "La búsqueda no arrojó resultados.")

        return object_list


class LegajosListView(ListView):
    model = Legajos
    template_name = "legajos/legajos_list.html"
    context_object_name = "legajos"
    paginate_by = 10  # Número de objetos por página

    def get_queryset(self):
        if not hasattr(self, "_cached_queryset"):
            queryset = (
                super()
                .get_queryset()
                .only(
                    "id",
                    "apellido",
                    "nombre",
                    "documento",
                    "tipo_doc",
                    "sexo",
                    "estado",
                )
            )
            query = self.request.GET.get("busqueda", "")

            if query:
                filter_condition = Q(apellido__icontains=query)
                if query.isnumeric():
                    filter_condition |= Q(documento__contains=query)
                queryset = queryset.filter(filter_condition)
            self._cached_queryset = (
                queryset  # pylint: disable=attribute-defined-outside-init
            )

        return self._cached_queryset

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("busqueda")
        if query:
            self.object_list = (
                self.get_queryset()
            )  # pylint: disable=attribute-defined-outside-init
            size_queryset = self.object_list.count()
            if size_queryset == 1:
                pk = self.object_list.first().id
                return redirect("legajos_ver", pk=pk)
            elif size_queryset == 0:
                messages.warning(self.request, "La búsqueda no arrojó resultados.")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("busqueda")
        mostrar_resultados = bool(query)
        page_obj = context.get("page_obj")

        if page_obj:
            context["page_range"] = page_obj.paginator.get_elided_page_range(
                number=page_obj.number
            )

        context.update(
            {
                "mostrar_resultados": mostrar_resultados,
                "query": query,
            }
        )

        return context


class LegajosDetailView(DetailView):
    model = Legajos
    template_name = "legajos/legajos_detail.html"

    def get_context_data(
        self, **kwargs
    ):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        pk = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)

        legajo = context["object"]

        fecha_actual = datetime.now().date()

        legajo_alertas = cache.get("legajo_alertas")
        alertas = cache.get("alertas")
        familiares = cache.get("familiares")
        hogar_familiares = cache.get("hogar_familiares")
        files = cache.get("files")
        legajo_alertas_organizadas = cache.get("legajo_alertas_organizadas")
        count_alertas = cache.get("count_alertas")
        count_alta = cache.get("count_alta")
        count_media = cache.get("count_media")
        count_baja = cache.get("count_baja")
        alertas_alta = cache.get("alertas_alta")
        alertas_media = cache.get("alertas_media")
        alertas_baja = cache.get("alertas_baja")
        historial_alertas = cache.get("historial_alertas")
        count_intervenciones = cache.get("count_intervenciones")
        dimensionfamilia = cache.get("dimensionfamilia")
        dimensionvivienda = cache.get("dimensionvivienda")
        dimensionsalud = cache.get("dimensionsalud")
        dimensiontrabajo = cache.get("dimensiontrabajo")
        datos_json = cache.get("datos_json")
        emoji_nacionalidad = cache.get("emoji_nacionalidad")

        if not legajo_alertas:
            legajo_alertas = LegajoAlertas.objects.filter(fk_legajo=pk).select_related(
                "fk_alerta__fk_categoria"
            )
            cache.set("legajo_alertas", legajo_alertas, 60)
        if not alertas:
            alertas = HistorialLegajoAlertas.objects.filter(fk_legajo=pk).values(
                "fecha_inicio", "fecha_fin", "fk_alerta__fk_categoria__dimension"
            )
            cache.set("alertas", alertas, 60)
        if not familiares:
            familiares = LegajoGrupoFamiliar.objects.filter(
                Q(fk_legajo_1=pk) | Q(fk_legajo_2=pk)
            ).values(
                "fk_legajo_1__nombre",
                "fk_legajo_1__apellido",
                "fk_legajo_1__id",
                "fk_legajo_1__foto",
                "fk_legajo_2__nombre",
                "fk_legajo_2__apellido",
                "fk_legajo_2__id",
                "fk_legajo_2__foto",
                "vinculo",
                "vinculo_inverso",
            )
            cache.set("familiares", familiares, 60)
        if not hogar_familiares:
            hogar_familiares = LegajoGrupoHogar.objects.filter(
                Q(fk_legajo_1Hogar=pk) | Q(fk_legajo_2Hogar=pk)
            ).values(
                "fk_legajo_2Hogar_id",
                "fk_legajo_2Hogar",
                "fk_legajo_1Hogar_id",
                "fk_legajo_1Hogar",
                "fk_legajo_1Hogar__nombre",
                "fk_legajo_2Hogar__nombre",
                "fk_legajo_1Hogar__foto",
                "fk_legajo_2Hogar__foto",
                "estado_relacion",
            )
            cache.set("hogar_familiares", hogar_familiares, 60)
        if not files:
            files = LegajosArchivos.objects.filter(
                Q(tipo="Imagen") | Q(tipo="Documento"), fk_legajo=pk
            )
            cache.set("files", files, 60)
        if not legajo_alertas_organizadas:
            legajo_alertas_organizadas = legajo_alertas.annotate(
                es_critica=Case(
                    When(fk_alerta__gravedad="Critica", then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                es_importante=Case(
                    When(fk_alerta__gravedad="Importante", then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                es_precaucion=Case(
                    When(fk_alerta__gravedad="Precaución", then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
            )
            cache.set("legajo_alertas_organizadas", legajo_alertas_organizadas, 60)
        if not count_alertas:
            count_alertas = legajo_alertas.count()
            cache.set("count_alertas", count_alertas, 60)
        if not count_alta:
            count_alta = legajo_alertas_organizadas.filter(es_critica=True).count()
            cache.set("count_alta", count_alta, 60)
        if not count_media:
            count_media = legajo_alertas_organizadas.filter(es_importante=True).count()
            cache.set("count_media", count_media, 60)
        if not count_baja:
            count_baja = legajo_alertas_organizadas.filter(es_precaucion=True).count()
            cache.set("count_baja", count_baja, 60)
        if not alertas_alta:
            alertas_alta = legajo_alertas_organizadas.filter(es_critica=True)
            cache.set("alertas_alta", alertas_alta, 60)
        if not alertas_media:
            alertas_media = legajo_alertas_organizadas.filter(es_importante=True)
            cache.set("alertas_media", alertas_media, 60)
        if not alertas_baja:
            alertas_baja = legajo_alertas_organizadas.filter(es_precaucion=True)
            cache.set("alertas_baja", alertas_baja, 60)
        if not historial_alertas:
            historial_alertas = alertas.exists()
            cache.set("historial_alertas", historial_alertas, 60)
        if not count_intervenciones:
            count_intervenciones = LegajosDerivaciones.objects.filter(
                fk_legajo=pk
            ).count()
            cache.set("count_intervenciones", count_intervenciones, 60)
        if not dimensionfamilia:
            dimensionfamilia = (
                DimensionFamilia.objects.filter(fk_legajo=pk)
                .values(
                    "cant_hijos",
                    "otro_responsable",
                    "hay_embarazadas",
                    "hay_priv_libertad",
                    "hay_prbl_smental",
                    "hay_enf_cronica",
                    "obs_familia",
                    "hay_fam_discapacidad",
                )
                .first()
            )
            cache.set("dimensionfamilia", dimensionfamilia, 60)
        if not dimensionvivienda:
            dimensionvivienda = (
                DimensionVivienda.objects.filter(fk_legajo=pk)
                .values(
                    "posesion",
                    "tipo",
                    "material",
                    "pisos",
                    "cant_ambientes",
                    "cant_camas",
                    "cant_hogares",
                    "cant_convivientes",
                    "cant_menores",
                    "hay_banio",
                    "hay_agua_caliente",
                    "hay_desmoronamiento",
                    "ContextoCasa",
                    "PoseenPC",
                    "Poseeninternet",
                    "PoseenCelular",
                    "obs_vivienda",
                )
                .first()
            )
            cache.set("dimensionvivienda", dimensionvivienda, 60)

        if not dimensionsalud:
            dimensionsalud = (
                DimensionSalud.objects.filter(fk_legajo=pk)
                .values(
                    "lugares_atencion",
                    "frec_controles",
                    "hay_enfermedad",
                    "hay_obra_social",
                    "hay_discapacidad",
                    "hay_cud",
                    "obs_salud",
                )
                .first()
            )
            cache.set("dimensionsalud", dimensionsalud, 60)
        if not dimensiontrabajo:
            dimensiontrabajo = (
                DimensionTrabajo.objects.filter(fk_legajo=pk)
                .values(
                    "tiene_trabajo",
                    "ocupacion",
                    "modo_contratacion",
                    "conviviente_trabaja",
                    "obs_trabajo",
                )
                .first()
            )
            cache.set("dimensiontrabajo", dimensiontrabajo, 60)
        if not datos_json:
            datos_json = self.grafico_evolucion_de_riesgo(fecha_actual, alertas)
            cache.set("datos_json", datos_json, 60)
        if not emoji_nacionalidad:
            emoji_nacionalidad = EMOJIS_BANDERAS.get(legajo.nacionalidad, "")
            cache.set("emoji_nacionalidad", emoji_nacionalidad, 60)

        context["familiares_fk1"] = [
            familiar
            for familiar in familiares
            if familiar["fk_legajo_1__id"] == int(pk)
        ]
        context["familiares_fk2"] = [
            familiar
            for familiar in familiares
            if familiar["fk_legajo_2__id"] == int(pk)
        ]
        context["count_familia"] = len(familiares)

        context["hogar_familiares_fk1"] = [
            familiar
            for familiar in hogar_familiares
            if familiar["fk_legajo_1Hogar"] == int(pk)
        ]
        context["hogar_familiares_fk2"] = [
            familiar
            for familiar in hogar_familiares
            if familiar["fk_legajo_2Hogar"] == int(pk)
        ]
        context["hogar_count_familia"] = len(hogar_familiares)

        context["files_img"] = files.filter(tipo="Imagen")
        context["files_docs"] = files.filter(tipo="Documento")

        context["count_alertas"] = count_alertas
        context["count_alta"] = count_alta
        context["count_media"] = count_media
        context["count_baja"] = count_baja

        context["alertas_alta"] = alertas_alta
        context["alertas_media"] = alertas_media
        context["alertas_baja"] = alertas_baja

        context["historial_alertas"] = historial_alertas

        context["count_intervenciones"] = count_intervenciones

        context["dimensionfamilia"] = dimensionfamilia

        context["dimensionvivienda"] = dimensionvivienda

        context["dimensionsalud"] = dimensionsalud

        context["dimensiontrabajo"] = dimensiontrabajo

        context["datos_json"] = datos_json

        context["emoji_nacionalidad"] = emoji_nacionalidad

        return context

    def grafico_evolucion_de_riesgo(
        self, fecha_actual, alertas
    ):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        if alertas.exists():
            primer_dia_siguiente_mes = datetime(
                fecha_actual.year, fecha_actual.month % 12 + 1, 1
            )
            fecha_inicio_doce_meses_excepto_mes_anterior = (
                primer_dia_siguiente_mes - timedelta(days=365)
            )

            alertas_ultimo_anio = alertas.filter(
                Q(fecha_inicio__gt=fecha_inicio_doce_meses_excepto_mes_anterior)
                | Q(fecha_fin__gt=fecha_inicio_doce_meses_excepto_mes_anterior)
                | Q(fecha_fin__isnull=True)
            ).distinct()

            dimensiones = {
                str(dimension.id).strip(): dimension.dimension
                for dimension in Dimension.objects.all()
                if dimension.id is not None
            }
            todas_dimensiones = list(dimensiones.keys())
            datos_por_dimension = {
                dimension: [0] * 12 for dimension in todas_dimensiones
            }

            for alerta in alertas_ultimo_anio:
                dimension = alerta["fk_alerta__fk_categoria__dimension"]
                fecha_inicio = alerta["fecha_inicio"]
                fecha_fin = alerta["fecha_fin"] or fecha_actual

                meses_activos = []
                while fecha_inicio <= fecha_fin:
                    meses_activos.append(fecha_inicio.month)
                    fecha_inicio = fecha_inicio.replace(day=1) + timedelta(days=32)
                    fecha_inicio = fecha_inicio.replace(day=1)

                for mes in meses_activos:
                    datos_por_dimension[dimension][mes - 1] += 1

            mes_actual = fecha_actual.month
            datos_por_dimension = {
                dimension: datos_por_dimension[dimension][mes_actual:]
                + datos_por_dimension[dimension][:mes_actual]
                for dimension in todas_dimensiones
            }

            nombres_meses = [
                calendar.month_name[mes].capitalize() for mes in range(1, 13)
            ]
            nombres_meses_ordenados = (
                nombres_meses[mes_actual:] + nombres_meses[:mes_actual]
            )

            datos_por_dimension["meses"] = nombres_meses_ordenados

            datos_json = json.dumps(datos_por_dimension)
        else:
            datos_json = {}

        return datos_json


class LegajosDeleteView(PermisosMixin, DeleteView):
    permission_required = ROL_ADMIN
    model = Legajos
    success_url = reverse_lazy("legajos_listar")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        legajo = self.get_object()

        # Crear una lista para almacenar los nombres de las relaciones existentes
        relaciones_existentes = []

        # Agregar los nombres de las relaciones existentes a la lista
        if LegajosArchivos.objects.filter(fk_legajo=legajo).exists():
            relaciones_existentes.append("Archivos")

        if LegajosDerivaciones.objects.filter(fk_legajo=legajo).exists():
            relaciones_existentes.append("Derivaciones")

        if LegajoAlertas.objects.filter(fk_legajo=legajo).exists():
            relaciones_existentes.append("Alertas")

        if HistorialLegajoAlertas.objects.filter(fk_legajo=legajo).exists():
            relaciones_existentes.append("Historial de Alertas")

        if (
            LegajoGrupoFamiliar.objects.filter(fk_legajo_1=legajo).exists()
            or LegajoGrupoFamiliar.objects.filter(fk_legajo_2=legajo).exists()
        ):
            relaciones_existentes.append("Grupo Familiar")

        # Agregar la lista de nombres de relaciones al contexto
        context["relaciones_existentes"] = relaciones_existentes
        return context

    def form_valid(self, form):
        usuario_eliminacion = self.request.user
        legajo = self.get_object()

        # Graba la data del usuario que realiza la eliminacion en el LOG
        mensaje = (
            f"Legajo borrado - Nombre: {legajo.nombre}, Apellido: {legajo.apellido}, "
            f"Tipo de documento: {legajo.tipo_doc}, Documento: {legajo.documento}"
        )
        logger.info(f"Username: {usuario_eliminacion} - {mensaje}")
        return super().form_valid(form)


class LegajosCreateView(PermisosMixin, CreateView):
    permission_required = ROL_ADMIN
    model = Legajos
    form_class = LegajosForm

    def form_invalid(self, form):
        print("form.errors", form.errors)
        messages.error(
            self.request,
            "Se produjo un error al crear el legajo. Por favor, verifique los datos ingresados.",
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        legajo = form.save(commit=False)

        if legajo.foto:
            buffer = recortar_imagen(legajo.foto)
            legajo.foto.save(legajo.foto.name, ContentFile(buffer.getvalue()))

        try:
            with transaction.atomic():
                legajo.save()

                # Crear las dimensiones
                dimensionfamilia = DimensionFamilia.objects.create(
                    fk_legajo_id=legajo.id
                )
                print("dimensionfamilia", dimensionfamilia)
                dimensionvivienda = DimensionVivienda.objects.create(
                    fk_legajo_id=legajo.id
                )
                print("dimensionvivienda", dimensionvivienda)
                dimensiosalud = DimensionSalud.objects.create(fk_legajo_id=legajo.id)
                print("dimensiosalud", dimensiosalud)
                dimensioneconomia = DimensionEconomia.objects.create(
                    fk_legajo_id=legajo.id
                )
                print("dimensioneconomia", dimensioneconomia)
                dimensioneducacion = DimensionEducacion.objects.create(
                    fk_legajo_id=legajo.id
                )
                print("dimensioneducacion", dimensioneducacion)
                dimensiontrabajo = DimensionTrabajo.objects.create(
                    fk_legajo_id=legajo.id
                )
                print("dimensiontrabajo", dimensiontrabajo)

            # Redireccionar según el botón presionado
            if "form_legajos" in self.request.POST:
                return redirect("legajos_ver", pk=int(legajo.id))
            elif "form_step2" in self.request.POST:
                return redirect("legajosdimensiones_editar", pk=int(legajo.id))
            return None

        except Exception as e:
            messages.error(
                self.request,
                f"Se produjo un error al crear las dimensiones. Por favor, inténtalo de nuevo. Error: {e}",
            )
            return redirect("legajos_crear")


class LegajosUpdateView(PermisosMixin, UpdateView):
    permission_required = ROL_ADMIN
    model = Legajos
    form_class = LegajosUpdateForm

    def form_valid(self, form):
        legajo = form.save(commit=False)  # Guardamos sin persistir en la base de datos
        current_legajo = self.get_object()

        with transaction.atomic():
            # Comprobamos si se ha cargado una nueva foto y si es diferente de la foto actual
            if legajo.foto and legajo.foto != current_legajo.foto:
                buffer = recortar_imagen(legajo.foto)
                legajo.foto.save(legajo.foto.name, ContentFile(buffer.getvalue()))

            self.object = (
                form.save()
            )  # Guardamos el objeto Legajos con la imagen recortada (si corresponde)

        if "form_legajos" in self.request.POST:
            return redirect("legajos_ver", pk=self.object.id)

        if "form_step2" in self.request.POST:
            return redirect("legajosdimensiones_editar", pk=legajo.id)

        return super().form_valid(form)


# endregion


# region ############################################################### GRUPO FAMILIAR


class LegajosGrupoFamiliarCreateView(CreateView):
    permission_required = ROL_ADMIN
    model = LegajoGrupoFamiliar
    form_class = NuevoLegajoFamiliarForm
    paginate_by = 8  # Número de elementos por página

    def get_context_data(self, **kwargs):
        # Paginación

        context = super().get_context_data(**kwargs)
        pk = self.kwargs["pk"]
        legajo_principal = Legajos.objects.get(pk=pk)
        # Calcula la edad utilizando la función 'edad' del modelo
        edad_calculada = legajo_principal.edad()

        # Verifica si tiene más de 18 años
        es_menor_de_18 = True
        if isinstance(edad_calculada, str) and "años" in edad_calculada:
            edad_num = int(edad_calculada.split()[0])
            if edad_num >= 18:
                es_menor_de_18 = False

        # Verificar si tiene un cuidador principal asignado utilizando el método que agregaste al modelo
        tiene_cuidador_ppal = LegajoGrupoFamiliar.objects.filter(
            fk_legajo_1=legajo_principal, cuidador_principal=True
        ).exists()

        # Obtiene los familiares asociados al legajo principal
        familiares = LegajoGrupoFamiliar.objects.filter(
            Q(fk_legajo_1=pk) | Q(fk_legajo_2=pk)
        ).values(
            "id",
            "fk_legajo_1__nombre",
            "fk_legajo_1__apellido",
            "fk_legajo_1__id",
            "fk_legajo_1__foto",
            "fk_legajo_2__nombre",
            "fk_legajo_2__apellido",
            "fk_legajo_2__id",
            "fk_legajo_2__foto",
            "vinculo",
            "vinculo_inverso",
        )

        paginator = Paginator(familiares, self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["familiares_fk1"] = [
            familiar for familiar in page_obj if familiar["fk_legajo_1__id"] == int(pk)
        ]
        context["familiares_fk2"] = [
            familiar for familiar in page_obj if familiar["fk_legajo_2__id"] == int(pk)
        ]

        context["familiares"] = page_obj
        context["count_familia"] = familiares.count()
        context["legajo_principal"] = legajo_principal
        context.update(
            {
                "es_menor_de_18": es_menor_de_18,
                "tiene_cuidador_ppal": tiene_cuidador_ppal,
                "pk": pk,
                "id_dimensionfamiliar": DimensionFamilia.objects.get(fk_legajo=pk).id,
            }
        )
        return context

    def form_valid(self, form):
        pk = self.kwargs["pk"]
        vinculo = form.cleaned_data["vinculo"]
        conviven = form.cleaned_data["conviven"]
        estado_relacion = form.cleaned_data["estado_relacion"].id
        cuidador_principal = form.cleaned_data["cuidador_principal"]

        # Crea el objeto Legajos
        try:
            nuevo_legajo = form.save()
            DimensionFamilia.objects.create(fk_legajo=nuevo_legajo)
            DimensionVivienda.objects.create(fk_legajo=nuevo_legajo)
            DimensionSalud.objects.create(fk_legajo=nuevo_legajo)
            DimensionEconomia.objects.create(fk_legajo=nuevo_legajo)
            DimensionEducacion.objects.create(fk_legajo=nuevo_legajo)
            DimensionTrabajo.objects.create(fk_legajo=nuevo_legajo)
        except Exception as e:
            return messages.error(
                self.request,
                f"Verifique que no exista un legajo con ese DNI y NÚMERO. Error: {e}",
            )

        # Crea el objeto LegajoGrupoFamiliar con los valores del formulario

        try:
            vinculo_instance = VinculoFamiliar.objects.get(vinculo=vinculo)
            estado_relacion_instance = EstadoRelacion.objects.get(pk=estado_relacion)
            legajo_principal = Legajos.objects.get(id=pk)
            LegajoGrupoFamiliar.objects.create(
                fk_legajo_1=legajo_principal,
                fk_legajo_2=nuevo_legajo,
                vinculo=vinculo_instance,
                vinculo_inverso=vinculo_instance.inverso,
                estado_relacion=estado_relacion_instance,
                conviven=conviven,
                cuidador_principal=cuidador_principal,
            )

        except Exception as e:
            messages.error(self.request, f"Error al crear el familiar. Error: {e}")
            return redirect(self.request.path_info)

        messages.success(self.request, "Familiar agregado correctamente.")
        return HttpResponseRedirect(self.request.path_info)


def busqueda_familiares(request):

    res = None
    busqueda = request.POST.get("busqueda", "")
    legajo_principal_id = request.POST.get("id")
    page_number = request.POST.get("page", 1)

    if not legajo_principal_id:
        return JsonResponse(
            {"error": "ID del legajo principal no proporcionado"}, status=400
        )

    legajos_asociados = LegajoGrupoFamiliar.objects.filter(
        Q(fk_legajo_1_id=legajo_principal_id) | Q(fk_legajo_2_id=legajo_principal_id)
    ).values_list("fk_legajo_1_id", "fk_legajo_2_id")

    legajos_asociados_ids = set()
    for fk_legajo_1_id, fk_legajo_2_id in legajos_asociados:
        if fk_legajo_1_id != legajo_principal_id:
            legajos_asociados_ids.add(fk_legajo_1_id)
        if fk_legajo_2_id != legajo_principal_id:
            legajos_asociados_ids.add(fk_legajo_2_id)

    paginate_by = 10
    familiares = Legajos.objects.filter(
        ~Q(id=legajo_principal_id)
        & (Q(apellido__icontains=busqueda) | Q(documento__icontains=busqueda))
    ).exclude(id__in=legajos_asociados_ids)

    if familiares.exists() and busqueda:
        paginator = Paginator(familiares, paginate_by)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        data = [
            {
                "pk": familiar.pk,
                "nombre": familiar.nombre,
                "apellido": familiar.apellido,
                "documento": familiar.documento,
                "tipo_doc": familiar.tipo_doc.tipo if familiar.tipo_doc else None,
                "fecha_nacimiento": familiar.fecha_nacimiento,
                "sexo": familiar.sexo.sexo if familiar.sexo else None,
                # Otros campos
            }
            for familiar in page_obj
        ]
        res = {
            "familiares": data,
            "page": page_number,
            "num_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }
    else:
        res = ""

    return JsonResponse({"data": res})


class LegajoGrupoFamiliarList(ListView):
    model = LegajoGrupoFamiliar

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)
        context["familiares_fk1"] = LegajoGrupoFamiliar.objects.filter(fk_legajo_1=pk)
        context["familiares_fk2"] = LegajoGrupoFamiliar.objects.filter(fk_legajo_2=pk)
        context["count_familia"] = (
            context["familiares_fk1"].count() + context["familiares_fk1"].count()
        )
        context["nombre"] = Legajos.objects.filter(pk=pk).first()
        context["pk"] = pk
        return context


class CreateGrupoFamiliar(View):
    def get(self, request, **kwargs):
        fk_legajo_1 = request.GET.get("fk_legajo_1", None)
        fk_legajo_2 = request.GET.get("fk_legajo_2", None)
        vinculo = request.GET.get("vinculo", None)
        estado_relacion = request.GET.get("estado_relacion", None)
        conviven = request.GET.get("conviven", None)
        cuidador_principal = request.GET.get("cuidador_principal", None)
        obj = None
        vinculo_instance = VinculoFamiliar.objects.get(pk=vinculo)

        if not vinculo_instance:
            return messages.error(self.request, "Vinculo inválido.")
        try:
            estado_relacion_instance = EstadoRelacion.objects.get(pk=estado_relacion)
        except EstadoRelacion.DoesNotExist:
            return JsonResponse({"error": "EstadoRelacion no encontrado"}, status=400)

        obj = LegajoGrupoFamiliar.objects.create(
            fk_legajo_1_id=fk_legajo_1,
            fk_legajo_2_id=fk_legajo_2,
            vinculo=vinculo_instance,
            vinculo_inverso=vinculo_instance.inverso,
            estado_relacion=estado_relacion_instance,
            conviven=conviven,
            cuidador_principal=cuidador_principal,
        )

        familiar = {
            "id": obj.id,
            "fk_legajo_1": obj.fk_legajo_1.id,
            "fk_legajo_2": obj.fk_legajo_2.id,
            "vinculo": obj.vinculo.vinculo,
            "nombre": obj.fk_legajo_2.nombre,
            "apellido": obj.fk_legajo_2.apellido,
            "foto": obj.fk_legajo_2.foto.url if obj.fk_legajo_2.foto else None,
            "cuidador_principal": obj.cuidador_principal,
        }
        data = {
            "tipo_mensaje": "success",
            "mensaje": "Vínculo familiar agregado correctamente.",
        }

        return JsonResponse({"familiar": familiar, "data": data})


class DeleteGrupoFamiliar(View):
    def get(self, request):
        pk = request.GET.get("id", None)
        try:
            familiar = get_object_or_404(LegajoGrupoFamiliar, pk=pk)
            familiar.delete()
            data = {
                "deleted": True,
                "tipo_mensaje": "success",
                "mensaje": "Vínculo familiar eliminado correctamente.",
            }
        except Exception as e:
            data = {
                "deleted": False,
                "tipo_mensaje": "error",
                "mensaje": f"No fue posible eliminar el archivo. Error: {e}",
            }

        return JsonResponse(data)


# endregion


# region ############################################################### DERIVACIONES


class LegajosDerivacionesBuscar(PermisosMixin, TemplateView):
    permission_required = ROL_ADMIN
    template_name = "legajos/legajosderivaciones_buscar.html"

    def get(self, request, *args, **kwargs):  # pylint: disable=too-many-locals
        context = self.get_context_data(**kwargs)
        legajos = cache.get("legajos")
        derivaciones = cache.get("derivaciones")
        con_derivaciones = cache.get("con_derivaciones")
        sin_derivaciones = cache.get("sin_derivaciones")

        if not legajos:
            legajos = Legajos.objects.all()
            cache.set("legajos", legajos, 60)
        if not derivaciones:
            derivaciones = LegajosDerivaciones.objects.all()
            cache.set("derivaciones", derivaciones, 60)
        if not con_derivaciones:
            con_derivaciones = LegajosDerivaciones.objects.none()
            cache.set("con_derivaciones", con_derivaciones, 60)
        if not sin_derivaciones:
            sin_derivaciones = Legajos.objects.none()
            cache.set("sin_derivaciones", sin_derivaciones, 60)

        barrios = legajos.values_list("barrio")
        circuitos = Circuito.objects.all().values_list("id", "circuito")
        localidad = Nacionalidad.objects.all().values_list("id", "nacionalidad")
        mostrar_resultados = False
        mostrar_btn_resetear = False
        query = self.request.GET.get("busqueda")
        if query:
            derivaciones_filtrado = (
                derivaciones.filter(
                    Q(fk_legajo__apellido__icontains=query)
                    | Q(fk_legajo__documento__icontains=query)
                )
                .values("fk_legajo")
                .distinct()
            )
            legajos_filtrado = legajos.filter(
                Q(apellido__icontains=query) | Q(documento__icontains=query)
            ).distinct()

            if derivaciones_filtrado:
                sin_derivaciones = legajos_filtrado.exclude(
                    id__in=derivaciones_filtrado
                )
                con_derivaciones = legajos_filtrado.filter(id__in=derivaciones_filtrado)

            else:
                sin_derivaciones = legajos_filtrado

            if not derivaciones_filtrado and not legajos_filtrado:
                messages.warning(self.request, "La búsqueda no arrojó resultados")

            mostrar_btn_resetear = True
            mostrar_resultados = True

        context["barrios"] = barrios
        context["circuitos"] = circuitos
        context["localidad"] = localidad
        context["mostrar_resultados"] = mostrar_resultados
        context["mostrar_btn_resetear"] = mostrar_btn_resetear
        context["sin_derivaciones"] = sin_derivaciones
        context["con_derivaciones"] = con_derivaciones
        return self.render_to_response(context)


class LegajosDerivacionesListView(PermisosMixin, ListView):
    permission_required = ROL_ADMIN
    model = LegajosDerivaciones
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(LegajosDerivacionesListView, self).get_context_data(**kwargs)

        model = cache.get("model")
        if not model:
            model = LegajosDerivaciones.objects.all()
            cache.set("model", model, 60)

        context["pendientes"] = model.filter(
            estado=EstadoDerivacion.objects.filter(estado="Pendiente").first()
        )
        context["aceptadas"] = model.filter(
            estado=EstadoDerivacion.objects.filter(estado="Aceptada").first()
        )
        context["analisis"] = model.filter(
            estado=EstadoDerivacion.objects.filter(estado="En análisis").first()
        )
        context["asesoradas"] = model.filter(
            estado=EstadoDerivacion.objects.filter(estado="Asesoramiento").first()
        )
        context["enviadas"] = model.filter(fk_usuario=self.request.user)
        return context

    # Funcion de busqueda

    def get_queryset(self):
        model = cache.get("model")
        if model is None:
            model = LegajosDerivaciones.objects.all()
            cache.set("model", model, 60)

        query = self.request.GET.get("busqueda")

        if query:
            object_list = model.filter(
                Q(fk_legajo__apellido__icontains=query)
                | Q(fk_legajo__documento__icontains=query)
            ).distinct()

        else:
            object_list = model.all()

        return object_list.order_by("-estado")


class LegajosDerivacionesCreateView(PermisosMixin, CreateView):
    permission_required = ROL_ADMIN
    model = LegajosDerivaciones
    form_class = LegajosDerivacionesForm
    success_message = "Derivación registrada con éxito"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        pk = self.kwargs.get("pk")

        if pk:
            # excluyo los programas que ya tienen derivaciones en curso para este legajo (solo dejo fuera las 'asesoradas')

            programas = Programas.objects.all().exclude(
                id__in=LegajosDerivaciones.objects.filter(fk_legajo=pk)
                .exclude(
                    estado__in=[
                        EstadoDerivacion.objects.filter(estado="Rechazada").first(),
                        EstadoDerivacion.objects.filter(estado="Finalizada").first(),
                    ]
                )
                .values_list("fk_programa", flat=True)
            )

            form.fields["fk_programa"].queryset = programas
            form.fields["fk_legajo"].initial = pk
            form.fields["fk_usuario"].initial = self.request.user
        return form

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)
        context["legajo"] = Legajos.objects.filter(id=pk).first()
        return context


class LegajosDerivacionesUpdateView(PermisosMixin, UpdateView):
    permission_required = ROL_ADMIN
    model = LegajosDerivaciones
    form_class = LegajosDerivacionesForm
    success_message = "Derivación editada con éxito"

    def get_initial(self):
        initial = super().get_initial()
        initial["fk_usuario"] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)
        legajo = LegajosDerivaciones.objects.filter(id=pk).first()
        context["legajo"] = Legajos.objects.filter(id=legajo.fk_legajo.id).first()
        return context


class LegajosDerivacionesHistorial(PermisosMixin, ListView):
    permission_required = ROL_ADMIN
    model = LegajosDerivaciones
    template_name = "legajos/legajosderivaciones_historial.html"

    def get_context_data(self, **kwargs):
        context = super(LegajosDerivacionesHistorial, self).get_context_data(**kwargs)
        pk = self.kwargs.get("pk")

        legajo = Legajos.objects.filter(id=pk).first()
        historial = LegajosDerivaciones.objects.filter(fk_legajo_id=pk)

        context["historial"] = historial
        context["legajo"] = legajo
        context["pendientes"] = historial.filter(
            estado=EstadoDerivacion.objects.filter(estado="Pendiente").first()
        ).count()
        context["admitidas"] = historial.filter(
            estado=EstadoDerivacion.objects.filter(estado="Aceptada").first()
        ).count()
        context["rechazadas"] = historial.filter(
            estado=EstadoDerivacion.objects.filter(estado="Rechazada").first()
        ).count()
        return context


class LegajosDerivacionesDeleteView(PermisosMixin, DeleteView):
    permission_required = ROL_ADMIN
    model = LegajosDerivaciones

    def form_valid(self, form):
        if (
            self.object.estado
            != EstadoDerivacion.objects.filter(estado="Pendiente").first()
        ):
            messages.error(
                self.request,
                "No es posible eliminar una solicitud en estado " + self.object.estado,
            )

            return redirect("legajosderivaciones_ver", pk=int(self.object.id))

        if self.request.user != self.object.fk_usuario:
            messages.error(
                self.request,
                "Solo el usuario que generó esta derivación puede eliminarla.",
            )

            return redirect("legajosderivaciones_ver", pk=int(self.object.id))

        else:
            legajo = LegajosDerivaciones.objects.filter(pk=self.object.id).first()
            self.object.delete()

            return redirect("legajosderivaciones_historial", pk=legajo.fk_legajo_id)


class LegajosDerivacionesDetailView(PermisosMixin, DetailView):
    permission_required = ROL_ADMIN
    model = LegajosDerivaciones


# endregion


# region ############################################################### ALERTAS


class LegajosAlertasListView(PermisosMixin, ListView):
    permission_required = ROL_ADMIN
    model = HistorialLegajoAlertas
    template_name = "legajos/legajoalertas_list.html"

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)
        context["legajo_alertas"] = HistorialLegajoAlertas.objects.filter(fk_legajo=pk)
        context["legajo"] = (
            Legajos.objects.filter(id=pk).values("apellido", "nombre", "id").first()
        )
        return context


class LegajosAlertasCreateView(PermisosMixin, SuccessMessageMixin, CreateView):
    permission_required = ROL_ADMIN
    model = LegajoAlertas
    form_class = LegajosAlertasForm
    success_message = "Alerta asignada correctamente."

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)

        alertas = LegajoAlertas.objects.filter(fk_legajo=pk)

        legajo = Legajos.objects.values(
            "pk", "dimensionfamilia__id", "nombre", "apellido"
        ).get(pk=pk)

        context["alertas"] = alertas
        context["legajo"] = legajo
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        pk = self.kwargs.get("pk")
        if pk:
            form.fields["fk_legajo"].initial = pk
            form.fields["creada_por"].initial = self.request.user.usuarios.id
        return form

    def get_success_url(self):
        # Redirige a la misma página después de agregar la alerta
        return self.request.path


class DeleteAlerta(PermisosMixin, View):
    permission_required = ROL_ADMIN

    def get(self, request):
        try:
            pk = request.GET.get("id", None)
            legajo_alerta = get_object_or_404(LegajoAlertas, pk=pk)
            legajo = legajo_alerta.fk_legajo
            alerta = legajo_alerta.fk_alerta
            legajo_alerta.delete()

            # Filtrar el registro activo actualmente (sin fecha_fin)
            registro_historial = HistorialLegajoAlertas.objects.filter(
                Q(fk_alerta=alerta) & Q(fk_legajo=legajo) & Q(fecha_fin__isnull=True)
            ).first()

            if registro_historial:
                registro_historial.eliminada_por = request.user.usuarios
                registro_historial.fecha_fin = date.today()
                registro_historial.save()

                data = {
                    "deleted": True,
                    "tipo_mensaje": "success",
                    "mensaje": "Alerta eliminada correctamente.",
                }
            else:
                data = {
                    "deleted": True,
                    "tipo_mensaje": "warning",
                    "mensaje": "Alerta eliminada, con errores en el historial.",
                }
        except Exception as e:
            data = {
                "deleted": False,
                "tipo_mensaje": "error",
                "mensaje": f"No fue posible eliminar el alerta. Error: {e}",
            }

        return JsonResponse(data)


class CategoriasSelectView(View):
    def get(self, request, *args, **kwargs):
        alerta_id = request.GET.get("alerta_id")
        if alerta_id:
            categorias = CategoriaAlertas.objects.filter(alertas__id=alerta_id)
        else:
            categorias = CategoriaAlertas.objects.all()

        data = [
            {"id": categoria.id, "text": categoria.nombre} for categoria in categorias
        ]
        return JsonResponse(data, safe=False)


class AlertasSelectView(View):
    def get(self, request, *args, **kwargs):
        categoria_id = request.GET.get("categoria_id")
        if categoria_id:
            alertas = Alertas.objects.filter(fk_categoria_id=categoria_id)
        else:
            alertas = Alertas.objects.all()

        data = [{"id": alerta.id, "text": alerta.nombre} for alerta in alertas]
        return JsonResponse(data, safe=False)


# endregion


# region ############################################################### DIMENSIONES


class DimensionesUpdateView(PermisosMixin, SuccessMessageMixin, UpdateView):
    # FIXME: Crear updateView por cada formulario
    permission_required = ROL_ADMIN
    template_name = "legajos/legajosdimensiones_form.html"
    model = DimensionFamilia
    form_class = DimensionFamiliaForm
    form_vivienda = DimensionViviendaForm
    form_salud = DimensionSaludForm
    form_educacion = DimensionEducacionForm
    form_economia = DimensionEconomiaForm
    form_trabajo = DimensionTrabajoForm
    success_message = "Editado correctamente"

    def get_object(self, queryset=None):
        pk = self.kwargs["pk"]
        legajo = Legajos.objects.only("id").get(id=pk)
        return DimensionFamilia.objects.get(fk_legajo=legajo.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs["pk"]
        legajo = (
            Legajos.objects.select_related(
                "dimensionvivienda",
                "dimensionsalud",
                "dimensioneducacion",
                "dimensioneconomia",
                "dimensiontrabajo",
            )
            .only(
                "id",
                "apellido",
                "nombre",
                "dimensionvivienda__fk_legajo",
                "dimensionvivienda__obs_vivienda",
                "dimensionsalud__fk_legajo",
                "dimensionsalud__obs_salud",
                "dimensionsalud__hay_obra_social",
                "dimensionsalud__hay_enfermedad",
                "dimensionsalud__hay_discapacidad",
                "dimensionsalud__hay_cud",
                "dimensioneducacion__fk_legajo",
                "dimensioneducacion__obs_educacion",
                "dimensioneducacion__areaCurso",
                "dimensioneducacion__areaOficio",
                "dimensioneconomia__fk_legajo",
                "dimensioneconomia__obs_economia",
                "dimensioneconomia__m2m_planes",
                "dimensiontrabajo__fk_legajo",
                "dimensiontrabajo__obs_trabajo",
            )
            .get(id=pk)
        )

        # TODO: Modificar logica para no utilizar los siguientes "None' y crear la dimension segun haga falta
        context.update(
            {
                "legajo": legajo,
                "form_vivienda": self.form_vivienda(
                    instance=getattr(legajo, "dimensionvivienda", None)
                ),
                "form_salud": self.form_salud(
                    instance=getattr(legajo, "dimensionsalud", None)
                ),
                "form_educacion": self.form_educacion(
                    instance=getattr(legajo, "dimensioneducacion", None)
                ),
                "form_economia": self.form_economia(
                    instance=getattr(legajo, "dimensioneconomia", None)
                ),
                "form_trabajo": self.form_trabajo(
                    instance=getattr(legajo, "dimensiontrabajo", None)
                ),
            }
        )

        return context

    def form_valid(
        self, form
    ):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        # TODO: Esto sera refactorizado
        self.object = form.save(commit=False)

        pk = self.kwargs["pk"]

        legajo_dim_vivienda = DimensionVivienda.objects.get(fk_legajo__id=pk)
        legajo_dim_salud = DimensionSalud.objects.get(fk_legajo__id=pk)
        legajo_dim_educacion = DimensionEducacion.objects.get(fk_legajo__id=pk)
        legajo_dim_economia = DimensionEconomia.objects.get(fk_legajo__id=pk)
        legajo_dim_trabajo = DimensionTrabajo.objects.get(fk_legajo__id=pk)
        form_multiple = self.form_class(self.request.POST).data.copy()

        # cambio el valor 'on' y 'off' por True/False
        for clave, valor in form_multiple.items():
            if valor == "on":
                form_multiple[clave] = True

            elif valor == "off":
                form_multiple[clave] = False

        # dimension vivienda

        fields_mapping_vivienda = {
            "tipo": TipoVivienda,
            "material": TipoConstruccionVivienda,
            "pisos": TipoPisosVivienda,
            "posesion": TipoPosesionVivienda,
            "cant_ambientes": CantidadAmbientes,
            "cant_convivientes": "cant_convivientes",
            "cant_menores": "cant_menores",
            "cant_camas": "cant_camas",
            "cant_hogares": "cant_hogares",
            "hay_agua_caliente": "hay_agua_caliente",
            "hay_desmoronamiento": "hay_desmoronamiento",
            "hay_banio": Inodoro,
            "PoseenCelular": "PoseenCelular",
            "PoseenPC": "PoseenPC",
            "Poseeninternet": "Poseeninternet",
            "ContextoCasa": ContextoCasa,
            "CondicionDe": CondicionDe,
            "CantidadAmbientes": "CantidadAmbientes",
            "gas": Gas,
            "techos": TipoTechoVivienda,
            "agua": Agua,
            "desague": Desague,
            "obs_vivienda": "obs_vivienda",
        }

        for field, model in fields_mapping_vivienda.items():
            value = form_multiple.get(field)

            if value:
                # Verifica si el valor del campo es una instancia de un modelo o una ForeignKey
                if isinstance(model, type) and issubclass(model, models.Model):
                    instance = model.objects.get(pk=value)
                    setattr(legajo_dim_vivienda, field, instance)
                else:
                    setattr(legajo_dim_vivienda, field, value)
            else:
                setattr(legajo_dim_vivienda, field, None)

        legajo_dim_vivienda.save()

        # dimension salud

        fields_mapping_salud = {
            "lugares_atencion": CentrosSalud,
            "frec_controles": Frecuencia,
            "hay_obra_social": "hay_obra_social",
            "hay_enfermedad": "hay_enfermedad",
            "hay_discapacidad": "hay_discapacidad",
            "hay_cud": "hay_cud",
            "obs_salud": "obs_salud",
        }

        for field in fields_mapping_salud:
            value = form_multiple.get(field)

            if value:
                # Verifica si el valor del campo es una instancia de un modelo o una ForeignKey
                if isinstance(fields_mapping_salud.get(field), type) and issubclass(
                    fields_mapping_salud.get(field), models.Model
                ):
                    instance = fields_mapping_salud.get(field).objects.get(pk=value)
                    setattr(legajo_dim_salud, field, instance)
                else:
                    setattr(legajo_dim_salud, field, value)

            else:
                setattr(legajo_dim_salud, field, None)

        legajo_dim_salud.save()

        # dimension educacion

        fields_mapping_educacion = {
            "max_nivel": NivelEducativo,
            "estado_nivel": EstadoNivelEducativo,
            "asiste_escuela": AsisteEscuela,
            "institucion": InstitucionesEducativas,
            "gestion": TipoGestion,
            "ciclo": NivelEducativo,
            "grado": Grado,
            "turno": Turno,
            "obs_educacion": "obs_educacion",
            "provinciaInstitucion": Provincia,
            "localidadInstitucion": Localidad,
            "municipioInstitucion": Municipio,
            "barrioInstitucion": "barrioInstitucion",
            "calleInstitucion": "calleInstitucion",
            "numeroInstitucion": "numeroInstitucion",
            "interesEstudio": "interesEstudio",
            "interesCurso": "interesCurso",
            "nivelIncompleto": MotivoNivelIncompleto,
            "sinEduFormal": MotivoNivelIncompleto,
            "realizandoCurso": "realizandoCurso",
            "areaCurso": AreaCurso,
            "interesCapLab": "interesCapLab",
            "areaOficio": AreaCurso,
            "oficio": "oficio",
        }

        for field, model in fields_mapping_educacion.items():
            value = form_multiple.get(field)

            if value:
                # Verifica si el valor del campo es una instancia de un modelo o una ForeignKey
                if isinstance(model, type) and issubclass(model, models.Model):
                    instance = model.objects.get(pk=value)
                    setattr(legajo_dim_educacion, field, instance)
                else:
                    setattr(legajo_dim_educacion, field, value)
            else:
                setattr(legajo_dim_educacion, field, None)

        legajo_dim_educacion.save()

        # dimension economia

        fields_mapping_economia = {
            "ingresos": "ingresos",
            "recibe_plan": "recibe_plan",
            "m2m_planes": "m2m_planes",
            "cant_aportantes": "cant_aportantes",
            "obs_economia": "obs_economia",
        }

        for field in fields_mapping_economia:
            value = form_multiple.get(field)

            if field == "m2m_planes":
                lista = form_multiple.getlist("m2m_planes")

                legajo_dim_economia.m2m_planes.set(lista)

            else:
                if value:
                    setattr(
                        legajo_dim_economia,
                        fields_mapping_economia.get(field, field),
                        value,
                    )

                else:
                    setattr(legajo_dim_economia, field, None)

        legajo_dim_economia.save()

        # dimension trabajo

        fields_mapping_trabajo = {
            "tiene_trabajo": "tiene_trabajo",
            "modo_contratacion": ModoContratacion,
            "ocupacion": "ocupacion",
            "conviviente_trabaja": "conviviente_trabaja",
            "obs_trabajo": "obs_trabajo",
            "horasSemanales": "horasSemanales",
            "actividadRealizadaComo": ActividadRealizada,
            "duracionTrabajo": DuracionTrabajo,
            "aportesJubilacion": AportesJubilacion,
            "TiempoBusquedaLaboral": TiempoBusquedaLaboral,
            "busquedaLaboral": "busquedaLaboral",
            "noBusquedaLaboral": NoBusquedaLaboral,
        }

        for field, model in fields_mapping_trabajo.items():
            value = form_multiple.get(field)

            if value:
                if isinstance(model, type) and issubclass(model, models.Model):
                    instance = model.objects.get(pk=value)
                    setattr(legajo_dim_trabajo, field, instance)
                else:
                    setattr(legajo_dim_trabajo, field, value)
            else:
                setattr(legajo_dim_trabajo, field, None)

        legajo_dim_trabajo.save()

        if "form_step1" in self.request.POST:
            self.object.save()

            return redirect("legajos_editar", pk=pk)

        if "form_step2" in self.request.POST:
            self.object.save()

            return redirect("legajos_ver", pk=pk)

        if "form_step3" in self.request.POST:
            self.object.save()

            return redirect("grupofamiliar_crear", pk=pk)

        self.object = form.save()

        return super().form_valid(form)


class DimensionesDetailView(PermisosMixin, DetailView):
    permission_required = ROL_ADMIN
    model = Legajos
    template_name = "legajos/legajosdimensiones_detail.html"


# endregion


# region ################################################################ ARCHIVOS
class LegajosArchivosListView(PermisosMixin, ListView):
    permission_required = ROL_ADMIN
    model = LegajosArchivos
    template_name = "legajos/legajosarchivos_list.html"

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)
        context["legajo_archivos"] = LegajosArchivos.objects.filter(fk_legajo=pk)
        context["legajo"] = Legajos.objects.filter(id=pk).first()
        return context


class LegajosArchivosCreateView(PermisosMixin, SuccessMessageMixin, CreateView):
    permission_required = ROL_ADMIN
    model = LegajosArchivos
    form_class = LegajosArchivosForm
    success_message = "Archivo actualizado correctamente."

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)
        archivos = LegajosArchivos.objects.filter(fk_legajo=pk)
        imagenes = archivos.filter(tipo="Imagen")
        documentos = archivos.filter(tipo="Documento")
        legajo = Legajos.objects.filter(pk=pk).first()
        context["imagenes"] = imagenes
        context["documentos"] = documentos
        context["legajo"] = legajo
        return context


class CreateArchivo(TemplateView):
    def post(self, request):
        pk = request.POST.get("pk")
        legajo = Legajos.objects.get(id=pk)
        response_data_list = []  # Lista para almacenar las respuestas de los archivos

        files = request.FILES.getlist(
            "file"
        )  # Acceder a los archivos enviados desde Dropzone

        for f in files:
            if f:
                file_extension = f.name.split(".")[-1].lower()
                if file_extension in ["jpg", "jpeg", "png", "gif", "bmp"]:
                    tipo = "Imagen"
                else:
                    tipo = "Documento"

                legajo_archivo = LegajosArchivos.objects.create(
                    fk_legajo=legajo, archivo=f, tipo=tipo
                )

                response_data = {
                    "id": legajo_archivo.id,
                    "tipo": legajo_archivo.tipo,
                    "archivo_url": legajo_archivo.archivo.url,
                }

                response_data_list.append(
                    response_data
                )  # Agregar la respuesta actual a la lista

        return JsonResponse(
            response_data_list, safe=False
        )  # Devolver la lista completa de respuestas como JSON


class DeleteArchivo(PermisosMixin, View):
    permission_required = ROL_ADMIN

    def get(self, request):
        try:
            pk = request.GET.get("id", None)
            legajo_archivo = get_object_or_404(LegajosArchivos, pk=pk)
            legajo_archivo.delete()

            data = {
                "deleted": True,
                "tipo_mensaje": "success",
                "mensaje": "Archivo eliminado correctamente.",
            }
        except Exception as e:
            data = {
                "deleted": False,
                "tipo_mensaje": "error",
                "mensaje": f"No fue posible eliminar el archivo. Error: {e}",
            }

        return JsonResponse(data)


class ProgramasIntervencionesView(TemplateView):
    template_name = "legajos/programas_intervencion.html"
    model = Legajos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        legajo = Legajos.objects.filter(pk=self.kwargs["pk"]).first()

        context["legajo"] = legajo

        return context


class AccionesSocialesView(TemplateView):
    template_name = "legajos/acciones_sociales.html"
    model = Legajos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        legajo_id = self.kwargs["pk"]

        legajo = Legajos.objects.only(
            "apellido",
            "nombre",
            "id",
            "tipo_doc",
            "documento",
            "fecha_nacimiento",
            "sexo",
        ).get(pk=legajo_id)

        context["legajo"] = legajo

        return context


class IntervencionesSaludView(TemplateView):
    template_name = "legajos/intervenciones_salud.html"
    model = Legajos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        legajo = Legajos.objects.filter(pk=self.kwargs["pk"]).first()

        context["legajo"] = legajo

        return context


class IndicesView(TemplateView):
    template_name = "legajos/indices.html"
    model = Legajos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        legajo = Legajos.objects.filter(pk=self.kwargs["pk"]).first()

        context["legajo"] = legajo

        return context


class IndicesDetalleView(TemplateView):
    template_name = "legajos/indices_detalle.html"
    model = Legajos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        legajo = Legajos.objects.filter(pk=self.kwargs["pk"]).first()

        context["legajo"] = legajo

        return context


# endregion ###########################################################

# region ############################################################### GRUPO Hogar


class LegajosGrupoHogarCreateView(CreateView):
    permission_required = ROL_ADMIN
    model = LegajoGrupoHogar
    form_class = LegajoGrupoHogarForm
    paginate_by = 8

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        legajo_principal = Legajos.objects.filter(pk=pk).first()

        context = super().get_context_data(**kwargs)

        hogares = LegajoGrupoHogar.objects.filter(
            Q(fk_legajo_1Hogar=pk) | Q(fk_legajo_2Hogar=pk)
        ).values(
            "id",
            "fk_legajo_1Hogar__nombre",
            "fk_legajo_2Hogar__nombre",
            "fk_legajo_1Hogar__apellido",
            "fk_legajo_2Hogar__apellido",
            "fk_legajo_1Hogar__foto",
            "fk_legajo_2Hogar__foto",
            "fk_legajo_1Hogar__id",
            "fk_legajo_2Hogar__id",
        )

        # Paginacion

        paginator = Paginator(hogares, self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["hogar_1"] = [
            familiar
            for familiar in page_obj
            if familiar["fk_legajo_1Hogar__id"] == int(pk)
        ]
        context["hogar_2"] = [
            familiar
            for familiar in page_obj
            if familiar["fk_legajo_2Hogar__id"] == int(pk)
        ]
        print(context["hogar_1"])

        context["hogares"] = page_obj
        context["count_hogar"] = hogares.count()
        context["legajo_principal"] = legajo_principal
        context["pk"] = pk

        return context

    def form_valid(self, form):
        pk = self.kwargs["pk"]
        estado_relacion = form.cleaned_data["estado_relacion"]

        # Crea el objeto Legajos
        try:
            nuevo_legajo = form.save()
            DimensionFamilia.objects.create(fk_legajo=nuevo_legajo)
            DimensionVivienda.objects.create(fk_legajo=nuevo_legajo)
            DimensionSalud.objects.create(fk_legajo=nuevo_legajo)
            DimensionEconomia.objects.create(fk_legajo=nuevo_legajo)
            DimensionEducacion.objects.create(fk_legajo=nuevo_legajo)
            DimensionTrabajo.objects.create(fk_legajo=nuevo_legajo)
            LegajoGrupoHogar.objects.create(fk_legajo=nuevo_legajo)
        except Exception as e:
            return messages.error(
                self.request,
                f"Verifique que no exista un legajo con ese DNI y NÚMERO. Error: {e}",
            )

        # crea la relacion de grupo familiar
        estado_relacion_instance = EstadoRelacion.objects.get(pk=estado_relacion)

        legajo_principal = Legajos.objects.get(id=pk)
        try:
            LegajoGrupoFamiliar.objects.create(
                fk_legajo_1=legajo_principal,
                fk_legajo_2=nuevo_legajo,
                #  vinculo=vinculo_data["vinculo"],
                # vinculo_inverso=vinculo_data["vinculo_inverso"],
                estado_relacion=estado_relacion_instance,
            )
        except Exception as e:
            return messages.error(
                self.request,
                f"Verifique que no exista un legajo con ese DNI y NÚMERO. {e}",
            )

        messages.success(self.request, "Familair agregado correctamente.")
        # Redireccionar a la misma página después de realizar la acción con éxito
        return HttpResponseRedirect(self.request.path_info)


def busqueda_hogar(request):

    res = None
    busqueda = request.POST.get("busqueda", "")
    legajo_principal_id = request.POST.get("id")
    page_number = request.POST.get("page", 1)

    legajos_asociados = LegajoGrupoHogar.objects.filter(
        Q(fk_legajo_1Hogar_id=legajo_principal_id)
        | Q(fk_legajo_2Hogar_id=legajo_principal_id)
    ).values_list("fk_legajo_1Hogar_id", "fk_legajo_2Hogar_id")

    legajos_asociados_ids = set()
    for fk_legajo_1, fk_legajo_2 in legajos_asociados:
        if fk_legajo_1 != legajo_principal_id:
            legajos_asociados_ids.add(fk_legajo_1)
        if fk_legajo_2 != legajo_principal_id:
            legajos_asociados_ids.add(fk_legajo_2)

    paginate_by = 10
    hogares = Legajos.objects.filter(
        ~Q(id=legajo_principal_id)
        & (Q(apellido__icontains=busqueda) | Q(documento__icontains=busqueda))
    ).exclude(id__in=legajos_asociados_ids)

    if hogares.exists() and busqueda:
        paginator = Paginator(hogares, paginate_by)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        data = [
            {
                "pk": hogar.pk,
                "nombre": hogar.nombre,
                "apellido": hogar.apellido,
                "documento": hogar.documento,
                "tipo_doc": hogar.tipo_doc.tipo if hogar.tipo_doc else None,
                "fecha_nacimiento": hogar.fecha_nacimiento,
                "sexo": hogar.sexo.sexo if hogar.sexo else None,
            }
            for hogar in page_obj
        ]
        res = {
            "hogares": data,
            "page": page_number,
            "num_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }
    else:
        res = ""

    return JsonResponse({"data": res})


class LegajoGrupoHogarList(ListView):
    model = LegajoGrupoFamiliar

    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)

        # FIXME: Esta query optimizada de "familiares" no se termino de implementar
        familiares = LegajoGrupoFamiliar.objects.filter(
            Q(fk_legajo_1=pk) | Q(fk_legajo_2=pk)
        ).values(
            "fk_legajo2__id",
            "fk_legajo1__id",
            "fk_legajo_2__nombre",
            "fk_legajo_2__apellido",
            "fk_legajo_2__calle",
            "fk_legajo_2__telefono",
            "estado_relacion",
            "conviven",
            "cuidado_principal",
            "fk_legajo_2__foto",
            "fk_legajo_1__nombre",
            "fk_legajo_1__apellido",
            "fk_legajo_1__calle",
            "fk_legajo_1__telefono",
            "estado_relacion",
            "conviven",
            "cuidado_principal",
            "fk_legajo_1__foto",
            "vinculo",
        )
        context["familiares_fk1"] = [
            familiar
            for familiar in familiares
            if familiar["fk_legajo_1__id"] == int(pk)
        ]
        context["familiares_fk2"] = [
            familiar
            for familiar in familiares
            if familiar["fk_legajo_1__id"] == int(pk)
        ]
        context["count_familia"] = (
            context["familiares_fk1"].count() + context["familiares_fk1"].count()
        )
        context["nombre"] = Legajos.objects.filter(pk=pk).values("nombre").first()
        context["pk"] = pk
        return context


class CreateGrupoHogar(View):
    def get(self, request, **kwargs):
        fk_legajo_1 = request.GET.get("fk_legajo_1", None)
        fk_legajo_2 = request.GET.get("fk_legajo_2", None)
        estado_relacion = request.GET.get("estado_relacion", None)

        obj = None

        try:
            estado_relacion_instance = EstadoRelacion.objects.get(pk=estado_relacion)
        except EstadoRelacion.DoesNotExist:
            return JsonResponse({"error": "EstadoRelacion no encontrado"}, status=400)

        obj = LegajoGrupoHogar.objects.create(
            fk_legajo_1Hogar_id=fk_legajo_1,
            fk_legajo_2Hogar_id=fk_legajo_2,
            estado_relacion=estado_relacion_instance,
        )

        familiar = {
            "id": obj.id,
            "fk_legajo_1": obj.fk_legajo_1Hogar.id,
            "fk_legajo_2": obj.fk_legajo_2Hogar.id,
            "estado_relacion": obj.estado_relacion.estado,
            "nombre": obj.fk_legajo_2Hogar.nombre,
            "apellido": obj.fk_legajo_2Hogar.apellido,
            "foto": (
                obj.fk_legajo_2Hogar.foto.url if obj.fk_legajo_2Hogar.foto else None
            ),
        }
        data = {
            "tipo_mensaje": "success",
            "mensaje": "Vínculo hogar agregado correctamente.",
        }

        return JsonResponse({"hogar": familiar, "data": data})


class DeleteGrupoHogar(View):
    def get(self, request):
        pk = request.GET.get("id", None)
        try:
            familiar = get_object_or_404(LegajoGrupoHogar, pk=pk)
            familiar.delete()
            data = {
                "deleted": True,
                "tipo_mensaje": "success",
                "mensaje": "Vínculo del hogar eliminado correctamente.",
            }
        except Exception as e:
            data = {
                "deleted": False,
                "tipo_mensaje": "error",
                "mensaje": f"No fue posible eliminar el vinculo. Error: {e}",
            }

        return JsonResponse(data)


class IntervencionDetail(TemplateView):
    permission_required = ROL_ADMIN
    template_name = "legajos/intervencion_detail.html"
    model = Intervencion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        legajo = Legajos.objects.values(
            "id", "nombre", "apellido", "documento", "fecha_nacimiento", "sexo"
        ).get(pk=self.kwargs["pk"])
        intervenciones = Intervencion.objects.filter(fk_legajo=self.kwargs["pk"])
        cantidad_intervenciones = Intervencion.objects.filter(
            fk_legajo=self.kwargs["pk"]
        ).count()
        context["intervenciones"] = intervenciones
        context["object"] = legajo
        context["cantidad_intervenciones"] = cantidad_intervenciones

        return context


class IntervencionCreateView(CreateView):
    permission_required = ROL_ADMIN
    model = Intervencion
    template_name = "legajos/intervencion_form.html"
    form_class = IntervencionForm

    def form_valid(self, form):
        pk = self.kwargs["pk"]
        form.save()
        return redirect("intervencion_ver", pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        legajo = Legajos.objects.values(
            "id", "nombre", "apellido", "documento", "fecha_nacimiento", "sexo"
        ).get(pk=self.kwargs["pk"])

        context["form"] = self.get_form()
        context["object"] = legajo

        return context


class IntervencionDeleteView(DeleteView):
    permission_required = ROL_ADMIN
    model = Intervencion
    template_name = "legajos/intervencion_confirm_delete.html"

    def form_valid(self, form):
        self.object.delete()
        return redirect("intervencion_ver", pk=self.kwargs["pk2"])


class IntervencionUpdateView(UpdateView):
    permission_required = ROL_ADMIN
    model = Intervencion
    form_class = IntervencionForm
    template_name = "legajos/intervencion_form.html"

    def form_valid(self, form):
        pk = self.kwargs["pk2"]
        form.save()
        return redirect("intervencion_ver", pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        legajo = Legajos.objects.values(
            "id", "nombre", "apellido", "documento", "fecha_nacimiento", "sexo"
        ).get(pk=self.kwargs["pk2"])
        context["form"] = self.get_form()
        context["object"] = legajo
        return context


class LlamadoDetail(TemplateView):
    permission_required = ROL_ADMIN
    template_name = "legajos/llamado_detail.html"
    model = Llamado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        legajo = Legajos.objects.values(
            "id", "nombre", "apellido", "documento", "fecha_nacimiento", "sexo"
        ).get(pk=self.kwargs["pk"])
        llamados = Llamado.objects.filter(fk_legajo=self.kwargs["pk"])
        cantidad_llamados = Llamado.objects.filter(fk_legajo=self.kwargs["pk"]).count()
        context["object"] = legajo
        context["llamados"] = llamados
        context["cantidad_llamados"] = cantidad_llamados
        return context


class LlamadoDeleteView(DeleteView):
    permission_required = ROL_ADMIN
    model = Llamado

    def form_valid(self, form):
        self.object.delete()
        return redirect("llamados_ver", pk=self.kwargs["pk2"])


class LlamadoCreateView(CreateView):
    permission_required = ROL_ADMIN
    model = Llamado
    template_name = "legajos/llamado_form.html"
    form_class = LlamadoForm

    def form_valid(self, form):
        pk = self.kwargs["pk"]
        form.save()
        return redirect("llamados_ver", pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        legajo = Legajos.objects.values(
            "id", "nombre", "apellido", "documento", "fecha_nacimiento", "sexo"
        ).get(pk=self.kwargs["pk"])
        context["form"] = self.get_form()
        context["object"] = legajo
        return context


class LlamadoUpdateView(UpdateView):
    permission_required = ROL_ADMIN
    model = Llamado
    form_class = LlamadoForm
    template_name = "legajos/llamado_form.html"

    def form_valid(self, form):
        pk = self.kwargs["pk2"]
        form.save()
        return redirect("llamados_ver", pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        legajo = Legajos.objects.values(
            "id", "nombre", "apellido", "documento", "fecha_nacimiento", "sexo"
        ).get(pk=self.kwargs["pk2"])
        context["form"] = self.get_form()
        context["object"] = legajo
        return context


class SubEstadosIntervencionesAJax(View):
    def get(self, request):
        request_id = request.GET.get("id", None)
        if request_id:
            sub_estados = SubIntervencion.objects.filter(fk_subintervencion=request_id)
        else:
            sub_estados = SubIntervencion.objects.all()
        data = [
            {"id": sub_estado.id, "text": sub_estado.nombre}
            for sub_estado in sub_estados
        ]
        return JsonResponse(data, safe=False)


class SubEstadosLlamadosAjax(View):
    def get(self, request):
        request_id = request.GET.get("id", None)
        if request_id:
            sub_estados = SubTipoLlamado.objects.filter(fk_tipo_llamado=request_id)
        else:
            sub_estados = SubTipoLlamado.objects.all()
        data = [
            {"id": sub_estado.id, "text": sub_estado.nombre}
            for sub_estado in sub_estados
        ]
        return JsonResponse(data, safe=False)


class TipoEstadosLlamadosAjax(View):
    def get(self, request):
        request_id = request.GET.get("id", None)
        if request_id:
            sub_estados = TipoLlamado.objects.filter(fk_programas_llamados=request_id)
        else:
            sub_estados = TipoLlamado.objects.all()
        data = [
            {"id": sub_estado.id, "text": sub_estado.nombre}
            for sub_estado in sub_estados
        ]
        return JsonResponse(data, safe=False)
