from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.shortcuts import redirect
from provincias.models import Proyecto, AnexoSocioProductivo, AbstractPersoneria
from provincias.forms import ProyectoForm, AnexoSocioProductivoForm, DatosProyectoForm, PersonaJuridicaForm, PersonaFisicaForm
from usuarios.models import Usuarios

class ProyectoCreateView(CreateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyecto_form.html'

    def form_valid(self, form):
        form.instance.creador = Usuarios.objects.get(pk=self.request.user.id)
        tipo_anexo = form.cleaned_data['tipo_anexo']
        if tipo_anexo == 'SOCIO_PRODUCTIVO':
            return redirect('anexo_create')
        elif tipo_anexo == 'FORMACION':
            return redirect('formacion_create')
        
        return  super().form_valid(form)


class ProyectoListView(ListView):
    model = Proyecto
    template_name = 'proyecto_list.html'
    context_object_name = 'proyectos'
    paginate_by = 10  # Paginación de 10 elementos por página

class ProyectoUpdateView(UpdateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = "proyecto_form.html"  # FIXME:

class ProyectoDeleteView(DeleteView):
    model = Proyecto
    template_name = 'proyecto_confirm_delete.html'
    success_url = reverse_lazy('proyecto_list')
class AnexoSocioProductivoCreateView(CreateView):
    model = AnexoSocioProductivo
    form_class = AnexoSocioProductivoForm
    template_name = 'anexo_socio_productivo_form.html'
    success_url = reverse_lazy('datos_proyecto_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['juridica_form'] = PersonaJuridicaForm(self.request.POST)
            context['fisica_form'] = PersonaFisicaForm(self.request.POST)
        else:
            context['juridica_form'] = PersonaJuridicaForm()
            context['fisica_form'] = PersonaFisicaForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        juridica_form = context['juridica_form']
        fisica_form = context['fisica_form']
        if form.cleaned_data['tipo_persona'] == 'juridica' and juridica_form.is_valid():
            juridica = juridica_form.save()
            form.instance.persona_juridica = juridica
        elif form.cleaned_data['tipo_persona'] == 'humana' and fisica_form.is_valid():
            fisica = fisica_form.save()
            form.instance.persona_fisica = fisica
        else:
            return self.form_invalid(form)
        response = super().form_valid(form)
        return redirect('datos_proyecto_create')

class DatosProyectoCreateView(CreateView):
    model = AbstractPersoneria
    form_class = DatosProyectoForm
    template_name = 'datos_proyecto_form.html'
    success_url = reverse_lazy('proyecto_list')  # Cambia esto según tu flujo
