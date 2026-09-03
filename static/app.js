const questionEl = document.getElementById("question");
const askBtn = document.getElementById("ask-btn");
const loaderEl = document.getElementById("loader");
const errorEl = document.getElementById("error");
const answerCardEl = document.getElementById("answer-card");
const answerContentEl = document.getElementById("answer-content");
const copyBtn = document.getElementById("copy-btn");
const historyListEl = document.getElementById("history-list");
const apiKeyStatusEl = document.getElementById("api-key-status");
const tokenCounterEl = document.getElementById("token-counter");

let lastAnswerText = "";

function renderMarkdown(text) {
  const html = marked.parse(text);
  return DOMPurify.sanitize(html);
}

function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString("ru-RU");
}

function setLoading(isLoading) {
  askBtn.disabled = isLoading;
  loaderEl.hidden = !isLoading;
}

function showError(message) {
  errorEl.textContent = message;
  errorEl.hidden = false;
}

function hideError() {
  errorEl.hidden = true;
}

async function askQuestion() {
  const question = questionEl.value.trim();
  if (!question) {
    showError("Введите вопрос");
    return;
  }

  hideError();
  setLoading(true);
  answerCardEl.hidden = true;

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || `Ошибка запроса (${response.status})`);
    }

    const data = await response.json();
    lastAnswerText = data.answer;
    answerContentEl.innerHTML = renderMarkdown(data.answer);
    answerCardEl.hidden = false;
    tokenCounterEl.innerHTML = `<span class="token-numbers">↑${data.input_tokens} ↓${data.output_tokens}</span> <span class="token-label">токенов</span>`;
    questionEl.value = "";
    await loadHistory();
  } catch (err) {
    showError(err.message || "Не удалось получить ответ");
  } finally {
    setLoading(false);
  }
}

async function loadHistory() {
  try {
    const response = await fetch("/history");
    if (!response.ok) return;
    const items = await response.json();

    if (items.length === 0) {
      historyListEl.innerHTML = '<p class="history-empty">Пока нет запросов</p>';
      return;
    }

    historyListEl.innerHTML = items
      .map(
        (item) => `
        <div class="history-item">
          <div class="history-question">${escapeHtml(item.question)}</div>
          <div class="history-answer">${renderMarkdown(item.answer)}</div>
          <div class="history-time">${formatDate(item.created_at)}</div>
        </div>
      `
      )
      .join("");
  } catch (err) {
    // тихо игнорируем ошибки загрузки истории
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

async function checkApiKey() {
  try {
    const response = await fetch("/health/api-key");
    const data = await response.json();
    apiKeyStatusEl.className = "badge badge-" + (data.status || "error");
    const labels = {
      valid: "ключ валиден",
      invalid: "ключ невалиден",
      expired: "ключ истёк",
      error: "ошибка проверки ключа",
    };
    apiKeyStatusEl.textContent = labels[data.status] || data.status;
    if (data.detail) {
      apiKeyStatusEl.title = data.detail;
    }
  } catch (err) {
    apiKeyStatusEl.className = "badge badge-error";
    apiKeyStatusEl.textContent = "ошибка проверки ключа";
  }
}

askBtn.addEventListener("click", askQuestion);
questionEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
    askQuestion();
  }
});

copyBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(lastAnswerText);
    const originalText = copyBtn.textContent;
    copyBtn.textContent = "Скопировано!";
    setTimeout(() => {
      copyBtn.textContent = originalText;
    }, 1500);
  } catch (err) {
    showError("Не удалось скопировать ответ");
  }
});

checkApiKey();
loadHistory();
