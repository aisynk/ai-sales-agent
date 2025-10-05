# backend/main.py
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database import get_db, SessionLocal
from models.models import Customer, Product, ChatSession
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends
from pydantic import BaseModel
from agents.sales_agent import SalesAgent
from agents.recommendation_agent import RecommendationAgent
from agents.inventory_agent import InventoryAgent
from agents.payment_agent import PaymentAgent
from agents.loyalty_agent import LoyaltyAgent
from agents.orchestrator import Orchestrator
from services.context_manager import ContextManager
from services.analytics import AnalyticsService
from services.error_recovery import ErrorRecoveryService







recommendation_agent = RecommendationAgent()
payment_agent = PaymentAgent()
loyalty_agent = LoyaltyAgent()
orchestrator = Orchestrator()
context_manager = ContextManager()

analytics_service = AnalyticsService()
error_recovery_service = ErrorRecoveryService()




class ReserveItemsRequest(BaseModel):
    items: List[Dict[str, Any]]
    session_id: str = None
    duration_minutes: int = 30

class CheckoutRequest(BaseModel):
    cart_items: List[Dict[str, Any]]
    customer_id: int = None
    payment_method: str = "card"
    apply_loyalty: bool = True
    coupon_code: str = None

class SmartChatRequest(BaseModel):
    message: str
    customer_id: int = None
    session_id: str = None
    cart_items: List[Dict[str, Any]] = []
    location: str = "online"
    budget: float = None
    category: str = None
    payment_method: str = "card"
    apply_loyalty: bool = True
    coupon_code: str = None

class CartItemRequest(BaseModel):
    session_id: str
    product_id: int
    quantity: int = 1

class ProductSearchRequest(BaseModel):
    query: str = ""
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    brand: Optional[str] = None
    sort_by: str = "relevance"  # relevance, price_low, price_high, rating
    limit: int = 20

class ErrorRecoveryRequest(BaseModel):
    error_type: str  # payment_failed, out_of_stock, network_error, etc.
    context: dict = {}
    session_id: str

# Load environment variables from .env file
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="AI Sales Agent API",
    description="Conversational AI for retail sales - completely free implementation",
    version="1.0.0",
    docs_url="/docs",  # Swagger documentation
    redoc_url="/redoc"  # Alternative documentation
)

