const state = {
  currentRoute: null,
  destinationMode: "automatico",
};


export function setCurrentRoute(route) {
  state.currentRoute = route;
}


export function getCurrentRoute() {
  return state.currentRoute;
}


export function setDestinationMode(mode) {
  state.destinationMode = mode;
}


export function getDestinationMode() {
  return state.destinationMode;
}
