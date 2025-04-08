import re

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/dummy_orchestrator", tags=["dummy_orchestrator"])

# Dummy global variables
date_str = ""
time_str = ""


class OrchestratorRequest(BaseModel):
    message: str


class OrchestratorResponse(BaseModel):
    agent_name: str
    data_type: str
    data: dict
    message: str


def parse_date_and_time(message: str):
    global date_str, time_str
    """
    Parses date/time from a user message. Example inputs:
      "28 mar, 10:00 am", "28 mar 10:00am", "10:00 pm 29 mar", "14:30 29 mar", etc.
    Returns (date_str, time_str) or ("", "") if not found.
      - date_str example: "28 March 2025"
      - time_str example: "10:00 AM"
    """

    # Lowercase for matching
    text = message.lower()

    # Regex for e.g. "28 mar", "29 mar", "1 apr"
    date_regex = r"\b(\d{1,2})\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b"
    # Regex for e.g. "10", "10:00", "10am", "10:00 pm", "14:30" etc.
    time_regex = r"\b(\d{1,2})(?::(\d{1,2}))?\s*(am|pm)?\b"

    date_match = re.search(date_regex, text)

    # --- Parse date ---
    month_map = {
        "jan": "January",
        "feb": "February",
        "mar": "March",
        "apr": "April",
        "may": "May",
        "jun": "June",
        "jul": "July",
        "aug": "August",
        "sep": "September",
        "oct": "October",
        "nov": "November",
        "dec": "December",
    }

    if date_match:
        day = date_match.group(1)  # e.g. "28"
        month_abbrev = date_match.group(2)  # e.g. "mar"
        month_full = month_map.get(month_abbrev, month_abbrev.capitalize())
        date_str = f"{day} {month_full} 2025"

        # --- New: search for time after the date substring ---
        time_search_text = text[date_match.end() :]
    else:
        time_search_text = text

    time_match = re.search(time_regex, time_search_text)

    # --- Parse time ---
    if time_match:
        hour_str = time_match.group(1)  # e.g. "10" or "14"
        minute_str = time_match.group(2)  # e.g. "00" or None
        ampm = time_match.group(3)  # e.g. "am", "pm", or None

        hour = int(hour_str)
        minute = int(minute_str) if minute_str else 0

        # If user typed an explicit am/pm, use it. Otherwise, guess:
        #   - 0 => 12 AM (midnight)
        #   - 1..11 => AM
        #   - 12..23 => PM
        if not ampm:
            if hour == 0:
                ampm = "am"
                hour_12 = 12
            elif hour < 12:
                ampm = "am"
                hour_12 = hour
            else:
                ampm = "pm"
                hour_12 = hour - 12 if hour > 12 else 12
        else:
            ampm = ampm.lower()
            if hour > 12:
                hour_12 = hour - 12
            elif hour == 0:
                hour_12 = 12
            else:
                hour_12 = hour

        time_str = f"{hour_12}:{minute:02d} {ampm.upper()}"

    return date_str, time_str


@router.post("", response_model=OrchestratorResponse)
async def orchestrate(request: OrchestratorRequest):
    global date_str, time_str
    user_message = request.message.lower().strip()

    if "history" in user_message:
        return OrchestratorResponse(
            agent_name="Vaccine Record Agent",
            data_type="vaccine_record",
            data={"vaccines": ["Influenza (INF)", "Hepatitis B (HepB)"]},
            message="Here is your vaccination history.",
        )

    elif any(word in user_message for word in ["change", "reschedule", "update"]):
        # The user wants to change the date/time of an existing booking.
        # Return the same booking slots or potentially different ones if you want
        return OrchestratorResponse(
            agent_name="Booking Agent",
            data_type="booking_slots",
            data={"slots": ["1 Apr, 9:00 AM", "2 Apr, 1:00 PM", "3 Apr, 4:00 PM"]},
            message="Sure. Please choose a new date/time for your booking.",
        )

    elif "book" in user_message:
        return OrchestratorResponse(
            agent_name="Vaccine List Provider Agent",
            data_type="vaccine_list",
            data={
                "vaccines": [
                    "Influenza (INF)",
                    "Pneumococcal Conjugate (PCV13)",
                    "Human Papillomavirus (HPV)",
                    "Tetanus, Diphtheria, Pertussis (Tdap)",
                ]
            },
            message="Sure. Here are some recommended vaccines, please select one.",
        )

    elif user_message in [
        "influenza (inf)",
        "pneumococcal conjugate (pcv13)",
        "human papillomavirus (hpv)",
        "tetanus, diphtheria, pertussis (tdap)",
    ]:
        return OrchestratorResponse(
            agent_name="Booking Agent",
            data_type="booking_slots",
            data={"slots": ["28 Mar, 10:00 AM", "29 Mar, 2:00 PM", "30 Mar, 11:00 AM"]},
            message="Ok. Please select a booking slot from the following options.",
        )

    elif any(
        keyword in user_message
        for keyword in ["28 mar", "29 mar", "30 mar", "1 apr", "2 apr", "3 apr"]
    ):
        date_str, time_str = parse_date_and_time(user_message)
        return OrchestratorResponse(
            agent_name="Booking Agent",
            data_type="booking_details",
            data={
                "clinic": "Sengkang Polyclinic",
                "vaccine": "Influenza (INF)",
                "date": date_str,
                "time": time_str,
            },
            message="Please confirm these booking details.",
        )

    elif "confirm" in user_message:
        return OrchestratorResponse(
            agent_name="Booking Agent",
            data_type="booking_success",
            data={
                "clinic": "Sengkang Polyclinic",
                "vaccine": "Influenza (INF)",
                "date": date_str,
                "time": time_str,
            },
            message="Your booking has been confirmed! Please arrive 15 minutes earlier.",
        )

    # Fallback
    return OrchestratorResponse(
        agent_name="Orchestrator Agent",
        data_type="general_query_response",
        data={"link": "https://uat.hhtest.sg/"},
        message="For more information, please visit our website.",
    )
