# backend/models/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Text
from sqlalchemy.sql import func
from database import Base

class Customer(Base):
    """
    Customer table - stores customer information and preferences
    """
    __tablename__ = "customers"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    
    # Flexible JSON fields for dynamic data
    preferences = Column(JSON, default=dict)
    # Example: {"styles": ["casual", "elegant"], "colors": ["blue", "black"], "sizes": {"dress": "M", "shoes": 8}}
    
    purchase_history = Column(JSON, default=list)
    # Example: [{"order_id": "123", "date": "2024-01-01", "items": [...], "total": 299.99}]
    
    # Loyalty program
    loyalty_tier = Column(String(20), default="Bronze")  # Bronze, Silver, Gold, Platinum
    loyalty_points = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Product(Base):
    """
    Product table - stores product catalog
    """
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic product info
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(100), index=True)  # "Dresses", "Shoes", "Accessories"
    brand = Column(String(100))
    
    # Pricing
    price = Column(Float, nullable=False)
    original_price = Column(Float)  # For showing discounts
    
    # Product details as JSON
    attributes = Column(JSON, default=dict)
    # Example: {"color": "emerald green", "sizes": ["XS", "S", "M", "L"], "material": "silk", "occasion": ["formal", "party"]}
    
    # Inventory across locations
    inventory = Column(JSON, default=list)
    # Example: [{"location": "online", "quantity": 50}, {"location": "store_downtown", "quantity": 5}]
    
    # Description and images
    description = Column(Text)
    images = Column(JSON, default=list)  # ["url1.jpg", "url2.jpg"]
    
    # Analytics
    views = Column(Integer, default=0)
    purchases = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ChatSession(Base):
    """
    ChatSession table - stores conversation history and context
    """
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Session identification
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, index=True)  # Link to customer (nullable for anonymous)
    
    # Channel tracking
    channel = Column(String(50), default="web")  # web, whatsapp, instore, mobile
    
    # Conversation context
    context = Column(JSON, default=dict)
    # Example: {"intent": "shopping_for_dress", "occasion": "birthday", "budget": 200, "step": "browsing"}
    
    # Complete message history
    messages = Column(JSON, default=list)
    # Example: [{"role": "user", "content": "Hi", "timestamp": "..."}, {"role": "assistant", "content": "Hello!", "timestamp": "..."}]
    
    # Shopping cart
    cart = Column(JSON, default=list)
    # Example: [{"product_id": 1, "quantity": 1, "price": 180}]
    
    # Session status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())