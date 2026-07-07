const form = document.querySelector("#support-form");
const messageInput = document.querySelector("#message");
const submitButton = document.querySelector("#submit-button");
const clearButton = document.querySelector("#clear-button");
const charCount = document.querySelector("#char-count");
const statusEl = document.querySelector("#status");
const statusDetailEl = document.querySelector("#status-detail");
const categoryEl = document.querySelector("#category");
const priorityEl = document.querySelector("#priority");
const ticketEl = document.querySelector("#ticket");
const responseEl = document.querySelector("#response");
const historyList = document.querySelector("#history-list");
const quickCases = document.querySelectorAll(".quick-case");

const historyItems = [];

function setStatus(text, tone = "neutral", detail = "") {
  statusEl.textContent = text;
  statusEl.classList.toggle("success", tone === "success");
  statusEl.classList.toggle("error", tone === "error");
  statusDetailEl.textContent = detail || "Listo para procesar una solicitud.";
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? "Procesando..." : "Enviar solicitud";
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

function renderHistory() {
  historyList.innerHTML = "";

  if (historyItems.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty-history";
    empty.textContent = "Sin solicitudes procesadas.";
    historyList.appendChild(empty);
    return;
  }

  historyItems.slice(0, 5).forEach((item) => {
    const row = document.createElement("li");
    const title = document.createElement("span");
    const meta = document.createElement("span");

    title.className = "history-title";
    title.textContent = item.message;
    meta.className = "history-meta";
    meta.textContent = `${item.category} / ${item.priority} / ${item.ticket}`;

    row.append(title, meta);
    historyList.appendChild(row);
  });
}

function pushHistory(message, data) {
  historyItems.unshift({
    message: message.length > 74 ? `${message.slice(0, 74)}...` : message,
    category: data.category || "Sin categoria",
    priority: data.priority || "Sin prioridad",
    ticket: data.requires_ticket ? data.ticket_id || "Ticket requerido" : "Sin ticket",
  });
  renderHistory();
}

messageInput.addEventListener("input", updateCount);

clearButton.addEventListener("click", () => {
  messageInput.value = "";
  updateCount();
  messageInput.focus();
});

quickCases.forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.message || "";
    updateCount();
    messageInput.focus();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();
  if (!message) {
    setStatus("Revisar", "error", "Escribe un requerimiento antes de enviar.");
    responseEl.textContent = "Escribe un requerimiento antes de enviar.";
    return;
  }

  setLoading(true);
  setStatus("Procesando", "neutral", "Ejecutando grafo de agentes local.");

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
    pushHistory(message, data);
    setStatus("Completado", "success", "Respuesta generada por el flujo de agentes.");
  } catch (error) {
    renderError(error);
    setStatus("Error", "error", "No se pudo completar la solicitud.");
  } finally {
    setLoading(false);
  }
});

updateCount();
renderHistory();
