"""
This files contains the wrapper for the agent_tools module.
Modifiable part: descriptions of functions when wrapped with autogen_tools
"""

from agent_tools import (
    cancel_booking,
    get_available_booking_slots,
    get_booking_by_id,
    get_nearest_polyclinic,
    get_user_details,
    get_vaccination_history,
    get_vaccine_recommendations,
    login_with_email_password_and_set_access_token,
    schedule_vaccination_slot,
    transfer_back_to_triage,
    transfer_to_appointment_agent,
    transfer_to_recommender_agent,
    transfer_to_vaccine_records_agent,
)
from autogen_core.tools import FunctionTool

# from agent_tools_wrapper import (
#     get_available_booking_slots_tool,
#     get_booking_by_id_tool,
#     schedule_vaccination_slot_tool,
#     cancel_booking_tool,
#     get_vaccination_history_tool,
#     get_user_details_tool,
#     get_vaccine_recommendations_tool,
#     get_nearest_polyclinic_tool,
#     transfer_back_to_triage_tool,
#     transfer_to_appointment_agent_tool,
#     transfer_to_recommender_agent_tool,
#     transfer_to_vaccine_records_agent_tool
# )
"""
===================================================
Development functions
===================================================
"""


"""
===================================================
Authentication functions
===================================================
"""
### POST /signup
## TODO: now assume user has already signed up using UI

### POST /login
login_with_email_password_and_set_access_token_tool = FunctionTool(
    login_with_email_password_and_set_access_token,
    description="Logs in a user with an email and password, and sets the access token to environment so all functions are authenticated to be used.",
)

"""
===================================================
Booking functions
===================================================
"""

### GET /bookings/available_slots
# remark: assumed logged in
# return: list of {id (booking_id), datetime, polyclinic, vaccine_id}
get_available_booking_slots_tool = FunctionTool(
    get_available_booking_slots,
    description="Returns available booking slots for a specified vaccine."
    "Accepts optional polyclinic and timeslot limits, which filters the list."
    "The response is a list, each entry includes booking ID('id'), datetime, polyclinic, and vaccine_id.",
)


### GET /bookings/{id}
# description: get booking details by booking_id
get_booking_by_id_tool = FunctionTool(
    get_booking_by_id,
    description="Retrieves booking details for a specific booking slot using its ID, regardless of the status being booked, cancelled, or completed."
    "The details include the booking ID ('id'), datetime, polyclinic, and vaccine_id.",
)

### POST /bookings/schedule
# remark: booking_slot_id can be obtained from get_available_booking_slots["slot_index"]["id"]
schedule_vaccination_slot_tool = FunctionTool(
    schedule_vaccination_slot,
    description="Schedules a vaccination slot for the logged-in user by providing a valid booking slot id (the 'id' from booking slot)."
    "If successful, the response includes the vaccine record ID ('id'), which has a field with values 'booked' or 'completed'.",
)

### DELETE /bookings/cancel/{record_id}
# remark: assumed logged in
# description: cancel a booking by record_id, i.e. primary key in vaccine_records table
cancel_booking_tool = FunctionTool(
    cancel_booking,
    description="Cancels an existing vaccination appointment by specifying the record ID.",
)


"""
===================================================
Chat functions
===================================================
"""
### POST /chat

"""
===================================================
Clinic functions
===================================================
"""

# GET /clinic/nearest
get_nearest_polyclinic_tool = FunctionTool(
    get_nearest_polyclinic,
    description="Cancels an existing vaccination appointment by specifying the record ID.",
)

"""
===================================================
Record functions (vaccination)
===================================================
"""
### GET /records
# login needed, i.e. must have auth_token in environment
# description: get vaccination history for currently login user
get_vaccination_history_tool = FunctionTool(
    get_vaccination_history,
    description="Fetch the vaccination history of the currently logged-in user."
    "Each vaccination record includes a unique record ID ('id'), unique booking_slot_id from the booking slots table, time created_at, and status ('booked' or 'completed').",
)


"""
===================================================
User functions
===================================================
"""
### GET /users
# remark: login needed, i.e. must have auth_token in environment
# description: get user details of the currently logged in user
get_user_details_tool = FunctionTool(
    get_user_details,
    description=(
        "Retrieves the currently logged-in user's details, including NRIC, first name, "
        "last name, email, date of birth, gender, address, enrolled clinic, and timestamps "
        "for account creation and last update."
    ),
)


### PUT /users
### DELETE /users/{id}


"""
===================================================
Vaccine functions
===================================================
"""
get_vaccine_recommendations
### GET /vaccines/recommendations
get_vaccine_recommendations_tool = FunctionTool(
    get_vaccine_recommendations,
    description=(
        "Retrieves the recommendation vaccine for the current logged in user. "
        "The recommendation is based on the user's details."
    ),
)
"""
===================================================
default functions
===================================================
"""

"""
=======
transfer tool
=======
"""

transfer_to_vaccine_records_agent_tool = FunctionTool(
    transfer_to_vaccine_records_agent,
    description="Use for retrieval of vaccination records history.",
)
transfer_to_recommender_agent_tool = FunctionTool(
    transfer_to_recommender_agent,
    description="Use for recommendation of vaccinations for user based on user's vaccination history, age and gender.",
)
transfer_to_appointment_agent_tool = FunctionTool(
    transfer_to_appointment_agent,
    description="Use for vaccination-related appointments enquiry, booking, cancellation and rescheduling.",
)
transfer_back_to_triage_tool = FunctionTool(
    transfer_back_to_triage,
    description="Call this if the user brings up a topic outside of your purview.",
)

if __name__ == "__main__":
    # test the functions
    print("Agent tools wrapper loaded.")
