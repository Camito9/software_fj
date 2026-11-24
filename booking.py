from typing import List
from entities import Cliente
from exceptions import (
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    SoftwareFJError,
)
from services import AlquilerEquipo, Servicio


class Reserva:
    """Integra cliente, servicio, duración y estado, gestionando su ciclo de vida."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA")

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: float,
        unidades: int = 1,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> None:
        if not isinstance(id_reserva, str) or not id_reserva.strip():
            raise ReservaInvalidaError("El ID de la reserva es obligatorio.")
        if not isinstance(cliente, Cliente) or not cliente.activo:
            raise ReservaInvalidaError("La reserva requiere un cliente válido y activo.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un servicio válido.")

        try:
            servicio.verificar_disponibilidad()
            costo = servicio.calcular_costo(
                duracion_horas=duracion_horas,
                unidades=unidades,
                descuento_pct=descuento_pct,
                impuesto_pct=impuesto_pct,
            )
        except SoftwareFJError as exc:
            raise ReservaInvalidaError(
                f"No se pudo crear la reserva '{id_reserva}': {exc}"
            ) from exc

        self._id_reserva = id_reserva.strip().upper()
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = float(duracion_horas)
        self._unidades = unidades
        self._costo_total = costo
        self._estado = "PENDIENTE"

    @property
    def id_reserva(self) -> str:
        return self._id_reserva

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    def confirmar(self) -> None:
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError(
                f"Solo se pueden confirmar reservas PENDIENTES. Estado actual de '{self._id_reserva}': {self._estado}."
            )
        try:
            self._servicio.verificar_disponibilidad()
            if isinstance(self._servicio, AlquilerEquipo):
                self._servicio.reservar_stock(self._unidades)
        except ServicioNoDisponibleError as exc:
            raise OperacionNoPermitidaError(
                f"No se pudo confirmar la reserva '{self._id_reserva}' por falta de disponibilidad."
            ) from exc

        self._estado = "CONFIRMADA"

    def cancelar(self) -> None:
        if self._estado == "PROCESADA":
            raise OperacionNoPermitidaError(
                f"No se puede cancelar la reserva '{self._id_reserva}' porque ya fue PROCESADA."
            )
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError(
                f"La reserva '{self._id_reserva}' ya se encuentra CANCELADA."
            )
        if self._estado == "CONFIRMADA" and isinstance(self._servicio, AlquilerEquipo):
            self._servicio.liberar_stock(self._unidades)

        self._estado = "CANCELADA"

    def procesar(self) -> float:
        if self._estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(
                f"Solo se pueden procesar reservas CONFIRMADAS. Estado actual de '{self._id_reserva}': {self._estado}."
            )
        self._estado = "PROCESADA"
        return self._costo_total

    def resumen(self) -> str:
        return (
            f"Reserva [{self._id_reserva}] | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.codigo} | Duración: {self._duracion_horas}h | "
            f"Total: ${self._costo_total:,.2f} | Estado: {self._estado}"
        )


class SistemaSoftwareFJ:
    """Gestor en memoria (listas de objetos) con registro en archivo de logs."""

    def __init__(self, logger) -> None:
        self.logger = logger
        self.clientes: List[Cliente] = []
        self.servicios: List[Servicio] = []
        self.reservas: List[Reserva] = []

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        if any(c.id == cliente.id for c in self.clientes):
            raise OperacionNoPermitidaError(f"Ya existe un cliente con ID '{cliente.id}'.")
        self.clientes.append(cliente)
        self.logger.info(f"Cliente registrado: {cliente.resumen()}")
        return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        if any(s.codigo == servicio.codigo for s in self.servicios):
            raise OperacionNoPermitidaError(f"Ya existe un servicio con código '{servicio.codigo}'.")
        self.servicios.append(servicio)
        self.logger.info(f"Servicio registrado: {servicio.describir()}")
        return servicio

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        for c in self.clientes:
            if c.id == id_cliente.strip().upper():
                return c
        raise ReservaInvalidaError(f"Cliente con ID '{id_cliente}' no encontrado.")

    def buscar_servicio(self, codigo_servicio: str) -> Servicio:
        for s in self.servicios:
            if s.codigo == codigo_servicio.strip().upper():
                return s
        raise ReservaInvalidaError(f"Servicio con código '{codigo_servicio}' no encontrado.")

    def crear_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        codigo_servicio: str,
        duracion_horas: float,
        unidades: int = 1,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> Reserva:
        try:
            cliente = self.buscar_cliente(id_cliente)
            servicio = self.buscar_servicio(codigo_servicio)
            reserva = Reserva(
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion_horas=duracion_horas,
                unidades=unidades,
                descuento_pct=descuento_pct,
                impuesto_pct=impuesto_pct,
            )
        except SoftwareFJError as exc:
            raise ReservaInvalidaError(
                f"Fallo al registrar la reserva '{id_reserva}' para el cliente '{id_cliente}'."
            ) from exc

        self.reservas.append(reserva)
        self.logger.info(f"Reserva creada: {reserva.resumen()}")
        return reserva