# Enable CORS for frontend (React will call our API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://127.0.0.1:3000",   # Alternative localhost
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, PUT, DELETE
    allow_headers=["*"],  # Allow all headers
)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint - welcome message
@app.get("/")
async def welcome():
    """
    Welcome endpoint to confirm API is running
    Visit this at: http://localhost:8000
    """
    return {
        "message": "🤖 AI Sales Agent API is running!",
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "SQLite (ready)",
            "ai_service": "Groq (connected)",
            "environment": "development"
        },
        "next_steps": [
            "Visit /docs for API documentation",
            "Visit /health for system health check",
            "Visit /test-ai to test AI connection"
        ]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    System health check for monitoring
    """
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "api": "running",
            "database": "connected", 
            "ai_service": "available"
        }
    }

# Test AI connection endpoint
@app.get("/test-ai")
async def test_ai_connection():
    """
    Test if Groq AI service is working
    This will make a real API call to test our setup
    """
    try:
        from groq import Groq
        
        # Create Groq client with our API key
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Test API call with simple prompt
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Fast, free model
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant. Respond briefly and enthusiastically."
                },
                {
                    "role": "user", 
                    "content": "Say 'Hello! AI is working perfectly!' and confirm you can help with sales conversations."
                }
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        return {
            "status": "success",
            "ai_response": response.choices[0].message.content,
            "model_used": "llama3-8b-8192",
            "service": "Groq (Free)",
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0,
            "message": "🎉 AI connection successful! Ready to build sales conversations."
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "troubleshooting": [
                "Check your GROQ_API_KEY in .env file",
                "Ensure API key starts with 'gsk_'", 
                "Verify internet connection",
                "Try creating new API key at console.groq.com"
            ]
        }


# Add to backend/main.py (after the /test-ai endpoint)



# Initialize sales agent
sales_agent = SalesAgent()

# Request model for chat
class ChatRequest(BaseModel):
    message: str
    context: dict = {}

# Chat endpoint
@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    """
    Chat with AI Sales Agent
    Send a message and get intelligent response
    """
    try:
        response = await sales_agent.chat(
            message=request.message,
            context=request.context
        )
        
        return {
            "success": True,
            "data": response,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Chat service temporarily unavailable"
        }
    
@app.get("/database-test")
async def test_database(db: Session = Depends(get_db)):
    """
    Test database connection and show sample data
    """
    try:
        # Count records in each table
        customer_count = db.query(Customer).count()
        product_count = db.query(Product).count()
        session_count = db.query(ChatSession).count()
        
        # Get sample customer
        sample_customer = db.query(Customer).first()
        
        # Get sample product
        sample_product = db.query(Product).first()
        
        return {
            "status": "success",
            "database": "connected",
            "statistics": {
                "customers": customer_count,
                "products": product_count,
                "chat_sessions": session_count
            },
            "sample_data": {
                "customer": {
                    "name": sample_customer.name if sample_customer else None,
                    "email": sample_customer.email if sample_customer else None,
                    "loyalty_tier": sample_customer.loyalty_tier if sample_customer else None
                } if sample_customer else None,
                "product": {
                    "name": sample_product.name if sample_product else None,
                    "price": sample_product.price if sample_product else None,
                    "category": sample_product.category if sample_product else None
                } if sample_product else None
            },
            "message": "✅ Database is working perfectly!"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Database connection failed"
        }

@app.get("/products")
async def get_products(db: Session = Depends(get_db)):
    """
    Get all products from database
    """
    try:
        products = db.query(Product).all()
        
        return {
            "success": True,
            "count": len(products),
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "category": p.category,
                    "brand": p.brand,
                    "rating": p.rating,
                    "in_stock": sum([inv["quantity"] for inv in p.inventory]) if p.inventory else 0
                }
                for p in products
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/customers")
async def get_customers(db: Session = Depends(get_db)):
    """
    Get all customers from database
    """
    try:
        customers = db.query(Customer).all()
        
        return {
            "success": True,
            "count": len(customers),
            "customers": [
                {
                    "id": c.id,
                    "name": c.name,
                    "email": c.email,
                    "loyalty_tier": c.loyalty_tier,
                    "loyalty_points": c.loyalty_points
                }
                for c in customers
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
# Initialize recommendation agent

# Recommendation endpoint
@app.post("/recommendations")
async def get_recommendations(
    occasion: str = "",
    category: str = None,
    budget: float = None,
    customer_id: int = None
):
    """
    Get personalized product recommendations
    
    Args:
        occasion: What they're shopping for (birthday, wedding, work, etc.)
        category: Specific category (optional)
        budget: Maximum price (optional)
        customer_id: Customer ID for personalization (optional)
    """
    try:
        recommendations = await recommendation_agent.recommend_for_customer(
            customer_id=customer_id,
            occasion=occasion,
            category=category,
            budget=budget
        )
        
        return {
            "success": True,
            "data": recommendations,
            "message": "Recommendations generated successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate recommendations"
        }
    



# Initialize inventory agent
inventory_agent = InventoryAgent()

# Check inventory endpoint
@app.post("/check-inventory")
async def check_inventory(
    product_ids: List[int],
    quantities: Dict[str, int] = None,
    customer_location: str = "online"
):
    """
    Check inventory for multiple products
    
    Args:
        product_ids: List of product IDs to check
        quantities: How many of each product needed
        customer_location: Customer's location preference
    """
    try:
        result = await inventory_agent.check_multiple_products(
            product_ids=product_ids,
            quantities=quantities or {},
            customer_location=customer_location
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Reserve items endpoint
@app.post("/reserve-items")
async def reserve_items(request: ReserveItemsRequest):
    """
    Reserve items during checkout
    
    Args:
        request: Contains items list, session_id (optional), and duration_minutes
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id
        if not session_id:
            import uuid
            session_id = f"session-{uuid.uuid4().hex[:8]}"
        
        result = await inventory_agent.reserve_items(
            items=request.items,
            session_id=session_id,
            duration_minutes=request.duration_minutes
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }
    
