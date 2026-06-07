import { qs, qsa } from "../utils/domUtils.js";
import { formatCepValue } from "../utils/formatUtils.js";


export function createRouteForm(form) {
  function bindCepMask(selector) {
    qsa(selector).forEach((input) => {
      input.addEventListener("input", (event) => {
        event.target.value = formatCepValue(event.target.value);
      });
    });
  }

  function read() {
    return {
      cep_origem: qs("#cep-origem", form).value.trim(),
      numero_origem: qs("#numero-origem", form).value.trim(),
      cep_destino: qs("#cep-destino", form).value.trim(),
      numero_destino: qs("#numero-destino", form).value.trim(),
    };
  }

  function isAuthenticated() {
    return form?.dataset.authenticated === "true";
  }

  return {
    bindCepMask,
    read,
    isAuthenticated,
  };
}
