from agents.classifier_agent import classifier_node


def test_classifier_access_request():
    result = classifier_node({"user_message": "No puedo acceder a mi cuenta"})

    assert result["category"] == "Acceso / autenticación"
    assert result["priority"] == "Media"
