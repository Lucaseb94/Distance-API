import { DEFAULT_CENTER } from "../config.js";


export function createMapView(mapElement) {
  let map;
  let originMarker;
  let destinationMarker;
  let routeLine;
  let stopMarkers = [];

  function init() {
    if (!window.google?.maps || map) {
      return;
    }

    map = new google.maps.Map(mapElement, {
      center: DEFAULT_CENTER,
      zoom: 11,
      mapTypeControl: false,
      fullscreenControl: false,
      streetViewControl: false,
    });
  }

  function clear() {
    if (originMarker) {
      originMarker.setMap(null);
      originMarker = null;
    }

    if (destinationMarker) {
      destinationMarker.setMap(null);
      destinationMarker = null;
    }

    if (routeLine) {
      routeLine.setMap(null);
      routeLine = null;
    }

    stopMarkers.forEach((marker) => marker.setMap(null));
    stopMarkers = [];
  }

  function draw(result) {
    if (!map || !window.google?.maps) {
      return;
    }

    clear();

    const stops = Array.isArray(result.paradas) ? result.paradas : [];
    const bounds = new google.maps.LatLngBounds();

    if (stops.length > 1) {
      drawNumberedStops(stops, bounds);
    } else {
      drawEndpointMarkers(result, bounds);
    }

    drawPolyline(result.polyline, bounds);

    if (!bounds.isEmpty()) {
      map.fitBounds(bounds, 64);
    }
  }

  function drawNumberedStops(stops, bounds) {
    stops.forEach((stop, index) => {
      const position = toLatLng(stop);

      if (!position) {
        return;
      }

      const marker = new google.maps.Marker({
        position,
        map,
        label: String(index + 1),
        title: stop.endereco || `Parada ${index + 1}`,
      });

      stopMarkers.push(marker);
      bounds.extend(position);
    });
  }

  function drawEndpointMarkers(result, bounds) {
    const originPosition = toLatLng(result.origem);
    const destinationPosition = toLatLng(result.destino);

    if (originPosition) {
      originMarker = new google.maps.Marker({
        position: originPosition,
        map,
        title: "Origem",
      });
      bounds.extend(originPosition);
    }

    if (destinationPosition) {
      destinationMarker = new google.maps.Marker({
        position: destinationPosition,
        map,
        title: "Destino",
      });
      bounds.extend(destinationPosition);
    }
  }

  function drawPolyline(polyline, bounds) {
    if (!polyline || !google.maps.geometry?.encoding) {
      return;
    }

    const path = google.maps.geometry.encoding.decodePath(polyline);
    routeLine = new google.maps.Polyline({
      path,
      map,
      strokeColor: "#0f766e",
      strokeOpacity: 0.95,
      strokeWeight: 5,
    });

    path.forEach((point) => bounds.extend(point));
  }

  function toLatLng(address) {
    if (
      !address
      || typeof address.lat !== "number"
      || typeof address.lng !== "number"
    ) {
      return null;
    }

    return { lat: address.lat, lng: address.lng };
  }

  return {
    init,
    clear,
    draw,
  };
}
