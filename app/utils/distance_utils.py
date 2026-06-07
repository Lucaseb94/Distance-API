def duration_to_seconds(duration):
    if not isinstance(duration, str) or not duration.endswith("s"):
        return None

    try:
        return float(duration[:-1])
    except ValueError:
        return None


def seconds_to_minutes(seconds):
    if type(seconds) not in (int, float):
        return None

    return round(seconds / 60, 2)


def meters_to_km(distance_meters):
    if type(distance_meters) not in (int, float):
        return None

    return round(distance_meters / 1000, 2)
