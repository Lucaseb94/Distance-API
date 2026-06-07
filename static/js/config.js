export const ENDPOINTS = {
  simpleRoute: "/api/rotas/calcular",
  itinerary: "/api/rotas/itinerario",
};

export const DEFAULT_CENTER = { lat: -23.5505, lng: -46.6333 };
export const INITIAL_STOP_COUNT = 4;

export const SELECTORS = {
  routeForm: "#route-form",
  submitButton: "#submit-button",
  statusMessage: "#status-message",
  multiStatusMessage: "#multi-status",
  resultCard: "#result-card",
  emptySummary: "#empty-summary",
  panelButton: "[data-panel-target]",
  panel: "[data-panel]",
  stopsList: "#stops-list",
  addStopButton: "#add-stop-button",
  calculateItineraryButton: "#calculate-itinerary-button",
  multiRouteForm: "#multi-route-form",
  routeModeInput: "[name='modo-destino']",
  checkedRouteMode: "[name='modo-destino']:checked",
  summaryOriginalStops: "#summary-original-stops",
  summaryStops: "#summary-stops",
  summaryLegs: "#summary-legs",
  map: "#map",
  cepInputs: "#cep-origem, #cep-destino",
};
