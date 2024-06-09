document.addEventListener("DOMContentLoaded", function () {
  const loadBrowserButton = document.getElementById("loadBrowserButton");
  const browserStatusSpan = document.getElementById("browserStatus");
  const pcControlDiv = document.getElementById("pcControl");
  const turnOnPCButton = document.getElementById("turnOnPCButton");
  const turnOffPCButton = document.getElementById("turnOffPCButton");

  fetchUpdateBrowserStatus();

  loadBrowserButton.addEventListener("click", function () {
    loadBrowserButton.disabled = true;
    intervalId = setInterval(() => {
      fetchUpdateBrowserStatus();
    }, 2000);

    fetch("/host/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
    });
  });

  function fetchUpdateBrowserStatus() {
    fetch("/host/api/browser-status")
      .then((response) => response.json())
      .then((data) => {
        let status = data.browser_status;
        browserStatusSpan.textContent = status;

        if (status == "En ejecución") {
          pcControlDiv.style.display = "block";
        }
      })
      .catch((error) => {
        console.error("Error al obtener el estado del navegador:", error);
      });
  }
});
