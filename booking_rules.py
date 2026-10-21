CAMPUS_RULES = {
    "Johannesburg": {
        "max_duration_minutes": 120,
        "allowed_hours": (8, 17),
        "description": "Maximum 2 hours per booking, 08:00–17:00 only."
    },
    "Cape Town": {
        "max_duration_minutes": 180,
        "allowed_hours": (9, 16),
        "description": "Max 3 hours per booking, 09:00–16:00 only."
    },
    "Durban": {
        "max_duration_minutes": 90,
        "allowed_hours": (7, 18),
        "description": "Max 90 minutes per booking, 07:00–18:00 only."
    }
}

def validate_booking(campus_name, start_hour, duration_minutes):
    rules = CAMPUS_RULES.get(campus_name)
    if not rules:
        return False, "Unknown campus."

    if duration_minutes > rules["max_duration_minutes"]:
        return False, f"Booking exceeds maximum of {rules['max_duration_minutes']} minutes for {campus_name}."

    open_hour, close_hour = rules["allowed_hours"]
    end_hour = start_hour + (duration_minutes / 60)
    if start_hour < open_hour or end_hour > close_hour:
        return False, f"Booking must be between {open_hour}:00 and {close_hour}:00."
    return True, "Valid."