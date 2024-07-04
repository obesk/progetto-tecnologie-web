document.addEventListener("DOMContentLoaded", function () {
  if (Notification.permission !== "granted") {
    Notification.requestPermission().then(function (permission) {
      if (permission === "granted") {
        new Notification("Notifications enabled!");
      }
    });
  }

  function initWebSocket(artworkId) {
    var socket = new WebSocket(
      "ws://" + window.location.host + "/ws/bids/" + artworkId + "/"
    );

    socket.onopen = function (event) {
      console.log("WebSocket connection established:", event);
    };

    socket.onmessage = function (event) {
      console.log("WebSocket message received:", event.data);
      var data = JSON.parse(event.data);
      var message = data["message"];

      if (Notification.permission === "granted") {
        new Notification(message.title, { body: message.body });
      }
    };

    socket.onerror = function (event) {
      console.error("WebSocket error observed:", event);
    };

    socket.onclose = function (event) {
      console.log("WebSocket connection closed. Reconnecting...", event);
      setTimeout(function () {
        initWebSocket(artworkId);
      }, 5000);
    };
  }

  var artworkElement = document.getElementById("artwork");
  if (artworkElement) {
    var artworkId = artworkElement.getAttribute("data-artwork-id");
    if (artworkId) {
      initWebSocket(artworkId);
    }
  }
});
