export function validateSimpleRoute(data) {
  if (!data.cep_origem) {
    return "Informe o CEP de origem.";
  }

  if (!data.numero_origem) {
    return "Informe o numero da origem.";
  }

  if (!data.cep_destino) {
    return "Informe o CEP de destino.";
  }

  if (!data.numero_destino) {
    return "Informe o numero do destino.";
  }

  return null;
}


export function validateItinerary(stops, destinationMode) {
  const incomplete = stops.some((stop) => !stop.cep || !stop.numero);

  if (incomplete) {
    return "Preencha CEP e numero de todos os pontos.";
  }

  if (destinationMode === "automatico" && stops.length < 3) {
    return "No destino automatico, informe origem e pelo menos duas paradas.";
  }

  return null;
}
