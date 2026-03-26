"""
REST API Client for communicating with the Django backend.
"""
import requests
import config


def submit_deposit(register_number: str, weight_grams: float) -> dict:
    """
    Submit a bottle deposit to the Django server.
    
    Args:
        register_number: The user's register number
        weight_grams: Weight of the bottle in grams
        
    Returns:
        dict with 'success', 'points_earned', 'total_points', 'message' keys
    """
    url = f"{config.SERVER_URL}/api/deposit/"
    payload = {
        "register_number": register_number,
        "weight_grams": weight_grams
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 201:
            data = response.json()
            return {
                "success": True,
                "points_earned": data.get("points_earned", 0),
                "total_points": data.get("total_points", 0),
                "message": data.get("message", "Deposit successful!")
            }
        else:
            return {
                "success": False,
                "message": f"Server error: {response.status_code} - {response.text}"
            }
    except requests.ConnectionError:
        return {
            "success": False,
            "message": "Cannot connect to server. Check your network connection."
        }
    except requests.Timeout:
        return {
            "success": False,
            "message": "Server took too long to respond. Try again."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }


def get_points(register_number: str) -> dict:
    """
    Get current points for a register number.
    
    Returns:
        dict with 'success', 'total_points', 'register_number' keys
    """
    url = f"{config.SERVER_URL}/api/points/{register_number}/"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "total_points": data.get("total_points", 0),
                "register_number": data.get("register_number", register_number)
            }
        elif response.status_code == 404:
            return {
                "success": True,
                "total_points": 0,
                "register_number": register_number,
                "message": "New user - no deposits yet."
            }
        else:
            return {
                "success": False,
                "message": f"Server error: {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
