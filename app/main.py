from app.logging_config import configure_logging
from graph.support_graph import support_graph


def main() -> None:
    configure_logging()
    user_message = input("Ingrese su requerimiento: ").strip()

    if not user_message:
        print("Debes ingresar un requerimiento para continuar.")
        return

    if len(user_message) > 2000:
        print("El requerimiento supera el máximo permitido de 2000 caracteres.")
        return

    result = support_graph.invoke({"user_message": user_message})

    print("\nRespuesta final:")
    print(result.get("final_response", "No se pudo generar una respuesta final."))


if __name__ == "__main__":
    main()