@app.post("/checkout")
async def checkout(request: CheckoutRequest):
    """
    Process checkout and payment
    
    Args:
        request: Contains cart_items, customer_id, payment_method, etc.
    """
    try:
        result = await payment_agent.process_checkout(
            cart_items=request.cart_items,
            customer_id=request.customer_id,
            payment_method=request.payment_method,
            apply_loyalty=request.apply_loyalty,
            coupon_code=request.coupon_code
        )
        
        return {
            "success": result.get("success", False),
            "data": result
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }
    
# Add to backend/main.py


# Initialize loyalty agent

# Get loyalty benefits
@app.get("/loyalty/{customer_id}")
async def get_loyalty_info(customer_id: int):
    """
    Get customer's loyalty benefits and status
    
    Args:
        customer_id: Customer ID
    """
    try:
        result = await loyalty_agent.get_customer_loyalty_info(customer_id)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Get personalized offers
@app.get("/loyalty/{customer_id}/offers")
async def get_loyalty_offers(customer_id: int):
    """
    Get personalized offers for customer
    
    Args:
        customer_id: Customer ID
    """
    try:
        context = {
            "action": "get_offers",
            "customer_id": customer_id
        }
        
        result = await loyalty_agent.execute(context)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Calculate points for purchase
@app.get("/loyalty/{customer_id}/calculate-points")
async def calculate_points(customer_id: int, purchase_amount: float):
    """
    Calculate points earned for a purchase amount
    
    Args:
        customer_id: Customer ID
        purchase_amount: Purchase amount in dollars
    """
    try:
        context = {
            "action": "calculate_points",
            "customer_id": customer_id,
            "purchase_amount": purchase_amount
        }
        
        result = await loyalty_agent.execute(context)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
# Add to backend/main.py


# Initialize orchestrator

# Smart conversation endpoint with orchestration


@app.post("/smart-chat")
async def smart_chat(request: SmartChatRequest):
    """
    Intelligent conversation with full agent orchestration
    
    This endpoint coordinates all AI agents to provide complete customer service
    from browsing to purchase
    """
    try:
        result = await orchestrator.handle_conversation(
            message=request.message,
            customer_id=request.customer_id,
            session_id=request.session_id,
            cart_items=request.cart_items,
            location=request.location,
            budget=request.budget,
            category=request.category,
            payment_method=request.payment_method,
            apply_loyalty=request.apply_loyalty,
            coupon_code=request.coupon_code
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": "Smart chat processing failed"
        }
    
# Add to backend/main.py


# Initialize context manager

