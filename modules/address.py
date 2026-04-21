from typing import Callable, Optional
from geopy.geocoders import Nominatim

def lookup(
    query: str,
    on_line: Optional[Callable[[str], None]],
    on_tool_start: Optional[Callable[[str], None]] = None,
) -> list[dict]:
    if on_tool_start:
        on_tool_start("nominatim")
    geolocator = Nominatim(user_agent="iCrackU-osint")
    try:
        location = geolocator.geocode(query, addressdetails=True, language="en")
    except Exception as e:
        return [{"tool": "nominatim", "query": query, "returncode": -1, "output": str(e)}]

    if location is None:
        output = "No results found."
        returncode = 1
    else:
        lines = [
            f"Address:   {location.address}",
            f"Latitude:  {location.latitude}",
            f"Longitude: {location.longitude}",
            f"Type:      {location.raw.get('type', 'unknown')}",
        ]
        output = "\n".join(lines)
        returncode = 0

    if on_line and returncode == 0:
        for line in output.splitlines():
            on_line(line)

    return [{"tool": "nominatim", "query": query, "returncode": returncode, "output": output}]
