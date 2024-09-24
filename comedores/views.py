from typing import Any
from django.db.models.base import Model
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)

from comedores.forms.comedor import ComedorForm, ReferenteForm
from comedores.forms.relevamiento import (
    RelevamientoForm,
    FuncionamientoPrestacionForm,
    EspacioForm,
    EspacioCocinaForm,
    EspacioPrestacionForm,
    ColaboradoresForm,
    FuenteRecursosForm,
    FuenteComprasForm,
    PrestacionFormSet,
)
from .models import Comedor, Relevamiento


class ComedorListView(ListView):
    model = Comedor
    template_name = "comedor/comedor_list.html"
    context_object_name = "comedores"
    paginate_by = 10

    def get_queryset(self):
        return Comedor.objects.prefetch_related("provincia", "referente").values(
            "id",
            "nombre",
            "provincia__nombre",
            "calle",
            "numero",
            "referente__nombre",
            "referente__apellido",
            "referente__numero",
        )


class ComedorCreateView(CreateView):
    model = Comedor
    form_class = ComedorForm
    template_name = "comedor/comedor_form.html"

    def get_success_url(self):
        return reverse("comedor_detalle", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["referente_form"] = ReferenteForm(self.request.POST)
        else:
            data["referente_form"] = ReferenteForm()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        referente_form = context["referente_form"]

        if referente_form.is_valid():
            self.object = form.save()
            referente = referente_form.save()

            self.object.referente = referente
            self.object.save()

            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ComedorDetailView(DetailView):
    model = Comedor
    template_name = "comedor/comedor_detail.html"
    context_object_name = "comedor"

    def get_object(self, queryset=None):
        return (
            Comedor.objects.select_related("provincia", "referente")
            .values(
                "id",
                "nombre",
                "comienzo",
                "provincia__nombre",
                "municipio__nombre_region",
                "localidad__nombre",
                "partido",
                "barrio",
                "calle",
                "numero",
                "entre_calle_1",
                "entre_calle_2",
                "codigo_postal",
                "referente__nombre",
                "referente__apellido",
                "referente__mail",
                "referente__numero",
                "referente__documento",
            )
            .get(pk=self.kwargs["pk"])
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Utiliza el diccionario self.object para acceder al id del comedor
        context["relevamientos"] = (
            Relevamiento.objects.filter(comedor=self.object["id"])
            .values("id", "fecha_visita")
            .order_by("fecha_visita")[:12]
        )

        return context


class ComedorUpdateView(UpdateView):
    model = Comedor
    form_class = ComedorForm
    template_name = "comedor/comedor_form.html"

    def get_success_url(self):
        return reverse("comedor_detalle", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        self.object = self.get_object()
        if self.request.POST:
            data["referente_form"] = ReferenteForm(
                self.request.POST, instance=self.object.referente
            )
        else:
            data["referente_form"] = ReferenteForm(instance=self.object.referente)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        referente_form = context["referente_form"]

        if referente_form.is_valid():
            self.object = form.save()
            referente = referente_form.save()

            self.object.referente = referente
            self.object.save()

            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ComedorDeleteView(DeleteView):
    model = Comedor
    template_name = "comedor/comedor_confirm_delete.html"
    context_object_name = "comedor"
    success_url = reverse_lazy("comedores")


class RelevamientoCreateView(CreateView):
    model = Relevamiento
    form_class = RelevamientoForm
    template_name = "relevamiento/relevamiento_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["pk"] = self.kwargs["pk"]
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
        }

        for form_name, form_class in forms.items():
            if self.request.POST:
                data[form_name] = form_class(self.request.POST)
            else:
                data[form_name] = form_class()

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
        }

        if all(form.is_valid() for form in forms.values()):
            self.object = form.save(commit=False)

            funcionamiento = forms["funcionamiento_form"].save()
            self.object.funcionamiento = funcionamiento

            espacio = forms["espacio_form"].save(commit=False)
            cocina = forms["espacio_cocina_form"].save(commit=True)
            espacio.cocina = cocina
            prestacion = forms["espacio_prestacion_form"].save(commit=True)
            espacio.prestacion = prestacion
            espacio.save()
            self.object.espacio = espacio

            colaboradores = forms["colaboradores_form"].save()
            self.object.colaboradores = colaboradores

            recursos = forms["recursos_form"].save()
            self.object.recursos = recursos

            compras = forms["compras_form"].save()
            self.object.compras = compras

            self.object.save()

            return redirect("relevamiento_detalle", pk=int(self.object.id))
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

    def get_object(self, queryset=None) -> Model:
        return (
            Relevamiento.objects.prefetch_related(
                "comedor",
                "funcionamiento",
                "espacio",
                "colaboradores",
                "recursos",
                "compras",
            )
            .filter(pk=self.kwargs["pk"])
            .values(
                "id",
                "comedor__nombre",
                "fecha_visita",
                "comedor__comienzo",
                "funcionamiento__modalidad_prestacion__nombre",
                "funcionamiento__servicio_por_turnos",
                "funcionamiento__cantidad_turnos",
                "comedor__id",
                "comedor__calle",
                "comedor__numero",
                "comedor__entre_calle_1",
                "comedor__entre_calle_2",
                "comedor__provincia__nombre",
                "comedor__municipio__nombre_region",
                "comedor__localidad__nombre",
                "comedor__partido",
                "comedor__barrio",
                "comedor__codigo_postal",
                "comedor__referente__nombre",
                "comedor__referente__apellido",
                "comedor__referente__mail",
                "comedor__referente__numero",
                "comedor__referente__documento",
                "espacio__tipo_espacio_fisico__nombre",
                "espacio__espacio_fisico_otro",
                "espacio__cocina__espacio_elaboracion_alimentos",
                "espacio__cocina__almacenamiento_alimentos_secos",
                "espacio__cocina__refrigerador",
                "espacio__cocina__recipiente_residuos_organicos",
                "espacio__cocina__recipiente_residuos_reciclables",
                "espacio__cocina__recipiente_otros_residuos",
                "espacio__cocina__abastecimiento_combustible__nombre",
                "espacio__cocina__abastecimiento_agua__nombre",
                "espacio__cocina__instalacion_electrica",
                "espacio__prestacion__espacio_equipado",
                "espacio__prestacion__tiene_ventilacion",
                "espacio__prestacion__tiene_salida_emergencia",
                "espacio__prestacion__salida_emergencia_senializada",
                "espacio__prestacion__tiene_equipacion_incendio",
                "espacio__prestacion__tiene_botiquin",
                "espacio__prestacion__tiene_buena_iluminacion",
                "espacio__prestacion__tiene_sanitarios",
                "espacio__prestacion__desague_hinodoro",
                "espacio__prestacion__tiene_buzon_quejas",
                "espacio__prestacion__tiene_gestion_quejas",
                "espacio__prestacion__frecuencia_limpieza__nombre",
                "colaboradores__cantidad_colaboradores__nombre",
                "colaboradores__colaboradores_capacitados_alimentos",
                "colaboradores__colaboradores_recibieron_capacitacion_alimentos",
                "colaboradores__colaboradores_capacitados_salud_seguridad",
                "colaboradores__colaboradores_recibieron_capacitacion_emergencias",
                "colaboradores__colaboradores_recibieron_capacitacion_violencia",
                "recursos__recibe_donaciones_particulares",
                "recursos__frecuencia_donaciones_particulares__nombre",
                "recursos__recursos_donaciones_particulares__nombre",
                "recursos__recibe_estado_nacional",
                "recursos__frecuencia_estado_nacional__nombre",
                "recursos__recursos_estado_nacional__nombre",
                "recursos__recibe_estado_provincial",
                "recursos__frecuencia_estado_provincial__nombre",
                "recursos__recursos_estado_provincial__nombre",
                "recursos__recibe_estado_municipal",
                "recursos__frecuencia_estado_municipal__nombre",
                "recursos__recursos_estado_municipal__nombre",
                "recursos__recibe_otros",
                "recursos__frecuencia_otros__nombre",
                "recursos__recursos_otros__nombre",
                "compras__almacen_cercano",
                "compras__verduleria",
                "compras__granja",
                "compras__carniceria",
                "compras__pescaderia",
                "compras__supermercado",
                "compras__mercado_central",
                "compras__ferias_comunales",
                "compras__mayoristas",
                "compras__otro",
            )
            .first()
        )


class RelevamientoDeleteView(DeleteView):
    model = Relevamiento
    template_name = "relevamiento/relevamiento_confirm_delete.html"
    context_object_name = "relevamiento"

    def get_success_url(self):
        comedor = self.object.comedor

        return reverse_lazy("comedor_detalle", kwargs={"pk": comedor.id})