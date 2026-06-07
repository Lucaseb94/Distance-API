export function createSidebar({ buttons, panels }) {
  function activate(panelName) {
    buttons.forEach((button) => {
      const active = button.dataset.panelTarget === panelName;
      button.classList.toggle("is-active", active);
    });

    panels.forEach((panel) => {
      const active = panel.dataset.panel === panelName;
      panel.hidden = !active;
      panel.classList.toggle("is-active", active);
    });
  }

  function bind() {
    buttons.forEach((button) => {
      button.addEventListener("click", () => activate(button.dataset.panelTarget));
    });
  }

  return {
    activate,
    bind,
  };
}
