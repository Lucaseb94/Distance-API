export function formatDistance(distanceKm) {
  if (typeof distanceKm !== "number") {
    return "-";
  }

  return `${distanceKm.toLocaleString("pt-BR", {
    maximumFractionDigits: 2,
  })} km`;
}


export function formatDuration(durationMin) {
  if (typeof durationMin !== "number") {
    return "-";
  }

  return `${Math.round(durationMin)} min`;
}


export function formatDestinationMode(mode) {
  if (mode === "automatico") {
    return "Destino automatico";
  }

  if (mode === "fixo") {
    return "Destino fixo";
  }

  return "Rota simples";
}


export function formatApiError(result, fallback) {
  if (!result || typeof result !== "object") {
    return fallback;
  }

  const limitError = result.errors?.find((error) => (
    error?.code === "demo_route_limit"
  ));

  if (limitError) {
    return [
      result.error || result.message || "Limite da demo atingido.",
      `Você já usou ${limitError.used} de ${limitError.limit} consultas disponíveis.`
    ].join(" ");
  }

  const baseMessage = result.error || result.message || fallback;
  const parts = [baseMessage];

  if (
    typeof result.detalhes === "string"
    && result.detalhes
    && !baseMessage.includes(result.detalhes)
  ) {
    parts.push(result.detalhes);
  }

  if (result.status_code) {
    parts.push(`Codigo ${result.status_code}`);
  }

  return parts.join(" ");
}


export function formatCepValue(value) {
  const digits = String(value || "").replace(/\D/g, "").slice(0, 8);
  return digits.replace(/^(\d{5})(\d{0,3})$/, "$1-$2");
}
