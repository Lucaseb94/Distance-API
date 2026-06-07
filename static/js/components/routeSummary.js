import { escapeHtml } from "../utils/domUtils.js";
import {
  formatDestinationMode,
  formatDistance,
  formatDuration,
} from "../utils/formatUtils.js";


export function createRouteSummary(elements, sidebar) {
  function renderRoute(result) {
    const origin = result.origem || {};
    const destination = result.destino || {};

    elements.fields.origem.textContent = origin.endereco || "-";
    elements.fields.destino.textContent = destination.endereco || "-";
    elements.fields.destinoEscolhido.textContent = (
      result.destino_escolhido?.endereco
      || destination.endereco
      || "-"
    );
    elements.fields.modo.textContent = formatDestinationMode(result.modo_destino);
    elements.fields.distancia.textContent = formatDistance(result.distancia_km);
    elements.fields.duracao.textContent = formatDuration(result.duracao_min);

    elements.emptySummary.hidden = true;
    elements.resultCard.hidden = false;
    sidebar.activate("resumo");
  }

  function renderItinerary(result) {
    renderRoute(result);
    renderStops(result.ordem_original || [], elements.originalStops);
    renderStops(result.ordem_otimizada || result.paradas || [], elements.optimizedStops);
    renderLegs(result.trechos || []);
  }

  function renderStops(stops, list) {
    const filledStops = stops.filter((stop) => (
      stop.endereco
      || stop.cep
      || stop.numero
    ));

    if (!filledStops.length) {
      list.innerHTML = "<li>Nenhuma parada adicionada.</li>";
      return;
    }

    list.innerHTML = filledStops
      .map((stop, index) => {
        if (stop.endereco) {
          return `<li>${index + 1}. ${escapeHtml(stop.endereco)}</li>`;
        }

        const cep = escapeHtml(stop.cep || "CEP nao informado");
        const numero = escapeHtml(stop.numero || "sem numero");
        return `<li>Parada ${index + 1}: ${cep}, ${numero}</li>`;
      })
      .join("");
  }

  function renderLegs(legs) {
    if (!legs.length) {
      elements.legs.innerHTML = "<li>Nenhum trecho calculado.</li>";
      return;
    }

    elements.legs.innerHTML = legs
      .map((leg) => {
        const distance = formatDistance(leg.distancia_km);
        const duration = formatDuration(leg.duracao_minutos);
        return `<li>Trecho ${leg.ordem}: ${distance}, ${duration}</li>`;
      })
      .join("");
  }

  return {
    renderRoute,
    renderItinerary,
    renderStops,
    renderLegs,
  };
}
