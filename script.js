// Fetch available locales and populate dropdown
async function loadLocales() {
    try {
        const response = await fetch('/locales');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
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

// Pokazuje komunikaty użytkownikowi
function showMessage(text, isError = false) {
    const messageDiv = document.getElementById("message");
    messageDiv.style.display = "block";
    messageDiv.textContent = text;
    messageDiv.className = isError ? "message error" : "message success";
}

// Główna funkcja generowania danych
async function generate() {
    const locale = document.getElementById("locale").value;
    const quantity = document.getElementById("quantity").value;
    const format = document.getElementById("format").value;

    const fields = Array.from(document.querySelectorAll(".checkbox-group input:checked"))
        .map(cb => cb.id.charAt(0).toUpperCase() + cb.id.slice(1));

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                locale: locale,
                quantity: quantity,
                format: format,
                fields: fields
            })
        });

        if (response.headers.get("Content-Type").includes("application/json")) {
            const json = await response.json();
            showMessage(json.message || json.error, true);
        } else {
            const blob = await response.blob();
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = response.headers.get("Content-Disposition").split("filename=")[1];
            document.body.appendChild(link);
            link.click();
            link.remove();
            showMessage("Dane zostały wygenerowane pomyślnie.");
        }
    } catch (err) {
        showMessage("Wystąpił błąd: " + err.message, true);
    }
}
