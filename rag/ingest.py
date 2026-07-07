from rag.documents import build_documents_from_articles, load_knowledge_articles
from rag.vector_store import build_vector_index


def main() -> None:
    articles = load_knowledge_articles()
    documents = build_documents_from_articles(articles)
    indexed = build_vector_index(documents)
    print(f"Indexed {indexed} knowledge documents.")


if __name__ == "__main__":
    main()
