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
  }, 2000);
}

// Funkcja do włączenia/wyłączenia checkboxa postalCode
function updatePostalCodeCheckboxState(localeValue) {
  const postalCodeCheckbox = document.getElementById('postalCode');
  const postalCodeLabel = postalCodeCheckbox.parentElement;

  if (localeValue === 'de') {
    postalCodeCheckbox.checked = false;
    postalCodeCheckbox.disabled = true;
    postalCodeLabel.innerHTML = '<input type="checkbox" id="postalCode" disabled /> Kod Pocztowy (brak)';
  } else if (localeValue === 'pl') {
    postalCodeCheckbox.checked = true;
    postalCodeCheckbox.disabled = false;
    postalCodeLabel.innerHTML = '<input type="checkbox" id="postalCode" checked /> Kod Pocztowy';
  } else {
    postalCodeCheckbox.checked = false;
    postalCodeCheckbox.disabled = false;
    postalCodeLabel.innerHTML = '<input type="checkbox" id="postalCode" /> Kod Pocztowy';
  }
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

    // Po załadowaniu - ustaw stan checkboxa
    updatePostalCodeCheckboxState(select.value);
  } catch (error) {
    showMessage("Błąd wczytywania lokalizacji: " + error.message, true);
  }
}

document.addEventListener('DOMContentLoaded', loadLocales);

// Obsługa zmiany lokalizacji
document.addEventListener('DOMContentLoaded', () => {
  const localeSelect = document.getElementById('locale');
  localeSelect.addEventListener('change', () => {
    updatePostalCodeCheckboxState(localeSelect.value);
  });
});

// Główna funkcja generowania
async function generate() {
  const locale = document.getElementById("locale").value;
  const quantity = document.getElementById("quantity").value;
  const format = document.getElementById("format").value;

  const fields = Array.from(document.querySelectorAll(".checkbox-group input:checked"))
      .map(cb => cb.id.charAt(0).toUpperCase() + cb.id.slice(1));

  if (format === "csv") {
    sendGenerateRequest({ locale, quantity, format, fields });
    return;
  }

  // SQL – podgląd
  try {
    const response = await fetch("/preview-sql", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ locale, quantity, fields })
    });

    const result = await response.json();

    if (result.sql) {
      document.getElementById("sql-preview-box").value = result.sql;
      document.getElementById("sql-overlay").style.display = "flex";
      window.pendingSqlData = { locale, quantity, fields };
    } else {
      showMessage("Nie udało się wygenerować podglądu SQL", true);
    }
  } catch (err) {
    showMessage("Błąd podglądu SQL: " + err.message, true);
  }
}

// Wyślij żądanie wygenerowania danych (CSV lub SQL z confirm)
async function sendGenerateRequest(payload) {
  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const contentType = response.headers.get("Content-Type");

    if (contentType && contentType.includes("application/json")) {
      const json = await response.json();
      if (json.error) showMessage(json.error, true);
      if (json.message) showMessage(json.message, false);
    } else {
      const blob = await response.blob();
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = response.headers.get("Content-Disposition").split("filename=")[1];
      document.body.appendChild(link);
      link.click();
      link.remove();

      if (payload.format === "sql") {
        showMessage("⚠️ Nie udało się połączyć z bazą.", true);
        showMessage("✅ Plik SQL został pobrany.");
      } else {
        showMessage("✅ Dane CSV zostały wygenerowane.");
      }
    }
  } catch (err) {
    showMessage("Wystąpił błąd: " + err.message, true);
  }
}

// Obsługa modala SQL
function closeSqlPreview() {
  document.getElementById("sql-overlay").style.display = "none";
  window.pendingSqlData = null;
}

async function confirmSqlInsert() {
  const { locale, quantity, fields } = window.pendingSqlData;
  closeSqlPreview();
  sendGenerateRequest({ locale, quantity, fields, format: "sql", confirm: true });
}

async function downloadSql() {
  const blob = new Blob([document.getElementById("sql-preview-box").value], { type: "application/sql" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "generated_preview.sql";
  link.click();
  closeSqlPreview();
}
