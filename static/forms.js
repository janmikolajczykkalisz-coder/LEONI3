// --- Przełącznik języka ---
document.addEventListener('DOMContentLoaded', function() {
  const btnLang = document.getElementById('btnLang');
  if (btnLang) {
    btnLang.addEventListener('click', function() {
      const current = "{{ lang if lang is defined else 'pl' }}";
      const next = current === "pl" ? "de" : "pl";
      window.location.href = "/set_lang/" + next;
    });
  }

  // --- Obsługa zmiany zestawu średnic ---
  const select = document.getElementById('diameter_set');
  if (select) {
    select.addEventListener('change', function() {
      let diameters = [];
      try {
        const v = this.value;
        if (v === '1' && typeof diametersSet1 !== 'undefined') diameters = diametersSet1;
        else if (v === '2' && typeof diametersSet2 !== 'undefined') diameters = diametersSet2;
        else if (v === '3' && typeof diametersSet3 !== 'undefined') diameters = diametersSet3;
      } catch (e) {
        diameters = [];
      }

      const inputs = document.querySelectorAll('.diam-cell');
      inputs.forEach((input, idx) => {
        if (diameters[idx] !== undefined && diameters[idx] !== null) {
          input.value = Number(diameters[idx]).toFixed(4);
        }
      });
    });
  }
});

// --- Usuwanie kamienia ---
function removeRow(button) {
  const row = button.closest("tr");
  if (row) row.remove();
}

// --- Dodawanie kamienia ---
function addStoneRow() {
  const tableBody = document.querySelector("#diameters-tbody");
  const index = tableBody.rows.length;
  const newRow = document.createElement("tr");
  newRow.innerHTML = `
    <td>
      <input type="text" id="code${index}" name="code${index}"
             class="form-control" placeholder="Kod #${index+1}" required>
    </td>
    <td>
      <input type="number" step="0.0001" name="diameter${index}"
             class="form-control diam-cell" placeholder="Średnica">
    </td>
    <td class="d-flex gap-2">
      <button type="button" class="btn btn-outline-primary btn-sm"
              onclick="startScanner('code${index}', ${index})">
        <i class="bi bi-qr-code-scan"></i> Skanuj
      </button>
      <button type="button" class="btn btn-outline-danger btn-sm"
              onclick="removeRow(this)">
        <i class="bi bi-trash"></i> Usuń
      </button>
    </td>
  `;
  tableBody.appendChild(newRow);
}
