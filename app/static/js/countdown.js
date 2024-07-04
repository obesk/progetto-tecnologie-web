document.addEventListener("DOMContentLoaded", function () {
  var countdownElements = document.querySelectorAll(".countdown");

  countdownElements.forEach(function (element) {
    var auctionEndDate = new Date(
      element.getAttribute("data-auction-end")
    ).getTime();

    var x = setInterval(function () {
      var now = new Date().getTime();
      var distance = auctionEndDate - now;

      var days = Math.floor(distance / (1000 * 60 * 60 * 24));
      var hours = Math.floor(
        (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
      );
      var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((distance % (1000 * 60)) / 1000);

      element.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;

      if (distance < 0) {
        clearInterval(x);
        element.innerHTML = "EXPIRED";
      }
    }, 1000);
  });
});
