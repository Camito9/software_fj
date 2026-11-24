from abc import ABC, abstractmethod
from exceptions import (
    CalculoInconsistenteError,
    DatoInvalidoError,
    ServicioNoDisponibleError,
)


class Servicio(ABC):
    """Clase abstracta que define el contrato común para los servicios de Software FJ."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
    ) -> None:
        if not isinstance(codigo, str) or not codigo.strip():
            raise DatoInvalidoError("El código del servicio es obligatorio.")
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise DatoInvalidoError("La tarifa base debe ser un número mayor que 0.")

        self._codigo = codigo.strip().upper()
        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        self._disponible = bool(valor)

    def verificar_disponibilidad(self) -> None:
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._codigo} - {self._nombre}' no se encuentra disponible."
            )

    def _calcular_importe_ajustado(
        self,
        subtotal: float,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        """Variante interna reutilizable para aplicar descuentos e impuestos de forma segura."""
        if subtotal <= 0:
            raise CalculoInconsistenteError("El subtotal calculado no puede ser menor o igual a 0.")
        if not (0 <= descuento_pct < 100):
            raise CalculoInconsistenteError("El descuento debe estar entre 0 y 99.99%.")
        if not (0 <= impuesto_pct <= 100):
            raise CalculoInconsistenteError("El impuesto debe estar entre 0 y 100%.")

        con_descuento = subtotal * (1 - descuento_pct / 100.0)
        total = con_descuento * (1 + impuesto_pct / 100.0)

        if total <= 0:
            raise CalculoInconsistenteError("El total calculado resultó inconsistente (<= 0).")
        return round(total, 2)

    @abstractmethod
    def validar_parametros(self, duracion_horas: float, unidades: int = 1) -> None:
        """Valida duración y parámetros específicos de cada servicio."""

    @abstractmethod
    def calcular_costo(
        self,
        duracion_horas: float,
        unidades: int = 1,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        """Calcula el costo con parámetros opcionales (descuento e impuesto)."""

    @abstractmethod
    def describir(self) -> str:
        """Describe las características del servicio."""


class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas de reuniones o capacitación."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        capacidad_personas: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if not isinstance(capacidad_personas, int) or capacidad_personas <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero mayor que 0.")
        self._capacidad_personas = capacidad_personas

    @property
    def capacidad_personas(self) -> int:
        return self._capacidad_personas

    def validar_parametros(self, duracion_horas: float, unidades: int = 1) -> None:
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise DatoInvalidoError("La duración de la reserva de sala debe ser mayor que 0 horas.")
        if duracion_horas > 12:
            raise DatoInvalidoError("Una sala no puede reservarse por más de 12 horas continuas.")
        if not isinstance(unidades, int) or unidades != 1:
            raise DatoInvalidoError("Para reserva de sala, la cantidad de salas debe ser 1.")

    def calcular_costo(
        self,
        duracion_horas: float,
        unidades: int = 1,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        self.validar_parametros(duracion_horas, unidades)
        subtotal = self.tarifa_base * float(duracion_horas)
        return self._calcular_importe_ajustado(subtotal, descuento_pct, impuesto_pct)

    def describir(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"[Sala] {self.codigo} - {self.nombre} | Capacidad: {self.capacidad_personas} pers. | "
            f"Tarifa/h: ${self.tarifa_base:,.2f} | {estado}"
        )


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos tecnológicos."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        stock_disponible: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if not isinstance(stock_disponible, int) or stock_disponible < 0:
            raise DatoInvalidoError("El stock de equipos no puede ser negativo.")
        self._stock_disponible = stock_disponible

    @property
    def stock_disponible(self) -> int:
        return self._stock_disponible

    def validar_parametros(self, duracion_horas: float, unidades: int = 1) -> None:
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0:
            raise DatoInvalidoError("La duración del alquiler de equipo debe ser mayor que 0 horas.")
        if not isinstance(unidades, int) or unidades <= 0:
            raise DatoInvalidoError("Debe alquilar al menos 1 equipo.")
        if unidades > self._stock_disponible:
            raise ServicioNoDisponibleError(
                f"Stock insuficiente para '{self.codigo}': solicitados {unidades}, disponibles {self._stock_disponible}."
            )

    def reservar_stock(self, unidades: int) -> None:
        self.verificar_disponibilidad()
        if unidades > self._stock_disponible:
            raise ServicioNoDisponibleError(f"No hay suficiente stock de '{self.nombre}'.")
        self._stock_disponible -= unidades
        if self._stock_disponible == 0:
            self._disponible = False

    def liberar_stock(self, unidades: int) -> None:
        if unidades > 0:
            self._stock_disponible += unidades
            self._disponible = True

    def calcular_costo(
        self,
        duracion_horas: float,
        unidades: int = 1,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        self.validar_parametros(duracion_horas, unidades)
        subtotal = self.tarifa_base * float(duracion_horas) * unidades
        return self._calcular_importe_ajustado(subtotal, descuento_pct, impuesto_pct)

    def describir(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"[Equipo] {self.codigo} - {self.nombre} | Stock: {self.stock_disponible} und. | "
            f"Tarifa/h/und: ${self.tarifa_base:,.2f} | {estado}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para asesorías técnicas o de software."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        tarifa_base: float,
        especialidad: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise DatoInvalidoError("La especialidad de la asesoría es obligatoria.")
        self._especialidad = especialidad.strip()

    @property
    def especialidad(self) -> str:
        return self._especialidad

    def validar_parametros(self, duracion_horas: float, unidades: int = 1) -> None:
        if not isinstance(duracion_horas, (int, float)) or duracion_horas < 1:
            raise DatoInvalidoError("La asesoría especializada requiere al menos 1 hora.")
        if not isinstance(unidades, int) or unidades != 1:
            raise DatoInvalidoError("Una asesoría se solicita por sesión (unidades = 1).")

    def calcular_costo(
        self,
        duracion_horas: float,
        unidades: int = 1,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> float:
        self.validar_parametros(duracion_horas, unidades)
        # Tarifa base por sesión + tarifa por hora adicional después de la primera hora
        horas_extra = max(0.0, float(duracion_horas) - 1.0)
        subtotal = self.tarifa_base + (horas_extra * self.tarifa_base * 0.75)
        return self._calcular_importe_ajustado(subtotal, descuento_pct, impuesto_pct)

    def describir(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"[Asesoría] {self.codigo} - {self.nombre} | Área: {self.especialidad} | "
            f"Tarifa base: ${self.tarifa_base:,.2f} | {estado}"
        )