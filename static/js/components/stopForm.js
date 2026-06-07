import { INITIAL_STOP_COUNT, SELECTORS } from "../config.js";
import { qs, qsa } from "../utils/domUtils.js";
import { formatCepValue } from "../utils/formatUtils.js";


export function createStopForm({ stopsList, modeInputs, onChange }) {
  let stopId = 0;

  function init() {
    for (let index = 0; index < INITIAL_STOP_COUNT; index += 1) {
      addStop();
    }

    modeInputs.forEach((input) => {
      input.addEventListener("change", () => {
        renumberStops();
        onChange?.();
      });
    });

    stopsList.addEventListener("input", onChange);
  }

  function addStop() {
    stopId += 1;

    const card = document.createElement("article");
    card.className = "stop-card";
    card.dataset.stopId = String(stopId);
    card.innerHTML = `
      <div class="stop-card-header">
        <strong class="stop-card-title">Ponto ${stopId}</strong>
        <button class="remove-stop-button" type="button">Remover</button>
      </div>
      <div class="stop-grid">
        <div class="field-group">
          <label for="parada-cep-${stopId}">CEP</label>
          <input
            id="parada-cep-${stopId}"
            name="cep"
            class="cep-input"
            type="text"
            inputmode="numeric"
            placeholder="00000-000"
            maxlength="9"
          >
        </div>
        <div class="field-group">
          <label for="parada-numero-${stopId}">Numero</label>
          <input
            id="parada-numero-${stopId}"
            name="numero"
            type="text"
            inputmode="numeric"
            placeholder="000"
          >
        </div>
      </div>
    `;

    qs(".cep-input", card).addEventListener("input", formatCepInput);
    qs(".remove-stop-button", card).addEventListener("click", () => {
      card.remove();
      renumberStops();
      onChange?.();
    });

    stopsList.appendChild(card);
    renumberStops();
    onChange?.();
  }

  function renumberStops() {
    const destinationMode = getDestinationMode();
    const total = stopsList.children.length;

    qsa(".stop-card-title", stopsList).forEach((title, index) => {
      if (index === 0) {
        title.textContent = "Origem";
        return;
      }

      if (destinationMode === "fixo" && index === total - 1) {
        title.textContent = "Destino final";
        return;
      }

      title.textContent = `Parada ${index}`;
    });

    qsa(".remove-stop-button", stopsList).forEach((button) => {
      button.disabled = stopsList.children.length <= 2;
    });
  }

  function readStops() {
    return qsa(".stop-card", stopsList).map((card) => ({
      cep: qs("[name='cep']", card).value.trim(),
      numero: qs("[name='numero']", card).value.trim(),
    }));
  }

  function getDestinationMode() {
    const selected = qs(SELECTORS.checkedRouteMode);
    return selected?.value || "fixo";
  }

  function formatCepInput(event) {
    event.target.value = formatCepValue(event.target.value);
  }

  return {
    init,
    addStop,
    readStops,
    getDestinationMode,
    renumberStops,
  };
}
