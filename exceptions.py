class SoftwareFJError(Exception):
    """Excepción base para errores del dominio de Software FJ."""


class DatoInvalidoError(SoftwareFJError):
    """Error por datos inválidos o parámetros faltantes."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Error por transiciones de estado o acciones no permitidas."""


class ServicioNoDisponibleError(SoftwareFJError):
    """Error cuando un servicio no está disponible o no admite la solicitud."""


class ReservaInvalidaError(SoftwareFJError):
    """Error durante la creación, confirmación o procesamiento de reservas."""


class CalculoInconsistenteError(SoftwareFJError):
    """Error cuando un cálculo financiero o de duración resulta inválido."""