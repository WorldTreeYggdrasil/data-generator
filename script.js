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
        console.error('Error loading locales:', error);
    }
}

// Load locales when page loads
document.addEventListener('DOMContentLoaded', loadLocales);

async function generate() {
    const locale = document.getElementById('locale').value;
    const quantity = document.getElementById('quantity').value;
    const name = document.getElementById('name').checked;
    const surname = document.getElementById('surname').checked;
    const id = document.getElementById('id').checked;
    const birthdate = document.getElementById('birthdate').checked;
    const street = document.getElementById('street').checked;
    const city = document.getElementById('city').checked;
    const country = document.getElementById('country').checked;
    const format = document.getElementById('format').value;
  
    const fields = [];
    if (name) fields.push("Name");
    if (surname) fields.push("Surname");
    if (id) fields.push("ID");
    if (birthdate) fields.push("Birth Date");
    if (street) fields.push("Street");
    if (city) fields.push("City");
    if (country) fields.push("Country");

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                locale,
                quantity,
                fields,
                format
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const extension = format === 'sql' ? '.sql' : '.csv';
        a.download = `generated_data_${locale}${extension}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error:', error);
        alert(`Error generating data: ${error.message}`);
    }
}
