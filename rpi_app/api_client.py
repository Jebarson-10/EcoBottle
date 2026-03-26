"""
Firebase Admin Client for interacting with Firestore.
Replaces the old REST API client.
"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import config
import os

# Initialize Firebase Admin SDK
_db = None

def _get_db():
    global _db
    if _db is None:
        try:
            # Check if credentials file exists
            if not os.path.exists(config.FIREBASE_CREDENTIALS_PATH):
                raise FileNotFoundError(f"Firebase credentials not found at {config.FIREBASE_CREDENTIALS_PATH}")
            
            cred = credentials.Certificate(config.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            _db = firestore.client()
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise e
    return _db

def submit_deposit(register_number: str, weight_grams: float) -> dict:
    """
    Submit a bottle deposit directly to Firestore.
    
    Args:
        register_number: The user's register number
        weight_grams: Weight of the bottle in grams
        
    Returns:
        dict with 'success', 'points_earned', 'total_points', 'message' keys
    """
    try:
        db = _get_db()
        points_earned = round(weight_grams * config.POINTS_PER_GRAM, 2)
        
        user_ref = db.collection('users').document(register_number)
        
        # Use a transaction to update points and add transaction record
        @firestore.transactional
        def update_in_transaction(transaction, user_ref):
            snapshot = user_ref.get(transaction=transaction)
            
            if snapshot.exists:
                new_total = round(float(snapshot.get('total_points')) + points_earned, 2)
                transaction.update(user_ref, {
                    'total_points': new_total,
                    'last_deposit': firestore.SERVER_TIMESTAMP
                })
            else:
                new_total = points_earned
                transaction.set(user_ref, {
                    'register_number': register_number,
                    'total_points': new_total,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'last_deposit': firestore.SERVER_TIMESTAMP
                })
                
            # Add transaction record to sub-collection
            trans_ref = user_ref.collection('transactions').document()
            transaction.set(trans_ref, {
                'weight_grams': float(weight_grams),
                'points_earned': float(points_earned),
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            
            return new_total

        transaction = db.transaction()
        total_points = update_in_transaction(transaction, user_ref)

        return {
            "success": True,
            "points_earned": points_earned,
            "total_points": total_points,
            "message": f"Successfully deposited! Earned {points_earned} points."
        }
        
    except FileNotFoundError as e:
        return {
            "success": False,
            "message": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Firebase error: {str(e)}"
        }

def get_points(register_number: str) -> dict:
    """
    Get current points for a register number from Firestore.
    """
    try:
        db = _get_db()
        user_doc = db.collection('users').document(register_number).get()
        
        if user_doc.exists:
            data = user_doc.data()
            return {
                "success": True,
                "total_points": data.get("total_points", 0),
                "register_number": register_number
            }
        else:
            return {
                "success": True,
                "total_points": 0,
                "register_number": register_number,
                "message": "New user - no deposits yet."
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
