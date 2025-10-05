# backend/services/channel_adapters.py
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import json

class BaseChannelAdapter(ABC):
    """
    Base class for channel-specific adapters
    Converts AI responses to channel-appropriate formats
    """
    
    def __init__(self, channel_name: str):
        self.channel_name = channel_name
    
    @abstractmethod
    def format_message(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format AI response for specific channel
        
        Args:
            ai_response: Raw AI response from orchestrator
            
        Returns:
            Channel-formatted response
        """
        pass
    
    @abstractmethod
    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> Any:
        """Format product recommendations for channel"""
        pass
    
    @abstractmethod
    def format_cart(self, cart_data: Dict[str, Any]) -> Any:
        """Format shopping cart for channel"""
        pass
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to max length with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."


class WebChatAdapter(BaseChannelAdapter):
    """
    Web chat adapter - supports rich UI elements
    """
    
    def __init__(self):
        super().__init__("web")
    
    def format_message(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for web chat with rich UI support
        """
        formatted = {
            "type": "chat_message",
            "channel": self.channel_name,
            "message": ai_response.get("message", ""),
            "timestamp": ai_response.get("timestamp"),
            "intent": ai_response.get("intent")
        }
        
        # Add quick reply suggestions
        if ai_response.get("suggestions"):
            formatted["quick_replies"] = [
                {
                    "type": "button",
                    "text": suggestion,
                    "action": "send_message",
                    "payload": suggestion
                }
                for suggestion in ai_response.get("suggestions", [])[:4]
            ]
        
        # Add product cards if recommendations exist
        if ai_response.get("recommendations"):
            formatted["product_cards"] = self.format_recommendations(
                ai_response["recommendations"]
            )
        
        # Add cart widget if cart data exists
        if ai_response.get("cart"):
            formatted["cart_widget"] = self.format_cart(ai_response["cart"])
        
        # Add loyalty badge
        if ai_response.get("loyalty_info"):
            formatted["loyalty_badge"] = {
                "tier": ai_response["loyalty_info"].get("tier"),
                "points": ai_response["loyalty_info"].get("points")
            }
        
        # Add action buttons
        if ai_response.get("actions"):
            formatted["action_buttons"] = [
                {
                    "type": action.get("type"),
                    "label": action.get("label"),
                    "description": action.get("description")
                }
                for action in ai_response.get("actions", [])
            ]
        
        return formatted
    
    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format recommendations as product cards for web"""
        return [
            {
                "product_id": rec.get("product_id"),
                "image": rec.get("image", "/placeholder.jpg"),
                "name": rec.get("name"),
                "brand": rec.get("brand"),
                "price": rec.get("price"),
                "original_price": rec.get("original_price"),
                "rating": rec.get("rating"),
                "reason": self._truncate_text(rec.get("reason", ""), 100),
                "in_stock": rec.get("in_stock", True),
                "actions": [
                    {"type": "view_details", "label": "View Details"},
                    {"type": "add_to_cart", "label": "Add to Cart"}
                ]
            }
            for rec in recommendations[:6]  # Limit to 6 for web
        ]
    
    def format_cart(self, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format cart as widget for web"""
        return {
            "items": cart_data.get("cart", []),
            "count": cart_data.get("cart_count", 0),
            "subtotal": cart_data.get("subtotal", 0),
            "actions": [
                {"type": "view_cart", "label": "View Cart"},
                {"type": "checkout", "label": "Checkout"}
            ]
        }


class WhatsAppAdapter(BaseChannelAdapter):
    """
    WhatsApp adapter - text-only with emoji support
    """
    
    def __init__(self):
        super().__init__("whatsapp")
    
    def format_message(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for WhatsApp - text-focused with emojis
        """
        # Build main message text
        message_parts = [ai_response.get("message", "")]
        
        # Add recommendations as text list
        if ai_response.get("recommendations"):
            message_parts.append("\n\n✨ *Recommended for you:*")
            for i, rec in enumerate(ai_response["recommendations"][:3], 1):
                rec_text = f"\n{i}. *{rec['name']}* by {rec.get('brand', 'Unknown')}"
                rec_text += f"\n   💰 ${rec['price']}"
                rec_text += f"\n   ⭐ {rec.get('rating', 'N/A')}/5"
                rec_text += f"\n   💡 {self._truncate_text(rec.get('reason', ''), 80)}"
                message_parts.append(rec_text)
        
        # Add loyalty info
        if ai_response.get("loyalty_info"):
            loyalty = ai_response["loyalty_info"]
            message_parts.append(
                f"\n\n🏆 *{loyalty.get('tier')}* Member | "
                f"✨ {loyalty.get('points')} points"
            )
        
        # Add cart summary - FIX THIS PART
        cart_data = ai_response.get("cart")
        if cart_data:
            # If cart_data is a dict with cart items
            if isinstance(cart_data, dict):
                cart_items = cart_data.get("cart", [])
                cart_count = cart_data.get("cart_count", 0)
                subtotal = cart_data.get("subtotal", 0)
                
                if cart_count > 0:
                    message_parts.append(f"\n\n🛒 *Your Cart ({cart_count} items):*\n")
                    for item in cart_items:
                        message_parts.append(
                            f"• {item.get('name')} x{item.get('quantity', 1)}\n"
                            f"  ${item.get('price', 0)} each = ${item.get('subtotal', 0)}"
                        )
                    message_parts.append(f"\n*Total: ${subtotal}*")
        
        # Combine all parts
        full_message = "".join(message_parts)
        
        # Create quick reply buttons (max 3 for WhatsApp)
        quick_replies = []
        if ai_response.get("suggestions"):
            quick_replies = [
                {
                    "type": "reply",
                    "text": self._truncate_text(suggestion, 20)
                }
                for suggestion in ai_response["suggestions"][:3]
            ]
        
        return {
            "type": "whatsapp_message",
            "channel": self.channel_name,
            "text": full_message,
            "quick_replies": quick_replies,
            "timestamp": ai_response.get("timestamp")
        }
    
    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations as text for WhatsApp"""
        text = "✨ *Recommended Products:*\n\n"
        
        for i, rec in enumerate(recommendations[:3], 1):
            text += f"{i}. *{rec['name']}*\n"
            text += f"   ${rec['price']} | {rec.get('brand', '')}\n"
            text += f"   {self._truncate_text(rec.get('reason', ''), 80)}\n\n"
        
        return text
    
    def format_cart(self, cart_data: Dict[str, Any]) -> str:
        """Format cart as text for WhatsApp"""
        if not cart_data or cart_data.get("cart_count", 0) == 0:
            return "🛒 Your cart is empty"
        
        text = f"🛒 *Your Cart* ({cart_data['cart_count']} items)\n\n"
        
        for item in cart_data.get("cart", []):
            text += f"• {item['name']} x{item['quantity']}\n"
            text += f"  ${item['price']} each = ${item['subtotal']}\n\n"
        
        text += f"*Subtotal:* ${cart_data.get('subtotal', 0)}"
        
        return text   
    
    def __init__(self):
        super().__init__("whatsapp")
    
    def format_message(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for WhatsApp - text-focused with emojis
        """
        # Build main message text
        message_parts = [ai_response.get("message", "")]
        
        # Add recommendations as text list
        if ai_response.get("recommendations"):
            message_parts.append("\n\n✨ *Recommended for you:*")
            for i, rec in enumerate(ai_response["recommendations"][:3], 1):
                rec_text = f"\n{i}. *{rec['name']}* by {rec.get('brand', 'Unknown')}"
                rec_text += f"\n   💰 ${rec['price']}"
                rec_text += f"\n   ⭐ {rec.get('rating', 'N/A')}/5"
                rec_text += f"\n   💡 {self._truncate_text(rec.get('reason', ''), 80)}"
                message_parts.append(rec_text)
        
        # Add loyalty info
        if ai_response.get("loyalty_info"):
            loyalty = ai_response["loyalty_info"]
            message_parts.append(
                f"\n\n🏆 *{loyalty.get('tier')}* Member | "
                f"✨ {loyalty.get('points')} points"
            )
        
        # Add cart summary if exists
        if ai_response.get("cart"):
            cart = ai_response["cart"]
            if cart.get("cart_count", 0) > 0:
                message_parts.append(
                    f"\n\n🛒 *Cart:* {cart['cart_count']} items | "
                    f"Total: ${cart.get('subtotal', 0)}"
                )
        
        # Combine all parts
        full_message = "".join(message_parts)
        
        # Create quick reply buttons (max 3 for WhatsApp)
        quick_replies = []
        if ai_response.get("suggestions"):
            quick_replies = [
                {
                    "type": "reply",
                    "text": self._truncate_text(suggestion, 20)
                }
                for suggestion in ai_response["suggestions"][:3]
            ]
        
        return {
            "type": "whatsapp_message",
            "channel": self.channel_name,
            "text": full_message,
            "quick_replies": quick_replies,
            "timestamp": ai_response.get("timestamp")
        }
    
    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations as text for WhatsApp"""
        text = "✨ *Recommended Products:*\n\n"
        
        for i, rec in enumerate(recommendations[:3], 1):
            text += f"{i}. *{rec['name']}*\n"
            text += f"   ${rec['price']} | {rec.get('brand', '')}\n"
            text += f"   {self._truncate_text(rec.get('reason', ''), 80)}\n\n"
        
        return text
    
    def format_cart(self, cart_data: Dict[str, Any]) -> str:
        """Format cart as text for WhatsApp"""
        if cart_data.get("cart_count", 0) == 0:
            return "🛒 Your cart is empty"
        
        text = f"🛒 *Your Cart* ({cart_data['cart_count']} items)\n\n"
        
        for item in cart_data.get("cart", []):
            text += f"• {item['name']} x{item['quantity']}\n"
            text += f"  ${item['price']} each = ${item['subtotal']}\n\n"
        
        text += f"*Subtotal:* ${cart_data.get('subtotal', 0)}"
        
        return text


class InStoreAdapter(BaseChannelAdapter):
    """
    In-store kiosk adapter - voice-friendly, staff integration
    """
    
    def __init__(self):
        super().__init__("instore")
    
    def format_message(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for in-store kiosk - large text, simple UI
        """
        formatted = {
            "type": "kiosk_message",
            "channel": self.channel_name,
            "display_text": ai_response.get("message", ""),
            "voice_text": self._simplify_for_voice(ai_response.get("message", "")),
            "timestamp": ai_response.get("timestamp")
        }
        
        # Large product tiles for kiosk
        if ai_response.get("recommendations"):
            formatted["product_tiles"] = [
                {
                    "product_id": rec.get("product_id"),
                    "image": rec.get("image"),
                    "name": rec.get("name"),
                    "price": rec.get("price"),
                    "in_stock_here": rec.get("in_stock", True),
                    "aisle": self._generate_aisle_location(rec.get("product_id"))
                }
                for rec in ai_response["recommendations"][:4]  # 4 large tiles
            ]
        
        # Staff assistance button
        formatted["staff_assistance"] = {
            "available": True,
            "message": "Need help? A store associate can assist you",
            "action": "call_associate"
        }
        
        # QR code for mobile continuation
        formatted["qr_code"] = {
            "available": True,
            "message": "Scan to continue shopping on your phone",
            "session_id": ai_response.get("session_id")
        }
        
        return formatted
    
    def _simplify_for_voice(self, text: str) -> str:
        """Simplify text for voice output"""
        # Remove markdown, emojis, etc.
        voice_text = text.replace("**", "").replace("*", "")
        voice_text = voice_text.replace("✨", "").replace("💰", "")
        return voice_text
    
    def _generate_aisle_location(self, product_id: int) -> str:
        """Generate mock aisle location"""
        aisle_map = {
            1: "Aisle 3, Section B",
            2: "Aisle 5, Section A",
            3: "Aisle 2, Section C"
        }
        return aisle_map.get(product_id, "Ask Associate")
    
    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format as large product tiles"""
        return [
            {
                "product_id": rec.get("product_id"),
                "name": rec.get("name"),
                "price": rec.get("price"),
                "image": rec.get("image"),
                "location": self._generate_aisle_location(rec.get("product_id")),
                "available_now": rec.get("in_stock", True)
            }
            for rec in recommendations[:4]
        ]
    
    def format_cart(self, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format cart for kiosk display"""
        return {
            "items": cart_data.get("cart", []),
            "count": cart_data.get("cart_count", 0),
            "subtotal": cart_data.get("subtotal", 0),
            "checkout_options": [
                {"type": "self_checkout", "label": "Self Checkout"},
                {"type": "assisted_checkout", "label": "Checkout with Associate"}
            ]
        }


class MobileAdapter(BaseChannelAdapter):
    """
    Mobile app adapter - touch-optimized, notifications
    """
    
    def __init__(self):
        super().__init__("mobile")
    
    def format_message(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for mobile app - compact, swipeable
        """
        formatted = {
            "type": "mobile_message",
            "channel": self.channel_name,
            "message": ai_response.get("message", ""),
            "timestamp": ai_response.get("timestamp")
        }
        
        # Horizontal scrollable product cards
        if ai_response.get("recommendations"):
            formatted["horizontal_products"] = self.format_recommendations(
                ai_response["recommendations"]
            )
        
        # Bottom sheet for cart
        if ai_response.get("cart"):
            formatted["cart_sheet"] = self.format_cart(ai_response["cart"])
        
        # Floating action buttons
        if ai_response.get("actions"):
            formatted["fab_actions"] = [
                {
                    "type": action.get("type"),
                    "icon": self._action_to_icon(action.get("type")),
                    "label": action.get("label")
                }
                for action in ai_response.get("actions", [])[:3]
            ]
        
        return formatted
    
    def _action_to_icon(self, action_type: str) -> str:
        """Map action type to mobile icon"""
        icon_map = {
            "view_product": "eye",
            "add_to_cart": "cart",
            "checkout": "credit-card",
            "view_cart": "shopping-bag"
        }
        return icon_map.get(action_type, "info")
    
    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format as compact cards for mobile"""
        return [
            {
                "product_id": rec.get("product_id"),
                "image": rec.get("image"),
                "name": self._truncate_text(rec.get("name", ""), 40),
                "price": rec.get("price"),
                "rating": rec.get("rating"),
                "quick_add": True
            }
            for rec in recommendations
        ]
    
    def format_cart(self, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format cart as bottom sheet"""
        return {
            "items": cart_data.get("cart", []),
            "count": cart_data.get("cart_count", 0),
            "subtotal": cart_data.get("subtotal", 0),
            "swipe_to_checkout": True
        }


# Factory function to get appropriate adapter
def get_channel_adapter(channel: str) -> BaseChannelAdapter:
    """
    Get the appropriate adapter for a channel
    
    Args:
        channel: Channel name (web, whatsapp, instore, mobile)
        
    Returns:
        Channel adapter instance
    """
    adapters = {
        "web": WebChatAdapter,
        "whatsapp": WhatsAppAdapter,
        "instore": InStoreAdapter,
        "mobile": MobileAdapter
    }
    
    adapter_class = adapters.get(channel.lower(), WebChatAdapter)
    return adapter_class()