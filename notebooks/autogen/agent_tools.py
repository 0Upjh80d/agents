import os

import requests
from dotenv import load_dotenv, set_key

# from agent_tools import (
#     get_available_booking_slots,
#     get_booking_by_id,
#     schedule_vaccination_slot,
#     cancel_booking,
#     get_vaccination_history,
#     get_user_details,
# get_vaccine_recommendations
# )

"""
===================================================
Development functions
===================================================
"""


# for development, create a new user and login, save access token to environment as 'AUTH_TOKEN'
def register_and_login_user(user_data: dict):
    load_dotenv(dotenv_path="../../.env", override=True)
    BACKEND_DB_URL = os.getenv("BACKEND_DB_URL")

    reg_url = f"{BACKEND_DB_URL}/signup"
    login_url = f"{BACKEND_DB_URL}/login"

    response = requests.post(reg_url, json=user_data)
    if response.status_code == 201:
        print("User registered successfully!")

        login_url = f"{BACKEND_DB_URL}/login"
        login_data = {
            "grant_type": "password",  # Required
            "username": user_data["email"],  # Email used for login
            "password": user_data["password"],  # Password used for login
            "scope": "",  # Optional (empty value sent)
            "client_id": "",  # Optional (empty value sent)
            "client_secret": "",  # Optional (empty value sent)
        }
        response = requests.post(
            login_url, data=login_data
        )  # receive access_token after login
        if response.status_code == 200:
            print("User logged in successfully!")
            access_token = response.json().get("access_token")
            if access_token:
                print("Access token received.")
                os.environ["AUTH_TOKEN"] = access_token
                set_key(".env", "AUTH_TOKEN", access_token)

                print("Access token saved to environment.")
            else:
                print("No access token found in response.")

        else:
            print("Failed to login user:", response.json())
    elif response.status_code == 409:
        print("User already exists.")
        print("User registered successfully!")

        login_url = f"{BACKEND_DB_URL}/login"
        login_data = {
            "grant_type": "password",  # Required
            "username": user_data["email"],  # Email used for login
            "password": user_data["password"],  # Password used for login
            "scope": "",  # Optional (empty value sent)
            "client_id": "",  # Optional (empty value sent)
            "client_secret": "",  # Optional (empty value sent)
        }
        response = requests.post(login_url, data=login_data)
        if response.status_code == 200:
            print("User logged in successfully!")
            access_token = response.json().get("access_token")
            if access_token:
                print("Access token received.")
                os.environ["AUTH_TOKEN"] = access_token
                set_key(".env", "AUTH_TOKEN", access_token)

                print("Access token saved to environment.")
            else:
                print("No access token found in response.")
    else:
        print("Failed to register user:", response.json())

    return response.json()


"""
===================================================
Authentication functions
===================================================
"""
### POST /signup
## TODO: now assume user has already signed up using UI


