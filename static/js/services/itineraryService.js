import { calculateItinerary } from "../api/routeApi.js";
import { validateItinerary } from "./validationService.js";


export async function submitItinerary(stops, destinationMode) {
  const error = validateItinerary(stops, destinationMode);

  if (error) {
    throw new Error(error);
  }

  return calculateItinerary({
    paradas: stops,
    otimizar: true,
    modo_destino: destinationMode,
  });
}
