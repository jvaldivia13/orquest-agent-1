const form = document.querySelector("#support-form");
const messageInput = document.querySelector("#message");
const submitButton = document.querySelector("#submit-button");
const charCount = document.querySelector("#char-count");
const statusEl = document.querySelector("#status");
const categoryEl = document.querySelector("#category");
const priorityEl = document.querySelector("#priority");
const ticketEl = document.querySelector("#ticket");
const responseEl = document.querySelector("#response");

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.classList.toggle("error", isError);
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? "Enviando..." : "Enviar";
}

function updateCount() {
  charCount.textContent = `${messageInput.value.length}/2000`;
}

function renderResult(data) {
  categoryEl.textContent = data.category || "-";
  priorityEl.textContent = data.priority || "-";
  ticketEl.textContent = data.requires_ticket
    ? data.ticket_id || "Requerido"
    : "No requerido";
  responseEl.textContent = data.response || "La API no devolvio una respuesta.";
}

function renderError(error) {
  categoryEl.textContent = "-";
  priorityEl.textContent = "-";
  ticketEl.textContent = "-";
  responseEl.textContent = error.message || "No se pudo completar la solicitud.";
}

messageInput.addEventListener("input", updateCount);

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();
  if (!message) {
    setStatus("Mensaje requerido", true);
    responseEl.textContent = "Escribe un requerimiento antes de enviar.";
    return;
  }

  setLoading(true);
  setStatus("Procesando");

  try {
    const response = await fetch("/support/request", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`La API respondio con estado ${response.status}.`);
    }

    const data = await response.json();
    renderResult(data);
    setStatus("Completado");
  } catch (error) {
    renderError(error);
    setStatus("Error", true);
  } finally {
    setLoading(false);
  }
});

updateCount();
