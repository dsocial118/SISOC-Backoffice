import os
import re
from typing import Union

from django.db.models import Q
import requests

from comedores.forms.comedor_form import ImagenComedorForm
from comedores.models import Comedor, Referente, Territorial
from config import settings
from configuraciones.models import Municipio, Provincia
from configuraciones.models import Localidad


class ComedorService:
    @staticmethod
    def get_comedores_filtrados(query: Union[str, None] = None):
        queryset = Comedor.objects.prefetch_related("provincia", "referente").values(
            "id",
            "nombre",
            "provincia__nombre",
            "municipio__nombre",
            "localidad__nombre",
            "barrio",
            "partido",
            "calle",
            "numero",
            "referente__nombre",
            "referente__apellido",
            "referente__celular",
        )
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query)
                | Q(provincia__nombre__icontains=query)
                | Q(municipio__nombre__icontains=query)
                | Q(localidad__nombre__icontains=query)
                | Q(barrio__icontains=query)
                | Q(calle__icontains=query)
            )
        return queryset

    @staticmethod
    def get_comedor_detail_object(comedor_id: int):
        return (
            Comedor.objects.select_related("provincia", "referente")
            .values(
                "id",
                "foto_legajo",
                "nombre",
                "comienzo",
                "provincia__nombre",
                "municipio__nombre",
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
                "referente__celular",
                "referente__documento",
            )
            .get(pk=comedor_id)
        )

    @staticmethod
    def get_ubicaciones_ids(data):
        if "provincia" in data:
            provincia_obj = Provincia.objects.filter(
                nombre__iexact=data["provincia"]
            ).first()
            data["provincia"] = provincia_obj.id if provincia_obj else ""

        if "municipio" in data:
            municipio_obj = Municipio.objects.filter(
                nombre__iexact=data["municipio"]
            ).first()
            data["municipio"] = municipio_obj.id if municipio_obj else ""

        if "localidad" in data:
            localidad_obj = Localidad.objects.filter(
                nombre__iexact=data["localidad"]
            ).first()
            data["localidad"] = localidad_obj.id if localidad_obj else ""

        return data

    @staticmethod
    def create_or_update_referente(data, referente_instance=None):
        referente_data = data.get("referente", {})

        if "celular" in referente_data:
            referente_data["celular"] = referente_data["celular"].replace("-", "")
        if "documento" in referente_data:
            referente_data["documento"] = referente_data["documento"].replace(".", "")

        if referente_instance is None:  # Crear referente
            referente_instance = Referente.objects.create(**referente_data)
        else:  # Actualizar referente
            for field, value in referente_data.items():
                setattr(referente_instance, field, value)
            referente_instance.save()

        return referente_instance

    @staticmethod
    def create_imagenes(imagen, comedor_pk):
        imagen_comedor = ImagenComedorForm(
            {"comedor": comedor_pk},
            {"imagen": imagen},
        )
        if imagen_comedor.is_valid():
            return imagen_comedor.save()
        else:
            return imagen_comedor.errors

    @staticmethod
    def send_to_gestionar(comedor: Comedor):
        if comedor.gestionar_uid is None:
            data = {
                "Action": "Add",
                "Properties": {"Locale": "es-ES"},
                "Rows": [
                    {
                        "ComedorID": comedor.id,
                        "ID_Sisoc": comedor.id,
                        "nombre": comedor.nombre,
                        "comienzo": f"01/01/{comedor.comienzo}",
                        "calle": comedor.calle,
                        "numero": comedor.numero,
                        "entre_calle_1": comedor.entre_calle_1,
                        "entre_calle_2": comedor.entre_calle_2,
                        "provincia": (
                            comedor.provincia.nombre if comedor.provincia else ""
                        ),
                        "municipio": (
                            comedor.municipio.nombre if comedor.municipio else ""
                        ),
                        "localidad": (
                            comedor.localidad.nombre if comedor.localidad else ""
                        ),
                        "partido": comedor.partido,
                        "barrio": comedor.barrio,
                        "codigo_postal": comedor.codigo_postal,
                        "Referente": (
                            comedor.referente.documento if comedor.referente else ""
                        ),
                        "Imagen": f"{os.getenv('DOMINIO')}/media/{comedor.foto_legajo}",
                    }
                ],
            }

            headers = {
                "applicationAccessKey": os.getenv("GESTIONAR_API_KEY"),
            }

            try:
                response = requests.post(
                    os.getenv("GESTIONAR_API_CREAR_COMEDOR"),
                    json=data,
                    headers=headers,
                )
                response.raise_for_status()
                response = response.json()

                comedor.gestionar_uid = response["Rows"][0]["ComedorID"]
                comedor.save()
            except requests.exceptions.RequestException as e:
                print(f"Error en la petición POST: {e}")

    @staticmethod
    def get_territoriales(comedor_id: int):
        data = {
            "Action": "Find",
            "Properties": {"Locale": "es-ES"},
            "Rows": [{"ComedorID": comedor_id}],
        }

        headers = {
            "applicationAccessKey": os.getenv("GESTIONAR_API_KEY"),
        }

        try:
            response = requests.post(
                os.getenv("GESTIONAR_API_CREAR_COMEDOR"),
                json=data,
                headers=headers,
            )
            response.raise_for_status()
            response = response.json()

            territoriales = []
            territoriales_data = [
                {"gestionar_uid": uid, "nombre": nombre.strip()}
                for uid, nombre in re.findall(
                    r"(\w+)/ ([^,]+(?:,.*?[^,])?)",
                    response[0]["ListadoRelevadoresDisponibles"],
                )
            ]

            for territorial_data in territoriales_data:
                territorial, _created = Territorial.objects.get_or_create(
                    gestionar_uid=territorial_data["gestionar_uid"],
                    defaults={"nombre": territorial_data["nombre"]},
                )
                territoriales.append(territorial)

            return territoriales
        except requests.exceptions.RequestException as e:
            print(f"Error en la petición POST: {e}")
            return []
