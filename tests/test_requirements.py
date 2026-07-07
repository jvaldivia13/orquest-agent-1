from pathlib import Path


def test_runtime_dependencies_are_pinned():
    requirements = Path("requirements.txt").read_text(encoding="utf-8").splitlines()
    runtime_packages = [
        "langchain",
        "langgraph",
        "langchain-deepseek",
        "python-dotenv",
        "pydantic",
        "fastapi",
        "uvicorn",
        "pytest",
    ]

    for package in runtime_packages:
        line = next((item for item in requirements if item.startswith(package)), "")
        assert "==" in line or "~=" in line or ">=" in line