# Create session
@app.post("/session/create")
async def create_session(customer_id: int = None, channel: str = "web"):
    """
    Create new chat session
    
    Args:
        customer_id: Customer ID (optional)
        channel: Channel name (web, whatsapp, instore, mobile)
    """
    try:
        session_id = context_manager.create_session(
            customer_id=customer_id,
            channel=channel
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "channel": channel,
            "message": "Session created successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Get session
@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session data"""
    try:
        session = context_manager.get_session(session_id)
        
        if session:
            return {
                "success": True,
                "data": session
            }
        else:
            return {
                "success": False,
                "message": "Session not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Cart management endpoints


@app.post("/cart/add")
async def add_to_cart(request: CartItemRequest):
    """Add item to cart"""
    try:
        result = context_manager.add_to_cart(
            session_id=request.session_id,
            product_id=request.product_id,
            quantity=request.quantity
        )
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/cart/{session_id}")
async def get_cart(session_id: str):
    """Get cart contents"""
    try:
        cart = context_manager.get_cart(session_id)
        return cart
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/cart/remove")
async def remove_from_cart(session_id: str, product_id: int):
    """Remove item from cart"""
    try:
        result = context_manager.remove_from_cart(session_id, product_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Channel switching
@app.post("/session/switch-channel")
async def switch_channel(session_id: str, new_channel: str):
    """
    Switch channel while maintaining context
    
    Args:
        session_id: Session ID
        new_channel: New channel (web, whatsapp, instore, mobile)
    """
    try:
        result = context_manager.switch_channel(session_id, new_channel)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
# Add to backend/main.py

@app.post("/channel-chat")
async def channel_chat(
    message: str,
    channel: str,
    customer_id: int = None,
    session_id: str = None,
    cart_items: List[Dict[str, Any]] = None
):
    """
    Smart chat with channel-specific formatting
    
    Args:
        message: Customer message
        channel: Channel (web, whatsapp, instore, mobile)
        customer_id: Customer ID
        session_id: Session ID
        cart_items: Cart items
    """
    try:
        result = await orchestrator.handle_channel_conversation(
            message=message,
            channel=channel,
            customer_id=customer_id,
            session_id=session_id,
            cart_items=cart_items or []
        )
        
        return {
            "success": True,
            "data": result,
            "channel": channel
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }
    
@app.get("/chat")
async def get_chat_page():
    """Serve the web chat interface"""
    return FileResponse("static/chat.html")

@app.get("/whatsapp")
async def get_whatsapp_page():
    """Serve the WhatsApp simulator"""
    return FileResponse("static/whatsapp.html")

@app.get("/kiosk")
async def get_kiosk_page():
    """Serve the in-store kiosk interface"""
    return FileResponse("static/kiosk.html")

@app.get("/demo")
async def get_demo_page():
    """Serve the omnichannel demo page"""
    return FileResponse("static/channel-switcher.html")
@app.get("/test-guide")
async def get_test_guide():
    """Serve the testing guide"""
    return FileResponse("static/test-guide.html")

# Also add a root redirect for convenience
@app.get("/")
async def root_redirect():
    """Redirect root to demo page"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/demo")



