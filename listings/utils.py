from geopy.geocoders import Nominatim

def get_location_details(lat: float, lon: float) -> dict:
    """
    Koordinatalarga qarab viloyat (region) va tumanni (district) aniqlash funksiyasi.
    """
    # Geolocator obyektini yaratamiz
    geolocator = Nominatim(user_agent="uzb_geo_resolver")

    # Standart qaytadigan javob strukturasi
    result = {
        "region": "Topilmadi",
        "district": "Topilmadi",
        "full_address": "Topilmadi"
    }

    try:
        # Koordinatani tekshiramiz
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)

        if location and location.raw:
            address = location.raw.get('address', {})

            # To'liq manzilni saqlaymiz
            result["full_address"] = location.address

            # Viloyatni aniqlash ('state' yoki 'region')
            result["region"] = address.get('state') or address.get('region') or "Topilmadi"

            # Tumanni aniqlash ('county', 'suburb' yoki 'district')
            result["district"] = address.get('county') or address.get('suburb') or address.get('district') or "Topilmadi"

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")

    return result

# --- Funksiyani tekshirib ko'rish ---
# Misol: Samarqand shahri atrofidagi koordinata
lat_input = 39.6542
lon_input = 66.9597

location_data = get_location_details(lat_input, lon_input)
print(location_data)
