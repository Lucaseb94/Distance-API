def combine_stops_with_route(
    original_stops,
    route_stops,
    final_order_indexes=None,
    intermediate_order=None
):
    ordered_original = order_stops_by_indexes(
        original_stops,
        final_order_indexes
    ) or order_stops_by_intermediates(
        original_stops,
        intermediate_order
    )
    ordered_stops = []

    for index, route_stop in enumerate(route_stops):
        original_stop = (
            ordered_original[index]
            if index < len(ordered_original)
            else {}
        )
        ordered_stops.append({
            "ordem": index + 1,
            "cep": original_stop.get("cep"),
            "numero": original_stop.get("numero"),
            "endereco": route_stop.get("endereco"),
            "lat": route_stop.get("lat"),
            "lng": route_stop.get("lng")
        })

    return ordered_stops


def order_stops_by_indexes(stops, final_order_indexes):
    if not isinstance(final_order_indexes, list):
        return None

    ordered_stops = [
        stops[index]
        for index in final_order_indexes
        if isinstance(index, int) and 0 <= index < len(stops)
    ]

    if len(ordered_stops) != len(stops):
        return None

    return ordered_stops


def order_stops_by_intermediates(stops, intermediate_order):
    if not intermediate_order or len(stops) <= 2:
        return stops

    intermediate_stops = stops[1:-1]
    ordered_intermediates = [
        intermediate_stops[index]
        for index in intermediate_order
        if isinstance(index, int) and 0 <= index < len(intermediate_stops)
    ]

    if len(ordered_intermediates) != len(intermediate_stops):
        return stops

    return [stops[0], *ordered_intermediates, stops[-1]]
