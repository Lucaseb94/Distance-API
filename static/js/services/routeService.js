import { calculateSimpleRoute } from "../api/routeApi.js";
import { validateSimpleRoute } from "./validationService.js";


export async function submitSimpleRoute(payload) {
  const error = validateSimpleRoute(payload);

  if (error) {
    throw new Error(error);
  }

  return calculateSimpleRoute(payload);
}
