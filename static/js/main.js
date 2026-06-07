import { SELECTORS } from "./config.js";
import { createMapView } from "./components/mapView.js";
import { createRouteForm } from "./components/routeForm.js";
import { createRouteSummary } from "./components/routeSummary.js";
import { createSidebar } from "./components/sidebar.js";
import { createStopForm } from "./components/stopForm.js";
import { showStatus } from "./components/statusMessages.js";
import { submitItinerary } from "./services/itineraryService.js";
import { submitSimpleRoute } from "./services/routeService.js";
import { setCurrentRoute, setDestinationMode } from "./state/appState.js";
import { qs, qsa } from "./utils/domUtils.js";


const form = qs(SELECTORS.routeForm);
const submitButton = qs(SELECTORS.submitButton);
const statusMessage = qs(SELECTORS.statusMessage);
const multiStatusMessage = qs(SELECTORS.multiStatusMessage);
const resultCard = qs(SELECTORS.resultCard);
const addStopButton = qs(SELECTORS.addStopButton);
const calculateItineraryButton = qs(SELECTORS.calculateItineraryButton);
const multiRouteForm = qs(SELECTORS.multiRouteForm);

const sidebar = createSidebar({
  buttons: qsa(SELECTORS.panelButton),
  panels: qsa(SELECTORS.panel),
});
const routeForm = createRouteForm(form);
const mapView = createMapView(qs(SELECTORS.map));
const summary = createRouteSummary({
  resultCard,
  emptySummary: qs(SELECTORS.emptySummary),
  originalStops: qs(SELECTORS.summaryOriginalStops),
  optimizedStops: qs(SELECTORS.summaryStops),
  legs: qs(SELECTORS.summaryLegs),
  fields: {
    origem: qs("#resultado-origem"),
    destino: qs("#resultado-destino"),
    destinoEscolhido: qs("#resultado-destino-escolhido"),
    modo: qs("#resultado-modo"),
    distancia: qs("#resultado-distancia"),
    duracao: qs("#resultado-duracao"),
  },
}, sidebar);
const stopForm = createStopForm({
  stopsList: qs(SELECTORS.stopsList),
  modeInputs: qsa(SELECTORS.routeModeInput),
  onChange: renderDraftStops,
});


function initApp() {
  sidebar.bind();
  routeForm.bindCepMask(SELECTORS.cepInputs);
  stopForm.init();
  bindEvents();
  bootMapWhenReady();
}


function bindEvents() {
  form.addEventListener("submit", handleSimpleRouteSubmit);
  addStopButton.addEventListener("click", stopForm.addStop);
  multiRouteForm.addEventListener("submit", handleItinerarySubmit);
  qsa(SELECTORS.routeModeInput).forEach((input) => {
    input.addEventListener("change", () => {
      setDestinationMode(stopForm.getDestinationMode());
    });
  });
}


function bootMapWhenReady() {
  if (window.__googleMapsReady) {
    mapView.init();
    return;
  }

  window.addEventListener("google-maps-ready", () => mapView.init(), { once: true });
}


async function handleSimpleRouteSubmit(event) {
  event.preventDefault();

  if (!routeForm.isAuthenticated()) {
    showStatus(statusMessage, "Faça login para calcular rotas.", "is-error");
    return;
  }

  submitButton.disabled = true;
  resultCard.hidden = true;
  mapView.clear();
  showStatus(statusMessage, "Calculando rota...", "is-loading");

  try {
    const result = await submitSimpleRoute(routeForm.read());
    setCurrentRoute(result);
    summary.renderRoute(result);
    mapView.draw(result);
    showStatus(statusMessage, "Rota calculada com sucesso.", "is-success");
  } catch (error) {
    handleError(error, statusMessage, "Nao foi possivel calcular a rota.");
  } finally {
    submitButton.disabled = false;
  }
}


async function handleItinerarySubmit(event) {
  event.preventDefault();

  if (!routeForm.isAuthenticated()) {
    showStatus(
      multiStatusMessage,
      "Entre ou crie uma conta para calcular itinerarios.",
      "is-warning"
    );
    return;
  }

  const destinationMode = stopForm.getDestinationMode();
  const stops = stopForm.readStops();
  calculateItineraryButton.disabled = true;
  mapView.clear();
  showStatus(multiStatusMessage, "Calculando itinerario...", "is-loading");

  try {
    const result = await submitItinerary(stops, destinationMode);
    setCurrentRoute(result);
    summary.renderItinerary(result);
    mapView.draw(result);
    showStatus(multiStatusMessage, itinerarySuccessMessage(result), "is-success");
  } catch (error) {
    handleError(error, multiStatusMessage, "Nao foi possivel calcular o itinerario.");
  } finally {
    calculateItineraryButton.disabled = false;
  }
}


function renderDraftStops() {
  summary.renderStops(stopForm.readStops(), qs(SELECTORS.summaryOriginalStops));
}


function itinerarySuccessMessage(result) {
  if (result.modo_destino === "automatico" && result.rotas_avaliadas) {
    return `Itinerario calculado. ${result.rotas_avaliadas} destinos finais avaliados.`;
  }

  return "Itinerario calculado com sucesso.";
}


function handleError(error, statusElement, fallback) {
  showStatus(statusElement, error.message || fallback, "is-error");

  if (error.redirect) {
    window.setTimeout(() => {
      window.location.href = error.redirect;
    }, 900);
  }
}


window.limparMapa = mapView.clear;
window.desenharRota = mapView.draw;
window.mostrarResultado = summary.renderRoute;

initApp();
