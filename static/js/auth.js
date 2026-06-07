const authForm = document.querySelector("[data-auth-form]");
const authMessage = document.querySelector("[data-auth-message]");

if (authForm && authMessage) {
  authForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const submitButton = authForm.querySelector("button[type='submit']");
    const senha = authForm.querySelector("#senha");
    const confirmarSenha = authForm.querySelector("#confirmar-senha");

    if (confirmarSenha && senha.value !== confirmarSenha.value) {
      authMessage.textContent = "As senhas precisam ser iguais.";
      authMessage.className = "auth-note is-error";
      return;
    }

    submitButton.disabled = true;
    authMessage.textContent = "Enviando...";
    authMessage.className = "auth-note";

    try {
      const response = await fetch(authForm.dataset.authEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(lerDadosFormulario(authForm)),
      });
      const resultado = await response.json();

      if (!response.ok || !resultado.valido) {
        authMessage.textContent = resultado.error || "Nao foi possivel continuar.";
        authMessage.className = "auth-note is-error";
        return;
      }

      authMessage.textContent = resultado.message || "Tudo certo.";
      authMessage.className = "auth-note is-success";

      if (resultado.redirect) {
        window.location.href = resultado.redirect;
      }
    } catch (error) {
      authMessage.textContent = "Nao foi possivel conectar ao backend.";
      authMessage.className = "auth-note is-error";
    } finally {
      submitButton.disabled = false;
    }
  });
}

function lerDadosFormulario(form) {
  const dados = {};

  new FormData(form).forEach((value, key) => {
    dados[key] = String(value).trim();
  });

  return dados;
}
