import requests


def get_location_details(lat: float, lon: float) -> dict:
    """
    Koordinatadan viloyat va tumanni aniqlash
    """

    url = "https://nominatim.openstreetmap.org/reverse"

    params = {
        "lat": lat,
        "lon": lon,
        "format": "jsonv2",
        "accept-language": "uz"
    }

    headers = {
        "User-Agent": "geo-resolver-app"
    }

    result = {
        "region": None,
        "district": None,
        "city": None,
        "full_address": None
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        address = data.get("address", {})

        result["full_address"] = data.get("display_name")

        result["region"] = (
            address.get("state")
            or address.get("province")
            or address.get("region")
        )

        result["district"] = (
            address.get("county")
            or address.get("city_district")
            or address.get("district")
            or address.get("municipality")
        )

        result["city"] = (
            address.get("city")
            or address.get("town")
            or address.get("village")
        )

        return result

    except requests.exceptions.RequestException as e:
        return {
            "error": str(e)
        }


# # TEST
# lat = 39.6542
# lon = 66.9597

# print(get_location_details(lat, lon))