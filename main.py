from booking import SistemaSoftwareFJ
from entities import Cliente
from exceptions import SoftwareFJError
from logger import configurar_logger
from services import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def ejecutar_operacion(titulo: str, logger, accion) -> None:
    print(f"\n--- {titulo} ---")
    try:
        resultado = accion()
    except SoftwareFJError as exc:
        logger.error(f"{titulo} | Error controlado: {exc}", exc_info=True)
        print(f"[ERROR CONTROLADO] {exc}")
    except Exception as exc:
        logger.critical(f"{titulo} | Error inesperado: {exc}", exc_info=True)
        print(f"[ERROR INESPERADO] {exc}")
    else:
        logger.info(f"{titulo} | Éxito: {resultado}")
        print(f"[ÉXITO] {resultado}")
    finally:
        print(f"[FIN DE OPERACIÓN] {titulo}")


def main() -> None:
    logger = configurar_logger("logs/software_fj.log")
    logger.info("=== INICIO DE SIMULACIÓN SOFTWARE FJ ===")
    sistema = SistemaSoftwareFJ(logger=logger)

    # 1. Registro válido de cliente #1
    ejecutar_operacion(
        "Op 1: Registro cliente válido (C01)",
        logger,
        lambda: sistema.registrar_cliente(
            Cliente("C01", "Laura Gómez", "laura.gomez@empresa.com", "3104567890")
        ).resumen(),
    )

    # 2. Registro inválido de cliente (correo y teléfono incorrectos)
    ejecutar_operacion(
        "Op 2: Registro cliente inválido",
        logger,
        lambda: sistema.registrar_cliente(
            Cliente("C02", "A", "correo-no-valido", "123")
        ).resumen(),
    )

    # 3. Registro válido de cliente #2
    ejecutar_operacion(
        "Op 3: Registro cliente válido (C03)",
        logger,
        lambda: sistema.registrar_cliente(
            Cliente("C03", "Carlos Ruiz", "carlos.ruiz@pyme.co", "3209876543")
        ).resumen(),
    )

    # 4. Creación válida de servicio de Sala
    ejecutar_operacion(
        "Op 4: Crear servicio ReservaSala (SALA-1)",
        logger,
        lambda: sistema.registrar_servicio(
            ReservaSala("SALA-1", "Sala de Juntas Norte", 80.0, capacidad_personas=12)
        ).describir(),
    )

    # 5. Creación válida de servicio de Alquiler de Equipo
    ejecutar_operacion(
        "Op 5: Crear servicio AlquilerEquipo (EQ-LAP)",
        logger,
        lambda: sistema.registrar_servicio(
            AlquilerEquipo("EQ-LAP", "Laptop Desarrollador i7", 25.0, stock_disponible=3)
        ).describir(),
    )

    # 6. Creación válida de servicio de Asesoría Especializada
    ejecutar_operacion(
        "Op 6: Crear servicio AsesoriaEspecializada (ASE-ARQ)",
        logger,
        lambda: sistema.registrar_servicio(
            AsesoriaEspecializada("ASE-ARQ", "Arquitectura de Software", 120.0, "Backend & POO")
        ).describir(),
    )

    # 7. Creación inválida de servicio (tarifa negativa)
    ejecutar_operacion(
        "Op 7: Crear servicio inválido (tarifa <= 0)",
        logger,
        lambda: sistema.registrar_servicio(
            ReservaSala("SALA-ERR", "Sala Inválida", -50.0, capacidad_personas=5)
        ).describir(),
    )

    # 8. Reserva exitosa de Sala con descuento e impuesto (sobrecarga vía parámetros opcionales)
    ejecutar_operacion(
        "Op 8: Reserva exitosa de Sala (R01)",
        logger,
        lambda: sistema.crear_reserva(
            "R01", "C01", "SALA-1", duracion_horas=3, descuento_pct=10.0, impuesto_pct=19.0
        ).resumen(),
    )

    # 9. Confirmar y procesar la reserva R01
    def confirmar_y_procesar_r01() -> str:
        reserva = sistema.reservas[0]
        reserva.confirmar()
        total_cobrado = reserva.procesar()
        return f"{reserva.resumen()} | Cobro final: ${total_cobrado:,.2f}"

    ejecutar_operacion("Op 9: Confirmar y procesar reserva R01", logger, confirmar_y_procesar_r01)

    # 10. Operación no permitida: intentar cancelar una reserva ya PROCESADA
    ejecutar_operacion(
        "Op 10: Intentar cancelar reserva ya PROCESADA (R01)",
        logger,
        lambda: sistema.reservas[0].cancelar(),
    )

    # 11. Reserva fallida por stock insuficiente en alquiler de equipos (encadenamiento de excepciones)
    ejecutar_operacion(
        "Op 11: Reserva fallida por stock insuficiente (R02)",
        logger,
        lambda: sistema.crear_reserva("R02", "C03", "EQ-LAP", duracion_horas=4, unidades=10).resumen(),
    )

    # 12. Reserva exitosa de Asesoría Especializada
    def reservar_asesoria() -> str:
        r = sistema.crear_reserva("R03", "C03", "ASE-ARQ", duracion_horas=2.5, impuesto_pct=19.0)
        r.confirmar()
        return r.resumen()

    ejecutar_operacion("Op 12: Reserva y confirmación de Asesoría (R03)", logger, reservar_asesoria)

    logger.info("=== FIN DE SIMULACIÓN SOFTWARE FJ ===")
    print("\nSimulación finalizada. Revisa el archivo 'logs/software_fj.log'.")


if __name__ == "__main__":
    main()