### POST /login
## TODO: now assume user has already logged in using UI
def login_with_email_password_and_set_access_token(
    email: str, password: str, verbose: bool = False
):
    load_dotenv(dotenv_path="../../.env", override=True)
    BACKEND_DB_URL = os.getenv("BACKEND_DB_URL")
    CLIENT_ID = os.getenv("CLIENT_ID", None)
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", None)
    SCOPE = os.getenv("AUTH_SCOPE", None)

    payload = {
        "grant_type": "password",
        "username": email,
        "password": password,
        "scope": SCOPE,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(f"{BACKEND_DB_URL}/login", data=payload)

    if response.status_code == 200:
        token_data = response.json()
        if verbose:
            print("✅ Login successful. Access token received.")
        os.environ["AUTH_TOKEN"] = token_data.get("access_token")
        return token_data
    else:
        if verbose:
            print("❌ Login failed:", response.status_code)
        return response.json()


"""
===================================================
Booking functions
===================================================
"""


### GET /bookings/available_slots
# remark: assumed logged in
# return: list of {id (booking_id), datetime, polyclinic, vaccine_id}
def get_available_booking_slots(
    vaccine_name: str,
    polyclinic_limit: int = None,
    timeslot_limit: int = None,
    verbose: bool = False,
):
    load_dotenv(dotenv_path="../../.env", override=True)
    BACKEND_DB_URL = os.getenv("BACKEND_DB_URL")
    auth_token = os.getenv("AUTH_TOKEN")

    if not auth_token:
        if verbose:
            print("Access token not found.")
        return

    params = {"vaccine_name": vaccine_name}
    if polyclinic_limit:
        params["polyclinic_limit"] = polyclinic_limit
    if timeslot_limit:
        params["timeslot_limit"] = timeslot_limit

    headers = {"Authorization": f"Bearer {auth_token}"}

    response = requests.get(
        f"{BACKEND_DB_URL}/bookings/available", params=params, headers=headers
    )

    if response.status_code == 200:
        if verbose:
            print("Available slots retrieved successfully.")
        slots = response.json()

        # filter unused key value pairs
        filtered_slots = []
        for slot in slots:
            filtered_slot = {
                "booking_slot_id": slot["id"],
                "datetime": slot["datetime"],
                "polyclinic_name": slot["polyclinic"]["name"],
                "poluclinic_id": slot["polyclinic"]["id"],
                "vaccine_id": slot["vaccine_id"],
            }
            filtered_slots.append(filtered_slot)
        return filtered_slots
    else:
        if verbose:
            print("Failed to fetch available slots:", response.status_code)
        return response.json()


### GET /bookings/{id}
# description: get booking details by booking_id
def get_booking_by_id(booking_id: str, verbose: bool = False):
    load_dotenv(dotenv_path="../../.env", override=True)
    BACKEND_DB_URL = os.getenv("BACKEND_DB_URL")
    auth_token = os.getenv("AUTH_TOKEN")

    if not auth_token:
        if verbose:
            print("Access token not found.")
        return

    headers = {"Authorization": f"Bearer {auth_token}"}

    response = requests.get(f"{BACKEND_DB_URL}/bookings/{booking_id}", headers=headers)

    if response.status_code == 200:
        if verbose:
            print("Booking details retrieved.")
        return response.json()
    else:
        if verbose:
            print("Failed to get booking:", response.status_code)
        return response.json()


### POST /bookings/schedule
# remark: booking_slot_id can be obtained from get_available_booking_slots["slot_index"]["id"]
def schedule_vaccination_slot(booking_slot_id: str, verbose: bool = False):
    load_dotenv(dotenv_path="../../.env", override=True)
    BACKEND_DB_URL = os.getenv("BACKEND_DB_URL")
    auth_token = os.getenv("AUTH_TOKEN")

    if not auth_token:
        if verbose:
            print("Access token not found.")
        return

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    payload = {"booking_slot_id": booking_slot_id}

    response = requests.post(
        f"{BACKEND_DB_URL}/bookings/schedule", json=payload, headers=headers
    )

    if response.status_code == 201:
        if verbose:
            print("Vaccination slot scheduled successfully.")
        return response.json()
    else:
        if verbose:
            print("Failed to schedule slot:", response.status_code)
        return response.json()


### DELETE /bookings/cancel/{record_id}
# remark: assumed logged in
# description: cancel a booking by record_id, i.e. primary key in vaccine_records table
def cancel_booking(record_id: str, verbose: bool = False):
    load_dotenv(dotenv_path="../../.env", override=True)
    BACKEND_DB_URL = os.getenv("BACKEND_DB_URL")
    auth_token = os.getenv("AUTH_TOKEN")

    if not auth_token:
        if verbose:
            print("Access token not found.")
        return

    headers = {"Authorization": f"Bearer {auth_token}"}

    response = requests.delete(
        f"{BACKEND_DB_URL}/bookings/cancel/{record_id}", headers=headers
    )

    if response.status_code == 200:
        if verbose:
            print("Booking cancelled successfully.")
        return response.json()
    else:
        if verbose:
            print("Failed to cancel booking:", response.status_code)
        return response.json()


"""
===================================================
Chat functions
===================================================
"""
### POST /chat

"""
===================================================
Record functions (vaccination)
===================================================
"""


### GET /records
# login needed, i.e. must have auth_token in environment
# description: get vaccination history for currently login user
def get_vaccination_history(verbose: bool = False):
    load_dotenv(dotenv_path="../../.env", override=True)
    BACKEND_DB_URL = os.getenv("BACKEND_DB_URL")
    auth_token = os.getenv("AUTH_TOKEN")

    if not auth_token:
        if verbose:
            print("Access token not found. Please register and log in first.")
        return

    # Define the URL for fetching vaccination records
    records_url = f"{BACKEND_DB_URL}/records"

    # Set headers with the Authorization token
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json",
    }

    # Send the GET request
    response = requests.get(records_url, headers=headers)
    if response.status_code == 200:
        if verbose:
            print("Vaccination history retrieved successfully!")
        slots = response.json()
        # filter unused key value pairs
        filtered_slots = []
        for slot in slots:
            booking_slot_id = slot["booking_slot_id"]
            vaccine_name = get_vaccination_name_by_booking_id(booking_slot_id)

            filtered_slot = {
                "vaccination_booking_id": slot["id"],
                "status": slot["status"],
                "booking_slot_id": booking_slot_id,
                "vaccine_name": vaccine_name,
            }
            filtered_slots.append(filtered_slot)
        return filtered_slots
    elif (
        response.status_code == 404
        and response.json().get("detail") == "No records found."
    ):
        if verbose:
            print("No vaccination records found.")
        return response.json()
    else:
        if verbose:
            print(
                f"Failed to retrieve vaccination history. Status code: {response.status_code}"
            )
            print(response.json())
        return response.json()


