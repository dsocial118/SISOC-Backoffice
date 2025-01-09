from django.contrib import admin

from comedores.models import (
    CantidadColaboradores,
    Comedor,
    FrecuenciaLimpieza,
    FrecuenciaRecepcionRecursos,
    FuenteCompras,
    FuenteRecursos,
    Observacion,
    Prestacion,
    Relevamiento,
    TipoAgua,
    TipoCombustible,
    TipoDesague,
    TipoEspacio,
    TipoModalidadPrestacion,
    TipoRecurso,
    TipoGestionQuejas,
    ValorComida,
    Intervencion,
    SubIntervencion,
    TipoIntervencion,
    EstadosIntervencion,
    Nomina,
)

admin.site.register(TipoModalidadPrestacion)
admin.site.register(TipoEspacio)
admin.site.register(TipoCombustible)
admin.site.register(TipoAgua)
admin.site.register(TipoDesague)
admin.site.register(FrecuenciaLimpieza)
admin.site.register(CantidadColaboradores)
admin.site.register(FrecuenciaRecepcionRecursos)
admin.site.register(TipoGestionQuejas)
admin.site.register(TipoRecurso)
admin.site.register(FuenteRecursos)
admin.site.register(FuenteCompras)
admin.site.register(Prestacion)
admin.site.register(Comedor)
admin.site.register(Relevamiento)
admin.site.register(Observacion)
admin.site.register(ValorComida)
admin.site.register(Intervencion)
admin.site.register(SubIntervencion)
admin.site.register(TipoIntervencion)
admin.site.register(EstadosIntervencion)
admin.site.register(Nomina)
