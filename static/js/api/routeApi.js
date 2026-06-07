import { ENDPOINTS } from "../config.js";
import { formatApiError } from "../utils/formatUtils.js";


export class ApiError extends Error {
  constructor(result, fallback) {
    super(formatApiError(result, fallback));
    this.result = result;
    this.redirect = result?.redirect;
  }
}


async function postJson(endpoint, payload, fallbackMessage) {
  let response;

  try {
    response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    throw new ApiError(
      { message: "Nao foi possivel conectar ao backend." },
      fallbackMessage
    );
  }

  const result = await parseJsonResponse(response, fallbackMessage);

  if (!response.ok || result.valido === false || result.success === false) {
    throw new ApiError(result, fallbackMessage);
  }

  return result;
}


async function parseJsonResponse(response, fallbackMessage) {
  try {
    return await response.json();
  } catch (error) {
    return {
      success: false,
      valido: false,
      message: fallbackMessage,
      error: fallbackMessage,
      status_code: response.status,
    };
  }
}


export function calculateSimpleRoute(payload) {
  return postJson(
    ENDPOINTS.simpleRoute,
    payload,
    "Endereco invalido."
  );
}


export function calculateItinerary(payload) {
  return postJson(
    ENDPOINTS.itinerary,
    payload,
    "Nao foi possivel calcular o itinerario."
  );
}
