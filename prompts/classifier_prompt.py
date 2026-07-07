CLASSIFIER_PROMPT = (
    "Clasifica el requerimiento de soporte TI. "
    "Devuelve solo JSON con keys category y priority. "
    "Categorias permitidas: Acceso / autenticacion, Red / conectividad, Hardware, "
    "Software, Solicitud administrativa, Otro. Prioridades: Baja, Media, Alta. "
    "Mensaje: {user_message}"
)


def build_classifier_prompt(user_message: str) -> str:
    return CLASSIFIER_PROMPT.format(user_message=user_message)