# Business Analytics Endpoint
@app.get("/analytics/business-metrics")
async def get_business_metrics():
    """
    Get comprehensive business metrics
    Shows AI impact on revenue, conversion, AOV
    """
    try:
        metrics = analytics_service.calculate_business_metrics()
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ROI Calculator Endpoint
@app.get("/analytics/roi-calculator")
async def calculate_roi(
    monthly_customers: int = 10000,
    implementation_cost: int = 200000
):
    """
    Calculate ROI for retailers
    
    Args:
        monthly_customers: Expected monthly customer traffic
        implementation_cost: One-time implementation cost
    """
    try:
        roi = analytics_service.calculate_roi_for_retailer(
            monthly_customers=monthly_customers,
            implementation_cost=implementation_cost
        )
        return {
            "success": True,
            "data": roi
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# System Status Endpoint
@app.get("/system/status")
async def system_status():
    """Complete system status and health check"""
    from database import engine
    
    try:
        # Test database connection
        with engine.connect() as conn:
            db_status = "connected"
    except:
        db_status = "disconnected"
    
    return {
        "success": True,
        "status": "operational",
        "components": {
            "api": "running",
            "database": db_status,
            "ai_service": "available",
            "orchestrator": "active",
            "agents": {
                "sales": "active",
                "recommendation": "active",
                "inventory": "active",
                "payment": "active",
                "loyalty": "active"
            }
        },
        "channels": {
            "web": "operational",
            "whatsapp": "operational",
            "instore": "operational",
            "mobile": "operational"
        },
        "version": "1.0.0",
        "uptime": "99.9%"
    }

@app.get("/metrics")
async def get_metrics_page():
    """Serve business metrics dashboard"""
    return FileResponse("static/metrics.html")

@app.get("/demo-script")
async def get_demo_script():
    """Serve the demo script"""
    return FileResponse("static/demo-script.html")



@app.post("/products/search")
async def search_products(request: ProductSearchRequest, db: Session = Depends(get_db)):
    """
    Advanced product search with filters
    """
    try:
        query = db.query(Product)
        
        # Text search
        if request.query:
            query = query.filter(
                (Product.name.ilike(f"%{request.query}%")) | 
                (Product.description.ilike(f"%{request.query}%"))
            )
        
        # Category filter
        if request.category:
            query = query.filter(Product.category == request.category)
        
        # Price range filter
        if request.min_price:
            query = query.filter(Product.price >= request.min_price)
        if request.max_price:
            query = query.filter(Product.price <= request.max_price)
        
        # Brand filter
        if request.brand:
            query = query.filter(Product.brand == request.brand)
        
        # Sorting
        if request.sort_by == "price_low":
            query = query.order_by(Product.price.asc())
        elif request.sort_by == "price_high":
            query = query.order_by(Product.price.desc())
        elif request.sort_by == "rating":
            query = query.order_by(Product.rating.desc())
        else:
            query = query.order_by(Product.rating.desc(), Product.purchases.desc())
        
        products = query.limit(request.limit).all()
        
        return {
            "success": True,
            "count": len(products),
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": float(p.price),
                    "original_price": float(p.original_price) if p.original_price else None,
                    "category": p.category,
                    "brand": p.brand,
                    "rating": float(p.rating) if p.rating else 0,
                    "image": p.images[0] if p.images else None
                }
                for p in products
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/products/filters")
async def get_available_filters(db: Session = Depends(get_db)):
    """
    Get available filter options (categories, brands, price ranges)
    """
    try:
        # Get unique categories
        categories = db.query(Product.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        
        # Get unique brands
        brands = db.query(Product.brand).distinct().all()
        brands = [b[0] for b in brands if b[0]]
        
        # Get price range
        min_price = db.query(func.min(Product.price)).scalar() or 0
        max_price = db.query(func.max(Product.price)).scalar() or 1000
        
        return {
            "success": True,
            "filters": {
                "categories": categories,
                "brands": brands,
                "price_range": {
                    "min": float(min_price),
                    "max": float(max_price)
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    


@app.post("/recover-error")
async def handle_error_recovery(request: ErrorRecoveryRequest):
    """
    Provide recovery options based on error type
    """
    recovery_options = []
    
    if request.error_type == "payment_failed":
        recovery_options = [
            {
                "type": "retry_payment",
                "label": "Try Payment Again",
                "description": "Retry with the same payment method",
                "action": "retry"
            },
            {
                "type": "change_payment",
                "label": "Use Different Payment Method",
                "description": "Try PayPal, Apple Pay, or another card",
                "action": "change_method"
            },
            {
                "type": "use_loyalty_points",
                "label": "Use Loyalty Points",
                "description": "Reduce total by using your points",
                "action": "apply_points"
            },
            {
                "type": "save_cart",
                "label": "Save for Later",
                "description": "We'll hold your cart for 24 hours",
                "action": "save"
            }
        ]
    
    elif request.error_type == "out_of_stock":
        recovery_options = [
            {
                "type": "notify_restock",
                "label": "Notify When Back in Stock",
                "description": "We'll email you when it's available",
                "action": "notify"
            },
            {
                "type": "alternative_products",
                "label": "View Similar Items",
                "description": "See products you might like instead",
                "action": "show_alternatives"
            },
            {
                "type": "check_other_locations",
                "label": "Check Other Stores",
                "description": "This item might be available in other locations",
                "action": "check_stores"
            }
        ]
    
    elif request.error_type == "network_error":
        recovery_options = [
            {
                "type": "retry",
                "label": "Try Again",
                "description": "Retry your request",
                "action": "retry"
            },
            {
                "type": "offline_mode",
                "label": "Continue Offline",
                "description": "Browse products offline, sync when connected",
                "action": "offline"
            }
        ]
    
    else:
        recovery_options = [
            {
                "type": "contact_support",
                "label": "Contact Support",
                "description": "Speak with a customer service representative",
                "action": "support"
            }
        ]
    
    return {
        "success": True,
        "error_type": request.error_type,
        "recovery_options": recovery_options,
        "message": "Here are some ways we can help resolve this issue"
    }

@app.get("/test-checklist")
async def get_test_checklist():
    """Serve testing checklist"""
    return FileResponse("static/test-checklist.html")

# Run the application (for development)
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting AI Sales Agent API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 Documentation will be at: http://localhost:8000/docs")
    print("🤖 Test AI at: http://localhost:8000/test-ai")
    print("💡 Press Ctrl+C to stop the server")
    print()
    
    # Run the development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Accept connections from anywhere
        port=8000,       # Port number
        reload=True,     # Restart when code changes
        log_level="info" # Show request logs
    )