from abc import ABC, abstractmethod
import re
from exceptions import DatoInvalidoError


class EntidadSistema(ABC):
    """Clase abstracta base para entidades generales del sistema."""

    def __init__(self, id_entidad: str) -> None:
        self._id = self._validar_id(id_entidad)

    @property
    def id(self) -> str:
        return self._id

    @staticmethod
    def _validar_id(valor: str) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("El ID de la entidad es obligatorio y debe ser texto.")
        return valor.strip().upper()

    @abstractmethod
    def resumen(self) -> str:
        """Retorna una representación resumida de la entidad."""


class Cliente(EntidadSistema):
    """Representa un cliente de Software FJ con datos encapsulados y validados."""

    def __init__(self, id_entidad: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(id_entidad)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self._activo = True

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 2:
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 2 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not isinstance(valor, str) or not re.match(patron, valor.strip()):
            raise DatoInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        limpio = re.sub(r"[\s\-()]", "", str(valor)) if valor is not None else ""
        if not limpio.isdigit() or not (7 <= len(limpio) <= 15):
            raise DatoInvalidoError(f"Teléfono inválido: '{valor}'. Debe tener entre 7 y 15 dígitos.")
        self._telefono = limpio

    @property
    def activo(self) -> bool:
        return self._activo

    def desactivar(self) -> None:
        self._activo = False

    def resumen(self) -> str:
        estado = "Activo" if self._activo else "Inactivo"
        return f"Cliente [{self.id}] {self.nombre} | Correo: {self.correo} | Tel: {self.telefono} | {estado}"