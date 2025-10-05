# backend/services/error_recovery.py
from typing import Dict, Any, List

class ErrorRecoveryService:
    """
    Handles error scenarios and provides recovery options
    """
    
    def handle_out_of_stock(
        self,
        product_name: str,
        alternatives: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle out of stock scenario"""
        
        recovery_message = f"Unfortunately, {product_name} is currently out of stock. "
        
        if alternatives:
            recovery_message += f"However, I found {len(alternatives)} similar items you might love:\n\n"
            for i, alt in enumerate(alternatives[:3], 1):
                recovery_message += f"{i}. {alt['name']} - ${alt['price']}\n"
                recovery_message += f"   {alt.get('reason', 'Great alternative!')}\n\n"
        else:
            recovery_message += "Would you like me to:\n"
            recovery_message += "• Notify you when it's back in stock\n"
            recovery_message += "• Show you similar items\n"
            recovery_message += "• Help you find something else"
        
        return {
            "recovery_type": "out_of_stock",
            "message": recovery_message,
            "alternatives": alternatives,
            "actions": [
                {"type": "notify", "label": "Notify Me"},
                {"type": "alternatives", "label": "Show Similar Items"},
                {"type": "browse", "label": "Browse Other Items"}
            ]
        }
    
    def handle_payment_failure(
        self,
        error_type: str,
        cart_total: float
    ) -> Dict[str, Any]:
        """Handle payment failure scenarios"""
        
        recovery_options = []
        
        if error_type == "insufficient_funds":
            recovery_message = "It looks like there might be an issue with your payment method."
            recovery_options = [
                {
                    "option": "use_loyalty_points",
                    "label": "Use Loyalty Points",
                    "description": f"Apply points to reduce total"
                },
                {
                    "option": "remove_items",
                    "label": "Adjust Cart",
                    "description": "Remove some items to reduce total"
                },
                {
                    "option": "split_payment",
                    "label": "Split Payment",
                    "description": "Use multiple payment methods"
                }
            ]
        
        elif error_type == "card_declined":
            recovery_message = "Your payment was declined by your card issuer."
            recovery_options = [
                {
                    "option": "different_card",
                    "label": "Try Different Card",
                    "description": "Use another payment method"
                },
                {
                    "option": "alternative_payment",
                    "label": "Alternative Payment",
                    "description": "PayPal, Apple Pay, Google Pay"
                },
                {
                    "option": "save_cart",
                    "label": "Save Cart",
                    "description": "Complete purchase later"
                }
            ]
        
        else:
            recovery_message = "We encountered an issue processing your payment."
            recovery_options = [
                {
                    "option": "retry",
                    "label": "Try Again",
                    "description": "Retry the payment"
                },
                {
                    "option": "contact_support",
                    "label": "Contact Support",
                    "description": "Get help from our team"
                }
            ]
        
        return {
            "recovery_type": "payment_failure",
            "error_type": error_type,
            "message": recovery_message,
            "recovery_options": recovery_options,
            "cart_preserved": True,
            "cart_total": cart_total
        }
    
    def handle_connection_error(self) -> Dict[str, Any]:
        """Handle connection/network errors"""
        return {
            "recovery_type": "connection_error",
            "message": "Having trouble connecting. Your cart and conversation are saved.",
            "actions": [
                {"type": "retry", "label": "Retry Connection"},
                {"type": "offline_mode", "label": "Continue Offline"}
            ],
            "data_preserved": True
        }