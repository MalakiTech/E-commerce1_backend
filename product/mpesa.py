import base64
from datetime import datetime
import requests
from django.conf import settings

BASE_URL = (
    "https://api.safaricom.co.ke"
    if settings.MPESA_ENV == "production"
    else "https://sandbox.safaricom.co.ke"
)


def _timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")


def normalize_phone(phone):
    """Converts 07XXXXXXXX or +2547XXXXXXXX to 2547XXXXXXXX for Daraja."""
    p = phone.replace(" ", "")
    if p.startswith("+"):
        p = p[1:]
    if p.startswith("0"):
        p = "254" + p[1:]
    return p


def get_access_token():
    auth = base64.b64encode(
        f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
    ).decode()
    resp = requests.get(
        f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
        headers={"Authorization": f"Basic {auth}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def stk_push(phone, amount, account_ref, description="Malaki order payment"):
    """Triggers the 'Enter M-Pesa PIN' prompt on the customer's phone."""
    token = get_access_token()
    ts = _timestamp()
    password = base64.b64encode(
        f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{ts}".encode()
    ).decode()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": ts,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(round(amount)),
        "PartyA": normalize_phone(phone),
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": normalize_phone(phone),
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": description,
    }

    resp = requests.post(
        f"{BASE_URL}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()  # {MerchantRequestID, CheckoutRequestID, ResponseCode, ...}
