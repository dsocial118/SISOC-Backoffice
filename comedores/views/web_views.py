import json
from typing import Any
from django.contrib import messages
from django.db.models.base import Model
from django.forms import BaseModelForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    TemplateView,
    View,
)


from comedores.forms.comedor_form import ComedorForm, ReferenteForm, IntervencionForm

from comedores.forms.observacion_form import ObservacionForm
from comedores.forms.relevamiento_form import (
    ColaboradoresForm,
    EspacioCocinaForm,
    EspacioForm,
    EspacioPrestacionForm,
    FuenteComprasForm,
    FuenteRecursosForm,
    FuncionamientoPrestacionForm,
    PrestacionForm,
    RelevamientoForm,
)

from comedores.models import (
    Comedor,
    ImagenComedor,
    Observacion,
    Prestacion,
    Relevamiento,
    Intervencion,
    SubIntervencion,
    Territorial,
    ValorComida,
)

from comedores.services.comedor_service import ComedorService
from comedores.services.relevamiento_service import RelevamientoService
from usuarios.models import Usuarios


def SubEstadosIntervencionesAJax(request):
    request_id = request.GET.get("id")
    if request_id:
        sub_estados = SubIntervencion.objects.filter(fk_subintervencion=request_id)
    else:
        sub_estados = SubIntervencion.objects.all()

    data = [
        {"id": sub_estado.id, "text": sub_estado.nombre} for sub_estado in sub_estados
    ]
    return JsonResponse(data, safe=False)


class IntervencionDetail(TemplateView):
    template_name = "comedor/intervencion_detail.html"
    model = Intervencion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comedor = Comedor.objects.values(
            "id", "gestionar_uid", "nombre", "provincia", "barrio", "calle", "numero"
        ).get(pk=self.kwargs["pk"])
        intervenciones = Intervencion.objects.filter(fk_comedor=self.kwargs["pk"])
        cantidad_intervenciones = Intervencion.objects.filter(
            fk_comedor=self.kwargs["pk"]
        ).count()
        context["intervenciones"] = intervenciones
        context["object"] = comedor
        context["cantidad_intervenciones"] = cantidad_intervenciones

        return context