"""
===================================================
User functions
===================================================
"""


### GET /users
# remark: login needed, i.e. must have auth_token in environment
# description: get user details of the currently logged in user
def get_user_details(verbose: bool = False):
    load_dotenv(dotenv_path="../../.env", override=True)
    BACKEND_DB_URL = os.getenv("BACKEND_DB_URL")
    auth_token = os.getenv("AUTH_TOKEN")

    if not auth_token and verbose:
        print("Access token not found. Please register and log in first.")
        return

    # Define the URL for fetching user details
    user_details_url = f"{BACKEND_DB_URL}/users/"

    # Set headers with the Authorization token
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    # Send the POST request
    response = requests.get(user_details_url, headers=headers)

    if response.status_code == 200:
        if verbose:
            print("User details retrieved successfully!")
        user_details = response.json()
        # print(user_details)
        return user_details
    else:
        if verbose:
            print(
                f"Failed to retrieve user details. Status code: {response.status_code}"
            )
        return response.json()


### PUT /users
### DELETE /users/{id}


"""
===================================================
Vaccine functions
===================================================
"""


### GET /vaccines/recommendations
# Remark: the user is assumed to be logged in already
def get_vaccine_recommendations(verbose: bool = False):
    load_dotenv(dotenv_path="../../.env", override=True)
    BACKEND_DB_URL = os.getenv("BACKEND_DB_URL")
    auth_token = os.getenv("AUTH_TOKEN")

    if not auth_token and verbose:
        print("Access token not found. Please register and log in first.")
        return

    recommendations_url = f"{BACKEND_DB_URL}/vaccines/recommendations"

    headers = {"Authorization": f"Bearer {auth_token}", "Accept": "application/json"}

    response = requests.get(recommendations_url, headers=headers)

    if response.status_code == 200:
        if verbose:
            print("Vaccine recommendations retrieved successfully!")
        return response.json()
    else:
        if verbose:
            print(
                f"Failed to retrieve vaccine recommendations. Status code: {response.status_code}"
            )
        return response.json()


"""
===================================================
default functions
===================================================
"""

"""
=====
transfer functions
=====
"""

vaccine_records_topic_type = "VaccineRecordsAgent"
vaccine_recommendation_topic_type = "VaccineRecommenderAgent"
appointment_topic_type = "AppointmentAgent"
triage_agent_topic_type = "TriageAgent"


def transfer_to_vaccine_records_agent() -> str:
    return vaccine_records_topic_type


def transfer_to_recommender_agent() -> str:
    return vaccine_recommendation_topic_type


def transfer_to_appointment_agent() -> str:
    return appointment_topic_type


def transfer_back_to_triage() -> str:
    return triage_agent_topic_type


"""
=====
Helper functions
=====
"""


def get_vaccination_name_by_booking_id(
    booking_slot_id: str, verbose: bool = False
) -> str | None:
    res_booking = get_booking_by_id(booking_slot_id, verbose)
    if not res_booking.get("details", None):
        vaccination_type = res_booking["vaccine"]["name"]
        return vaccination_type
    else:
        return None


# Test the functions
if __name__ == "__main__":

    pass
