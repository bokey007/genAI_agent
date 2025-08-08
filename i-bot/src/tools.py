import requests
from src.config import settings

def create_ticket(title: str, description: str):
    """
    Creates a ticket in ServiceNow.
    """
    if not settings.SERVICENOW_URL or not settings.SERVICENOW_API_KEY:
        print("ServiceNow URL or API key not configured. Skipping ticket creation.")
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.SERVICENOW_API_KEY}",
    }
    
    data = {
        "short_description": title,
        "description": description,
    }

    try:
        response = requests.post(settings.SERVICENOW_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating ServiceNow ticket: {e}")
        return None