class IntervencionCreateView(CreateView):
    model = Intervencion
    template_name = "comedor/intervencion_form.html"
    form_class = IntervencionForm

    def form_valid(self, form):
        pk = self.kwargs["pk"]
        form.save()
        return redirect("intervencion_ver", pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comedor = Comedor.objects.values(
            "id", "gestionar_uid", "nombre", "provincia", "barrio", "calle", "numero"
        ).get(pk=self.kwargs["pk"])

        context["form"] = self.get_form()
        context["object"] = comedor

        return context


class IntervencionDeleteView(DeleteView):
    model = Intervencion
    template_name = "comedor/intervencion_confirm_delete.html"

    def form_valid(self, form):
        self.object.delete()
        return redirect("intervencion_ver", pk=self.kwargs["pk2"])


class IntervencionUpdateView(UpdateView):
    model = Intervencion
    form_class = IntervencionForm
    template_name = "comedor/intervencion_form.html"

    def form_valid(self, form):
        pk = self.kwargs["pk2"]
        form.save()
        return redirect("intervencion_ver", pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comedor = Comedor.objects.values(
            "id", "gestionar_uid", "nombre", "provincia", "barrio", "calle", "numero"
        ).get(pk=self.kwargs["pk2"])
        context["form"] = self.get_form()
        context["object"] = comedor
        return context


class ComedorListView(ListView):
    model = Comedor
    template_name = "comedor/comedor_list.html"
    context_object_name = "comedores"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("busqueda")
        return ComedorService.get_comedores_filtrados(query)


class ComedorCreateView(CreateView):
    model = Comedor
    form_class = ComedorForm
    template_name = "comedor/comedor_form.html"

    def get_success_url(self):
        return reverse("comedor_detalle", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["referente_form"] = ReferenteForm(
            self.request.POST or None, prefix="referente"
        )
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        referente_form = context["referente_form"]
        imagenes = self.request.FILES.getlist("imagenes")

        if referente_form.is_valid():  # Creo y asigno el referente
            self.object = form.save(commit=False)
            self.object.referente = referente_form.save()
            self.object.save()

            for imagen in imagenes:  # Creo las imagenes
                try:
                    ComedorService.create_imagenes(imagen, self.object.pk)
                except Exception:
                    return self.form_invalid(form)

            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ComedorDetailView(DetailView):
    model = Comedor
    template_name = "comedor/comedor_detail.html"
    context_object_name = "comedor"

    def get_object(self, queryset=None):
        return ComedorService.get_comedor_detail_object(self.kwargs["pk"])

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        beneficiarios = Relevamiento.objects.filter(comedor=self.object["id"]).first()
        if beneficiarios == None:
            countDesayuno = 0
            countAlmuerzo = 0
            countMerienda = 0
            countCena = 0
        else:
            if beneficiarios.prestacion:
                countDesayuno = (
                    (beneficiarios.prestacion.lunes_desayuno_actual or 0)
                    + (beneficiarios.prestacion.martes_desayuno_actual or 0)
                    + (beneficiarios.prestacion.miercoles_desayuno_actual or 0)
                    + (beneficiarios.prestacion.jueves_almuerzo_actual or 0)
                    + (beneficiarios.prestacion.viernes_desayuno_actual or 0)
                    + (beneficiarios.prestacion.sabado_desayuno_actual or 0)
                    + (beneficiarios.prestacion.domingo_desayuno_actual or 0)
                )

                countAlmuerzo = (
                    (beneficiarios.prestacion.lunes_almuerzo_actual or 0)
                    + (beneficiarios.prestacion.martes_almuerzo_actual or 0)
                    + (beneficiarios.prestacion.miercoles_almuerzo_actual or 0)
                    + (beneficiarios.prestacion.jueves_almuerzo_actual or 0)
                    + (beneficiarios.prestacion.viernes_almuerzo_actual or 0)
                    + (beneficiarios.prestacion.sabado_almuerzo_actual or 0)
                    + (beneficiarios.prestacion.domingo_almuerzo_actual or 0)
                )
                countMerienda = (
                    (beneficiarios.prestacion.lunes_merienda_actual or 0)
                    + (beneficiarios.prestacion.martes_merienda_actual or 0)
                    + (beneficiarios.prestacion.miercoles_merienda_actual or 0)
                    + (beneficiarios.prestacion.jueves_merienda_actual or 0)
                    + (beneficiarios.prestacion.viernes_merienda_actual or 0)
                    + (beneficiarios.prestacion.sabado_merienda_actual or 0)
                    + (beneficiarios.prestacion.domingo_merienda_actual or 0)
                )
                countCena = (
                    (beneficiarios.prestacion.lunes_cena_actual or 0)
                    + (beneficiarios.prestacion.martes_cena_actual or 0)
                    + (beneficiarios.prestacion.miercoles_cena_actual or 0)
                    + (beneficiarios.prestacion.jueves_cena_actual or 0)
                    + (beneficiarios.prestacion.viernes_cena_actual or 0)
                    + (beneficiarios.prestacion.sabado_cena_actual or 0)
                    + (beneficiarios.prestacion.domingo_cena_actual or 0)
                )
            else:
                countDesayuno = 0
                countAlmuerzo = 0
                countMerienda = 0
                countCena = 0
        countBeneficiarios = countDesayuno + countAlmuerzo + countMerienda + countCena

        valorCena = countCena * ValorComida.objects.get(tipo="Cena").valor
        valorDesayuno = countDesayuno * ValorComida.objects.get(tipo="Desayuno").valor
        valorAlmuerzo = countAlmuerzo * ValorComida.objects.get(tipo="Almuerzo").valor
        valorMerienda = countMerienda * ValorComida.objects.get(tipo="Merienda").valor

        territoriales = ComedorService.get_territoriales(self.object["id"])

        context.update(
            {
                "relevamientos": Relevamiento.objects.filter(comedor=self.object["id"])
                .values("id", "fecha_visita", "estado")
                .order_by("-fecha_visita")[:3],
                "territoriales": territoriales,
                "observaciones": Observacion.objects.filter(comedor=self.object["id"])
                .values("id", "fecha_visita")
                .order_by("-fecha_visita")[:3],
                "countRelevamientos": Relevamiento.objects.filter(
                    comedor=self.object["id"]
                ).count(),
                "countBeneficiarios": countBeneficiarios,
                "presupuestoDesayuno": valorDesayuno,
                "presupuestoAlmuerzo": valorAlmuerzo,
                "presupuestoMerienda": valorMerienda,
                "presupuestoCena": valorCena,
                "imagenes": ImagenComedor.objects.filter(
                    comedor=self.object["id"]
                ).values("imagen"),
            }
        )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            relevamiento = Relevamiento()
            relevamiento.comedor = get_object_or_404(Comedor, id=self.object["id"])
            relevamiento.estado = "Pendiente"

            if request.POST.get("territorial"):
                gestionar_uid = json.loads(request.POST.get("territorial"))[
                    "gestionar_uid"
                ]
                nombre = json.loads(request.POST.get("territorial"))["nombre"]
                if gestionar_uid and nombre:
                    territorial, _created = Territorial.objects.get_or_create(
                        gestionar_uid=gestionar_uid, defaults={"nombre": nombre}
                    )
                    relevamiento.territorial = territorial
                    relevamiento.estado = "Visita pendiente"

            relevamiento.save()
            return redirect(
                reverse(
                    "relevamiento_detalle",
                    kwargs={
                        "pk": relevamiento.pk,
                        "comedor_pk": relevamiento.comedor.pk,
                    },
                )
            )
        except Exception as e:
            messages.error(request, f"Error al crear el relevamiento: {e}")
            return redirect("comedor_detalle", pk=self.object["id"])


class ComedorUpdateView(UpdateView):
    model = Comedor
    form_class = ComedorForm
    template_name = "comedor/comedor_form.html"

    def get_success_url(self):
        return reverse("comedor_detalle", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        self.object = self.get_object()
        data["referente_form"] = ReferenteForm(
            self.request.POST if self.request.POST else None,
            instance=self.object.referente,
            prefix="referente",
        )
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        referente_form = context["referente_form"]
        imagenes = self.request.FILES.getlist("imagenes")

        if referente_form.is_valid():  # Creo y asigno el referente
            self.object = form.save()
            self.object.referente = referente_form.save()
            self.object.save()

            for imagen in imagenes:  # Creo las imagenes
                try:
                    ComedorService.create_imagenes(imagen, self.object.pk)
                except Exception:
                    return self.form_invalid(form)

            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ComedorDeleteView(DeleteView):
    model = Comedor
    template_name = "comedor/comedor_confirm_delete.html"
    context_object_name = "comedor"
    success_url = reverse_lazy("comedores")


class RelevamientoListView(ListView):
    model = Relevamiento
    template_name = "relevamiento/relevamiento_list.html"
    context_object_name = "relevamientos"

    def get_queryset(self):
        comedor = self.kwargs["comedor_pk"]
        return (
            Relevamiento.objects.filter(comedor=comedor)
            .order_by("-fecha_visita")
            .values("id", "fecha_visita", "estado")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comedor"] = Comedor.objects.values(
            "id",
            "nombre",
            "provincia__nombre",
            "localidad__nombre",
            "municipio__nombre",
        ).get(pk=self.kwargs["comedor_pk"])

        return context


class RelevamientoCreateView(CreateView):
    model = Relevamiento
    form_class = RelevamientoForm
    template_name = "relevamiento/relevamiento_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["comedor_pk"] = self.kwargs["comedor_pk"]
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        forms = {
            "funcionamiento_form": FuncionamientoPrestacionForm,
            "espacio_form": EspacioForm,
            "espacio_cocina_form": EspacioCocinaForm,
            "espacio_prestacion_form": EspacioPrestacionForm,
            "colaboradores_form": ColaboradoresForm,
            "recursos_form": FuenteRecursosForm,
            "compras_form": FuenteComprasForm,
            "prestacion_form": PrestacionForm,
        }

        for form_name, form_class in forms.items():
            data[form_name] = form_class(
                self.request.POST if self.request.POST else None
            )

        data["comedor"] = Comedor.objects.values("id", "nombre").get(
            pk=self.kwargs["comedor_pk"]
        )

        return data

    def form_valid(self, form):
        context = self.get_context_data()
        forms = {
            "funcionamiento_form": context["funcionamiento_form"],
            "espacio_form": context["espacio_form"],
            "espacio_cocina_form": context["espacio_cocina_form"],
            "espacio_prestacion_form": context["espacio_prestacion_form"],
            "colaboradores_form": context["colaboradores_form"],
            "recursos_form": context["recursos_form"],
            "compras_form": context["compras_form"],
            "prestacion_form": context["prestacion_form"],
        }

        if all(form.is_valid() for form in forms.values()):
            self.object = RelevamientoService.populate_relevamiento(
                form, forms, self.request.user.id
            )

            return redirect(
                "relevamiento_detalle",
                comedor_pk=int(self.object.comedor.id),
                pk=int(self.object.id),
            )
        else:
            self.error_message(forms)
            return self.form_invalid(form)

    def error_message(self, forms):
        for form_name, form_instance in forms.items():
            if not form_instance.is_valid():
                messages.error(
                    self.request, f"Errores en {form_name}: {form_instance.errors}"
                )


class RelevamientoDetailView(DetailView):
    model = Relevamiento
    template_name = "relevamiento/relevamiento_detail.html"
    context_object_name = "relevamiento"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        relevamiento = Relevamiento.objects.get(pk=self.get_object()["id"])
        context["relevamiento"]["gas"] = (
            RelevamientoService.separate_m2m_string(
                relevamiento.espacio.cocina.abastecimiento_combustible.all()
            )
            if relevamiento.espacio
            else None
        )
        context["prestacion"] = (
            Prestacion.objects.get(pk=relevamiento.prestacion.id)
            if relevamiento.prestacion
            else None
        )

        return context

    def get_object(self, queryset=None) -> Model:
        return RelevamientoService.get_relevamiento_detail_object(self.kwargs["pk"])


class RelevamientoUpdateView(UpdateView):
    model = Relevamiento
    form_class = RelevamientoForm
    template_name = "relevamiento/relevamiento_form.html"
    success_url = reverse_lazy("relevamiento_lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["comedor_pk"] = self.kwargs["comedor_pk"]
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        forms = {
            "funcionamiento_form": FuncionamientoPrestacionForm,
            "espacio_form": EspacioForm,
            "espacio_cocina_form": EspacioCocinaForm,
            "espacio_prestacion_form": EspacioPrestacionForm,
            "colaboradores_form": ColaboradoresForm,
            "recursos_form": FuenteRecursosForm,
            "compras_form": FuenteComprasForm,
            "prestacion_form": PrestacionForm,
        }

        for form_name, form_class in forms.items():
            data[form_name] = form_class(
                self.request.POST if self.request.POST else None,
                instance=getattr(
                    self.object, form_name.split("_form", maxsplit=1)[0], None
                ),
            )

        data["comedor"] = Comedor.objects.values("id", "nombre").get(
            pk=self.kwargs["comedor_pk"]
        )
        data["espacio_cocina_form"] = EspacioCocinaForm(
            self.request.POST if self.request.POST else None,
            instance=getattr(self.object.espacio, "cocina", None),
        )
        data["espacio_prestacion_form"] = EspacioPrestacionForm(
            self.request.POST if self.request.POST else None,
            instance=getattr(self.object.espacio, "prestacion", None),
        )
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        forms = {
            "funcionamiento_form": context["funcionamiento_form"],
            "espacio_form": context["espacio_form"],
            "espacio_cocina_form": context["espacio_cocina_form"],
            "espacio_prestacion_form": context["espacio_prestacion_form"],
            "colaboradores_form": context["colaboradores_form"],
            "recursos_form": context["recursos_form"],
            "compras_form": context["compras_form"],
            "prestacion_form": context["prestacion_form"],
        }

        if all(form.is_valid() for form in forms.values()):
            self.object = RelevamientoService.populate_relevamiento(
                form, forms, self.request.user.id
            )

            return redirect(
                "relevamiento_detalle",
                comedor_pk=int(self.object.comedor.id),
                pk=int(self.object.id),
            )
        else:
            self.error_message(forms)
            return self.form_invalid(form)

    def error_message(self, forms):
        for form_name, form_instance in forms.items():
            if not form_instance.is_valid():
                messages.error(
                    self.request, f"Errores en {form_name}: {form_instance.errors}"
                )


class RelevamientoDeleteView(DeleteView):
    model = Relevamiento
    template_name = "relevamiento/relevamiento_confirm_delete.html"
    context_object_name = "relevamiento"

    def get_success_url(self):
        comedor = self.object.comedor

        return reverse_lazy("comedor_detalle", kwargs={"pk": comedor.id})


class ObservacionCreateView(CreateView):
    model = Observacion
    form_class = ObservacionForm
    template_name = "observacion/observacion_form.html"
    context_object_name = "observacion"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "comedor": Comedor.objects.values("id", "nombre").get(
                    pk=self.kwargs["comedor_pk"]
                )
            }
        )

        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.comedor_id = Comedor.objects.get(pk=self.kwargs["comedor_pk"]).id
        usuario = Usuarios.objects.get(pk=self.request.user.id).usuario
        form.instance.observador = f"{usuario.first_name} {usuario.last_name}"
        form.instance.fecha_visita = timezone.now()

        self.object = form.save()

        return redirect(
            "observacion_detalle",
            comedor_pk=int(self.kwargs["comedor_pk"]),
            pk=int(self.object.id),
        )


class ObservacionDetailView(DetailView):
    model = Observacion
    template_name = "observacion/observacion_detail.html"
    context_object_name = "observacion"

    def get_object(self, queryset=None) -> Model:
        return (
            Observacion.objects.prefetch_related("comedor")
            .values(
                "id",
                "fecha_visita",
                "observacion",
                "comedor__id",
                "comedor__nombre",
                "observador",
            )
            .get(pk=self.kwargs["pk"])
        )


class ObservacionUpdateView(UpdateView):
    model = Observacion
    form_class = ObservacionForm
    template_name = "observacion/observacion_form.html"
    context_object_name = "observacion"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        comedor = Comedor.objects.values("id", "nombre").get(
            pk=self.kwargs["comedor_pk"]
        )

        context.update({"comedor": comedor})

        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.comedor_id = Comedor.objects.get(pk=self.kwargs["comedor_pk"]).id
        usuario = Usuarios.objects.get(pk=self.request.user.id).usuario
        form.instance.observador = f"{usuario.first_name} {usuario.last_name}"
        form.instance.fecha_visita = timezone.now()

        self.object = form.save()

        return redirect(
            "observacion_detalle",
            comedor_pk=int(self.kwargs["comedor_pk"]),
            pk=int(self.object.id),
        )


class ObservacionDeleteView(DeleteView):
    model = Observacion
    template_name = "observacion/observacion_confirm_delete.html"
    context_object_name = "observacion"

    def get_success_url(self):
        comedor = self.object.comedor

        return reverse_lazy("comedor_detalle", kwargs={"pk": comedor.id})
