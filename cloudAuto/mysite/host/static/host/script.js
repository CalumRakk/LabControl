document.addEventListener("DOMContentLoaded", function () {
  const csrfmiddlewaretoken = document.querySelector(
    "[name=csrfmiddlewaretoken]"
  ).value;

  const PC = {
    pcControl: document.getElementById("pcControl"),
    onButton: document.getElementById("turnOnPCButton"),
    offButton: document.getElementById("turnOffPCButton"),
    statusPanel: document.getElementById("pcStatus"),
    enableOnButon: function enableTurnOnPCButton() {
      this.onButton.disabled = false;
      this.offButton.disabled = true;
    },
    enableOffButton: function enableTurnOffPCButton() {
      this.onButton.disabled = true;
      this.offButton.disabled = false;
    },
    updateButtons: function (data) {
      let pc_status = data.pc_status;
      if (pc_status == "Detenida") {
        this.enableOnButon();
      } else if (pc_status == "En ejecución") {
        this.enableOffButton();
      } else {
        this.onButton.disabled = false;
        this.offButton.disabled = false;
      }
    },
    change_status: function (data) {
      let browser_status = data.browser_status;
      let pc_status = data.pc_status;

      // Actualiza el status del Panel para el PC
      this.statusPanel.textContent = pc_status;

      // Actualiza el Panel del PC
      if (browser_status == "En ejecución") {
        this.pcControl.style.display = "block";
      } else {
        this.pcControl.style.display = "none";
      }

      // Actualiza los Botones de encendido y apagado
      this.updateButtons(data);
    },
  };

  const Browser = {
    loadButton: document.getElementById("loadBrowserButton"),
    statusPanel: document.getElementById("browserStatus"),
    change_status: function (data) {
      let browser_status = data.browser_status;
      // Actualiza el status del Panel para el navegador
      this.statusPanel.textContent = browser_status;

      // Actualiza el boton para cargar el navegador
      if (browser_status == "Detenida") {
        this.loadButton.disabled = false;
      } else {
        this.loadButton.disabled = true;
      }

      PC.change_status(data);
    },
  };

  fetchUpdateStatus();

  Browser.loadButton.addEventListener("click", function () {
    Browser.loadButton.disabled = true;
    Browser.statusPanel.textContent = "Cargando...";
    fetch("/host/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfmiddlewaretoken,
      },
      body: JSON.stringify({
        a: "turnOnBrowser",
        value: true,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        Browser.change_status(data);
      })
      .catch((error) => {
        console.error("Error al obtener el estado del navegador:", error);
      });
  });

  function fetchUpdateStatus() {
    fetch("/host/api/status")
      .then((response) => response.json())
      .then((data) => {
        Browser.change_status(data);
      })
      .catch((error) => {
        console.error("Error al obtener el estado del navegador:", error);
      });
  }
});
