function generate() {
    const locale = document.getElementById('locale').value;
    const quantity = document.getElementById('quantity').value;
    const name = document.getElementById('name').checked;
    const surname = document.getElementById('surname').checked;
    const id = document.getElementById('id').checked;
    const birthdate = document.getElementById('birthdate').checked;
  
    const fields = [];
    if (name) fields.push("Name");
    if (surname) fields.push("Surname");
    if (id) fields.push("ID");
    if (birthdate) fields.push("Birth Date");
  
    alert(`Wygeneruj ${quantity} rekordów [${fields.join(", ")}] dla lokalizacji ${locale.toUpperCase()}`);
    // Tutaj podłącz Python przez API
  }
  