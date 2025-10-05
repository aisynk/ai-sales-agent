# backend/services/context_manager.py
from typing import Dict, Any, List, Optional
from database import SessionLocal
from models.models import ChatSession, Customer
from datetime import datetime
import uuid
import json

class ContextManager:
    """
    Manages conversation context and shopping cart across channels
    Enables seamless omnichannel experience
    """
    
    def __init__(self):
        pass
    
    def create_session(
        self,
        customer_id: int = None,
        channel: str = "web"
    ) -> str:
        """
        Create new chat session
        
        Args:
            customer_id: Customer ID (optional for anonymous)
            channel: Channel (web, whatsapp, instore, mobile)
            
        Returns:
            Session ID
        """
        db = SessionLocal()
        
        try:
            session_id = f"session-{uuid.uuid4().hex[:12]}"
            
            # Create session record
            session = ChatSession(
                session_id=session_id,
                customer_id=customer_id,
                channel=channel,
                context={},
                messages=[],
                cart=[],
                is_active=True
            )
            
            db.add(session)
            db.commit()
            
            return session_id
            
        finally:
            db.close()
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None
        """
        db = SessionLocal()
        
        try:
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
            if not session:
                return None
            
            return {
                "session_id": session.session_id,
                "customer_id": session.customer_id,
                "channel": session.channel,
                "context": session.context or {},
                "messages": session.messages or [],
                "cart": session.cart or [],
                "is_active": session.is_active,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None
            }
            
        finally:
            db.close()
    
    def update_session(
        self,
        session_id: str,
        context: Dict[str, Any] = None,
        messages: List[Dict[str, Any]] = None,
        cart: List[Dict[str, Any]] = None,
        channel: str = None
    ) -> bool:
        """
        Update session data
        
        Args:
            session_id: Session ID
            context: Updated context
            messages: Updated messages
            cart: Updated cart
            channel: Updated channel (for channel switching)
            
        Returns:
            Success status
        """
        db = SessionLocal()
        
        try:
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
            if not session:
                return False
            
            # Update fields if provided
            if context is not None:
                session.context = context
            
            if messages is not None:
                session.messages = messages
            
            if cart is not None:
                session.cart = cart
            
            if channel is not None:
                session.channel = channel
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error updating session: {e}")
            return False
        finally:
            db.close()
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> bool:
        """
        Add message to conversation history
        
        Args:
            session_id: Session ID
            role: "user" or "assistant"
            content: Message content
            
        Returns:
            Success status
        """
        session = self.get_session(session_id)
        
        if not session:
            return False
        
        messages = session.get("messages", [])
        messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        return self.update_session(session_id, messages=messages)
    
    def add_to_cart(
        self,
        session_id: str,
        product_id: int,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Add item to shopping cart
        
        Args:
            session_id: Session ID
            product_id: Product ID
            quantity: Quantity to add
            
        Returns:
            Updated cart
        """
        session = self.get_session(session_id)
        
        if not session:
            return {"success": False, "message": "Session not found"}
        
        cart = session.get("cart", [])
        
        # Check if item already in cart
        existing_item = next(
            (item for item in cart if item["product_id"] == product_id),
            None
        )
        
        if existing_item:
            # Update quantity
            existing_item["quantity"] += quantity
        else:
            # Add new item
            cart.append({
                "product_id": product_id,
                "quantity": quantity,
                "added_at": datetime.now().isoformat()
            })
        
        # Update session
        success = self.update_session(session_id, cart=cart)
        
        return {
            "success": success,
            "cart": cart,
            "cart_count": len(cart),
            "total_items": sum(item["quantity"] for item in cart)
        }
    
    def remove_from_cart(
        self,
        session_id: str,
        product_id: int
    ) -> Dict[str, Any]:
        """
        Remove item from cart
        
        Args:
            session_id: Session ID
            product_id: Product ID to remove
            
        Returns:
            Updated cart
        """
        session = self.get_session(session_id)
        
        if not session:
            return {"success": False, "message": "Session not found"}
        
        cart = session.get("cart", [])
        
        # Remove item
        cart = [item for item in cart if item["product_id"] != product_id]
        
        # Update session
        success = self.update_session(session_id, cart=cart)
        
        return {
            "success": success,
            "cart": cart,
            "cart_count": len(cart),
            "total_items": sum(item["quantity"] for item in cart)
        }
    
    def update_cart_quantity(
        self,
        session_id: str,
        product_id: int,
        quantity: int
    ) -> Dict[str, Any]:
        """
        Update quantity of item in cart
        
        Args:
            session_id: Session ID
            product_id: Product ID
            quantity: New quantity
            
        Returns:
            Updated cart
        """
        session = self.get_session(session_id)
        
        if not session:
            return {"success": False, "message": "Session not found"}
        
        cart = session.get("cart", [])
        
        # Find and update item
        for item in cart:
            if item["product_id"] == product_id:
                if quantity <= 0:
                    # Remove if quantity is 0
                    cart.remove(item)
                else:
                    item["quantity"] = quantity
                break
        
        # Update session
        success = self.update_session(session_id, cart=cart)
        
        return {
            "success": success,
            "cart": cart,
            "cart_count": len(cart),
            "total_items": sum(item["quantity"] for item in cart)
        }
    
    def get_cart(self, session_id: str) -> Dict[str, Any]:
        """
        Get current cart contents
        
        Args:
            session_id: Session ID
            
        Returns:
            Cart data with product details
        """
        session = self.get_session(session_id)
        
        if not session:
            return {"success": False, "message": "Session not found"}
        
        cart = session.get("cart", [])
        
        # Get product details for cart items
        if cart:
            from models.models import Product
            db = SessionLocal()
            
            try:
                cart_with_details = []
                
                for item in cart:
                    product = db.query(Product).filter(
                        Product.id == item["product_id"]
                    ).first()
                    
                    if product:
                        cart_with_details.append({
                            "product_id": product.id,
                            "name": product.name,
                            "price": float(product.price),
                            "brand": product.brand,
                            "image": product.images[0] if product.images else None,
                            "quantity": item["quantity"],
                            "subtotal": float(product.price) * item["quantity"]
                        })
                
                total = sum(item["subtotal"] for item in cart_with_details)
                
                return {
                    "success": True,
                    "cart": cart_with_details,
                    "cart_count": len(cart_with_details),
                    "total_items": sum(item["quantity"] for item in cart_with_details),
                    "subtotal": round(total, 2)
                }
                
            finally:
                db.close()
        
        return {
            "success": True,
            "cart": [],
            "cart_count": 0,
            "total_items": 0,
            "subtotal": 0.0
        }
    
    def switch_channel(
        self,
        session_id: str,
        new_channel: str
    ) -> Dict[str, Any]:
        """
        Switch channel while maintaining context
        
        Args:
            session_id: Session ID
            new_channel: New channel name
            
        Returns:
            Confirmation with context
        """
        session = self.get_session(session_id)
        
        if not session:
            return {"success": False, "message": "Session not found"}
        
        old_channel = session.get("channel")
        
        # Update channel
        success = self.update_session(session_id, channel=new_channel)
        
        if success:
            return {
                "success": True,
                "message": f"Switched from {old_channel} to {new_channel}",
                "session_id": session_id,
                "new_channel": new_channel,
                "context_preserved": True,
                "cart_items": len(session.get("cart", [])),
                "conversation_messages": len(session.get("messages", []))
            }
        
        return {"success": False, "message": "Channel switch failed"}
    
    def clear_cart(self, session_id: str) -> bool:
        """Clear all items from cart"""
        return self.update_session(session_id, cart=[])
    
    def end_session(self, session_id: str) -> bool:
        """Mark session as inactive"""
        db = SessionLocal()
        
        try:
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
            if session:
                session.is_active = False
                db.commit()
                return True
            
            return False
            
        finally:
            db.close()