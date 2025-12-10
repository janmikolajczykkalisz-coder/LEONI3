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

  // --- Obsługa zmiany zestawu średnic (index.html) ---
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

// --- Funkcje do manipulacji tabelą (index.html) ---
function removeRow(button) {
  const row = button.closest("tr");
  if (row) row.remove();
}

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

// --- AJAX do zmiany statusu (history.html) ---
function updateStatus(stoneId, newStatus) {
  fetch(`/update_status/${stoneId}`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `status=${encodeURIComponent(newStatus)}`
  });
}

// --- Dynamiczne uzupełnianie średnic (history.html) ---
function initHistoryDiameters(diametersBySet) {
  const zestawSelect = document.getElementById("zestawSelect");
  const diameterSelect = document.getElementById("diameterSelect");

  function updateDiameters() {
    const zestaw = zestawSelect.value;
    const options = diametersBySet[zestaw] || [];
    diameterSelect.innerHTML = "";
    options.forEach(d => {
      const opt = document.createElement("option");
      opt.value = d;
      opt.textContent = Number(d).toFixed(4);
      diameterSelect.appendChild(opt);
    });
  }

  if (zestawSelect && diameterSelect) {
    zestawSelect.addEventListener("change", updateDiameters);
    updateDiameters(); // inicjalizacja przy pierwszym otwarciu
  }
}

// --- QR Code Scanner (index.html + history.html) ---
let html5QrCode;
function startScanner(inputId, index) {
  const readerElem = document.getElementById("reader");
  readerElem.style.display = "block";

  if (!html5QrCode) {
    html5QrCode = new Html5Qrcode("reader");
  }

  html5QrCode.start(
    { facingMode: "environment" },
    { fps: 10, qrbox: 250 },
    (decodedText) => {
      // wpisz wynik do pola formularza
      if (inputId) {
        document.getElementById(inputId).value = decodedText;
      } else {
        const scannedField = document.getElementById("scannedCode");
        if (scannedField) scannedField.value = decodedText;
      }
      // zatrzymaj skaner po odczycie
      html5QrCode.stop().then(() => {
        readerElem.style.display = "none";
      });
    },
    (errorMessage) => {
      // ignorujemy błędy odczytu
    }
  ).catch(err => {
    console.error("Błąd uruchamiania skanera:", err);
  });
}
