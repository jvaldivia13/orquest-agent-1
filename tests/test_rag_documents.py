from rag.documents import build_documents_from_articles


def test_build_documents_from_articles_keeps_metadata_and_text():
    documents = build_documents_from_articles(
        [
            {
                "id": "KB-100",
                "category": "Red / conectividad",
                "title": "VPN no conecta",
                "keywords": ["vpn", "red"],
                "content": "Validar cliente VPN y conectividad.",
            }
        ]
    )

    assert documents == [
        {
            "id": "KB-100",
            "text": "VPN no conecta\nValidar cliente VPN y conectividad.\nKeywords: vpn, red",
            "metadata": {
                "id": "KB-100",
                "category": "Red / conectividad",
                "title": "VPN no conecta",
            },
        }
    ]
