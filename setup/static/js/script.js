/* Contador */
document.addEventListener("DOMContentLoaded", function() {
  const dataCasamento = new Date("2026-04-05T15:30:00").getTime();

  const atualizarContador = () => {
    const agora = new Date().getTime();
    const distancia = dataCasamento - agora;

    if (distancia < 0) {
      document.getElementById("countdown").innerHTML = "Já estamos casados! 💍";
      return;
    }

    const dias = Math.floor(distancia / (1000 * 60 * 60 * 24));
    const horas = Math.floor((distancia % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutos = Math.floor((distancia % (1000 * 60 * 60)) / (1000 * 60));

    document.getElementById("dias").innerText = dias;
    document.getElementById("horas").innerText = horas;
    document.getElementById("minutos").innerText = minutos;
  };

  atualizarContador();
  setInterval(atualizarContador, 60000);
});

/* API MAPA */
document.addEventListener("DOMContentLoaded", function () {
  const destino = [-22.81162209144038, -43.20288945718821];

  const map = L.map("map").setView(destino, 13);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: ''
  }).addTo(map);

  const redIcon = L.icon({
    iconUrl: './static/img/gps-2.png',
    iconSize: [41, 41],
    iconAnchor: [12, 41],
  });

  L.marker(destino, { icon: redIcon })
    .addTo(map)
    .bindPopup("Green House Buffet")
    .openPopup();

  let controleDeRota = null;

  document.getElementById("btnTraçarRota").addEventListener("click", () => {
    const enderecoPartida = document.getElementById("enderecoPartida").value;

    if (!enderecoPartida) {
      alert("Digite um endereço válido.");
      return;
    }

    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(enderecoPartida)}`)
      .then((res) => res.json())
      .then((dados) => {
        if (dados.length === 0) {
          alert("Endereço não encontrado.");
          return;
        }

        const origem = [parseFloat(dados[0].lat), parseFloat(dados[0].lon)];

        if (controleDeRota) {
          map.removeControl(controleDeRota);
        }

        controleDeRota = L.Routing.control({
          waypoints: [L.latLng(origem), L.latLng(destino)],
          router: L.Routing.osrmv1({
            serviceUrl: 'https://router.project-osrm.org/route/v1'  // forçando uso do OSRM demo server
          }),
          routeWhileDragging: false,
          createMarker: function (i, wp) {
            return L.marker(wp.latLng, { icon: redIcon });
          },
          lineOptions: {
            styles: [{ color: '#3498db', weight: 5 }]
          }
        }).addTo(map);
    
        map.setView(origem, 13);
      })
      .catch((err) => {
        console.error(err);
        alert("Erro ao buscar endereço.");
      });
  });
});