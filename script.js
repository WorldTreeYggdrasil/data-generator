const messageDiv = document.getElementById('message');
const notificationQueue = [];
let isShowing = false;

function showMessage(text, isError = false) {
  notificationQueue.push({ text, isError });
  if (!isShowing) {
    processQueue();
  }
}

function processQueue() {
  if (notificationQueue.length === 0) {
    isShowing = false;
    messageDiv.style.display = 'none';
    return;
  }
  isShowing = true;
  const { text, isError } = notificationQueue.shift();

  messageDiv.textContent = text;
  messageDiv.className = 'message ' + (isError ? 'error' : 'success');
  messageDiv.style.display = 'block';

  setTimeout(() => {
    messageDiv.style.display = 'none';
    processQueue();
  }, 1500);
}

// Ładowanie lokalizacji
async function loadLocales() {
  try {
    const response = await fetch('/locales');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const locales = await response.json();

    const select = document.getElementById('locale');
    select.innerHTML = '';
    locales.forEach(locale => {
      const option = document.createElement('option');
      option.value = locale;
      option.textContent = locale.toUpperCase();
      select.appendChild(option);
    });
  } catch (error) {
    showMessage("Błąd wczytywania lokalizacji: " + error.message, true);
  }
}

document.addEventListener('DOMContentLoaded', loadLocales);

// Generowanie danych
async function generate() {
  const locale = document.getElementById("locale").value;
  const quantity = document.getElementById("quantity").value;
  const format = document.getElementById("format").value;

  const fields = Array.from(document.querySelectorAll(".checkbox-group input:checked"))
      .map(cb => cb.id.charAt(0).toUpperCase() + cb.id.slice(1));

  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ locale, quantity, format, fields })
    });

    const contentType = response.headers.get("Content-Type");

    if (contentType && contentType.includes("application/json")) {
      const json = await response.json();

      if (json.error) {
        showMessage(json.error, true);
      }
      if (json.message) {
        showMessage(json.message, false);
      }
    } else {
      const blob = await response.blob();
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = response.headers.get("Content-Disposition").split("filename=")[1];
      document.body.appendChild(link);
      link.click();
      link.remove();

      if (format === "sql") {
        showMessage("⚠️ Nie udało się połączyć z bazą.", true);
        showMessage("✅ Plik SQL został zapisany pomyślnie.");

      } else {
        showMessage("✅ Dane zostały wygenerowane pomyślnie.");
      }
    }
  } catch (err) {
    showMessage("Wystąpił błąd: " + err.message, true);
  }
}
