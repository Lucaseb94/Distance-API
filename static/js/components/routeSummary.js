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

    list.replaceChildren();

    if (!filledStops.length) {
      appendListItem(list, "Nenhuma parada adicionada.");
      return;
    }

    filledStops.forEach((stop, index) => {
      if (stop.endereco) {
        appendListItem(list, `${index + 1}. ${stop.endereco}`);
        return;
      }

      const cep = stop.cep || "CEP nao informado";
      const numero = stop.numero || "sem numero";
      appendListItem(list, `Parada ${index + 1}: ${cep}, ${numero}`);
    });
  }

  function renderLegs(legs) {
    elements.legs.replaceChildren();

    if (!legs.length) {
      appendListItem(elements.legs, "Nenhum trecho calculado.");
      return;
    }

    legs.forEach((leg) => {
      const distance = formatDistance(leg.distancia_km);
      const duration = formatDuration(leg.duracao_minutos);
      appendListItem(elements.legs, `Trecho ${leg.ordem}: ${distance}, ${duration}`);
    });
  }

  function appendListItem(list, text) {
    const item = document.createElement("li");
    item.textContent = text;
    list.appendChild(item);
  }

  return {
    renderRoute,
    renderItinerary,
    renderStops,
    renderLegs,
  };
}
