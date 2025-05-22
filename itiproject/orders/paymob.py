import requests
from django.conf import settings

def get_paymob_token():
    url = "https://accept.paymobsolutions.com/api/auth/tokens"
    response = requests.post(url, json={"api_key": settings.PAYMOB_API_KEY})
    
    if response.status_code == 201:
        return response.json()["token"]
    else:
        raise Exception("Failed to get Paymob auth token")

def create_paymob_order(auth_token, amount_cents, items=[]):
    url = "https://accept.paymobsolutions.com/api/ecommerce/orders"

    payload = {
        "auth_token": auth_token,
        "delivery_needed": False,
        "amount_cents": amount_cents,
        "items": items  # optional, can be empty
    }

    response = requests.post(url, json=payload)
    if response.status_code == 201:
        return response.json()["id"]  # Paymob Order ID
    else:
        raise Exception("Failed to create Paymob order")

def generate_payment_key(auth_token, order_id, amount_cents, billing_data):
    url = "https://accept.paymob.com/api/acceptance/payment_keys"

    payload = {
        "auth_token": auth_token,
        "amount_cents": amount_cents,
        "expiration": 3600,
        "order_id": order_id,
        "billing_data": billing_data,
        "currency": "EGP",
        "integration_id": 5100998,  # your Paymob integration ID
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["token"]


def generate_paymob_payment_key(auth_token, amount_cents, order_id, billing_data):
    url = "https://accept.paymob.com/api/acceptance/payment_keys"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "auth_token": auth_token,
        "amount_cents": amount_cents,
        "expiration": 3600,
        "order_id": order_id,
        "billing_data": billing_data,
        "currency": "EGP",
        "integration_id": settings.PAYMOB_INTEGRATION_ID,  # You must set this in settings.py
        "lock_order_when_paid": "false"
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()["token"]



