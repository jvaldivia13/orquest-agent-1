import subprocess
import sys


def test_cli_runs_as_module_and_prints_response():
    completed = subprocess.run(
        [sys.executable, "-m", "app.main"],
        input="No puedo conectarme a la VPN\n",
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert completed.returncode == 0
    assert "Respuesta final:" in completed.stdout
    assert "VPN" in completed.stdout
