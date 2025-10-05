# backend/agents/orchestrator.py
from agents.base_agent import BaseAgent
from agents.sales_agent import SalesAgent
from agents.recommendation_agent import RecommendationAgent
from agents.inventory_agent import InventoryAgent
from agents.payment_agent import PaymentAgent
from agents.loyalty_agent import LoyaltyAgent
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class Orchestrator(BaseAgent):
    """
    Orchestrator - coordinates all worker agents to deliver complete customer journey
    This is the brain that makes everything work together
    """
    
    def __init__(self):
        super().__init__("Orchestrator")
        
        # Initialize all worker agents
        self.sales_agent = SalesAgent()
        self.recommendation_agent = RecommendationAgent()
        self.inventory_agent = InventoryAgent()
        self.payment_agent = PaymentAgent()
        self.loyalty_agent = LoyaltyAgent()
        
        self._log("Orchestrator initialized with all worker agents")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration method - routes to appropriate workflow
        
        Args:
            context: Complete conversation context
            
        Returns:
            Coordinated response from multiple agents
        """
        self._log("Orchestrating customer interaction...")
        
        try:
            # Get customer message and context
            message = context.get("message", "")
            customer_id = context.get("customer_id")
            session_id = context.get("session_id")
            conversation_history = context.get("conversation_history", [])
            
            # Step 1: Sales agent analyzes intent
            sales_response = await self.sales_agent.execute({
                "message": message,
                "customer_info": context.get("customer_info", {}),
                "conversation_history": conversation_history
            })
            
            intent = sales_response.get("intent")
            required_agents = sales_response.get("requires_worker_agents", [])
            
            self._log(f"Intent detected: {intent}, Required agents: {required_agents}")
            
            # Step 2: Call required worker agents based on intent
            worker_results = {}
            
            if intent == "browsing":
                worker_results = await self._handle_browsing(context, required_agents)
            
            elif intent == "purchase_intent":
                worker_results = await self._handle_purchase(context, required_agents)
            
            elif intent == "needs_help":
                worker_results = await self._handle_help(context, required_agents)
            
            # Step 3: Synthesize final response
            final_response = await self._synthesize_response(
                sales_response=sales_response,
                worker_results=worker_results,
                context=context
            )
            
            return final_response
            
        except Exception as e:
            self._log(f"Orchestration error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "response": "I'm having trouble processing that right now. Let me help you differently.",
                "error": str(e)
            }
    
    async def _handle_browsing(
        self, 
        context: Dict[str, Any], 
        required_agents: List[str]
    ) -> Dict[str, Any]:
        """
        Handle browsing intent - coordinate recommendations and inventory
        
        Args:
            context: Customer context
            required_agents: Which agents to call
            
        Returns:
            Combined results from worker agents
        """
        results = {}
        
        # Get recommendations
        if "recommendation" in required_agents:
            self._log("Calling recommendation agent...")
            
            recommendations = await self.recommendation_agent.execute({
                "customer_info": context.get("customer_info", {}),
                "occasion": self._extract_occasion(context.get("message", "")),
                "budget": context.get("budget"),
                "category": context.get("category")
            })
            
            results["recommendations"] = recommendations
        
        # Check inventory for recommended items
        if "inventory" in required_agents and results.get("recommendations"):
            self._log("Checking inventory for recommendations...")
            
            recommended_products = results["recommendations"].get("recommendations", [])
            if recommended_products:
                product_ids = [p["product_id"] for p in recommended_products[:3]]
                
                inventory = await self.inventory_agent.check_multiple_products(
                    product_ids=product_ids,
                    customer_location=context.get("location", "online")
                )
                
                results["inventory"] = inventory
        
        # Get loyalty benefits if customer is known
        if context.get("customer_id"):
            self._log("Getting loyalty benefits...")
            
            loyalty_info = await self.loyalty_agent.get_customer_loyalty_info(
                context["customer_id"]
            )
            
            results["loyalty"] = loyalty_info
        
        return results
    
    async def _handle_purchase(
        self,
        context: Dict[str, Any],
        required_agents: List[str]
    ) -> Dict[str, Any]:
        """
        Handle purchase intent - coordinate inventory, loyalty, and payment
        
        Args:
            context: Customer context
            required_agents: Which agents to call
            
        Returns:
            Combined results from worker agents
        """
        results = {}
        cart_items = context.get("cart_items", [])
        
        # Check inventory availability
        if "inventory" in required_agents and cart_items:
            self._log("Checking inventory for cart items...")
            
            product_ids = [item["product_id"] for item in cart_items]
            quantities = {str(item["product_id"]): item.get("quantity", 1) for item in cart_items}
            
            inventory = await self.inventory_agent.check_multiple_products(
                product_ids=product_ids,
                quantities=quantities,
                customer_location=context.get("location", "online")
            )
            
            results["inventory"] = inventory
        
        # Calculate loyalty discounts
        if "loyalty" in required_agents and context.get("customer_id"):
            self._log("Calculating loyalty benefits...")
            
            loyalty_info = await self.loyalty_agent.get_customer_loyalty_info(
                context["customer_id"]
            )
            
            results["loyalty"] = loyalty_info
        
        # Process payment if requested
        if "payment" in required_agents and cart_items:
            self._log("Processing payment...")
            
            payment_result = await self.payment_agent.process_checkout(
                cart_items=cart_items,
                customer_id=context.get("customer_id"),
                payment_method=context.get("payment_method", "card"),
                apply_loyalty=context.get("apply_loyalty", True),
                coupon_code=context.get("coupon_code")
            )
            
            results["payment"] = payment_result
        
        return results
    
    async def _handle_help(
        self,
        context: Dict[str, Any],
        required_agents: List[str]
    ) -> Dict[str, Any]:
        """
        Handle help/question intent
        
        Args:
            context: Customer context
            required_agents: Which agents to call
            
        Returns:
            Combined results from worker agents
        """
        results = {}
        
        # Check inventory if asking about specific product
        if "inventory" in required_agents:
            product_ids = context.get("product_ids", [])
            if product_ids:
                self._log("Checking inventory for help request...")
                
                inventory = await self.inventory_agent.check_multiple_products(
                    product_ids=product_ids,
                    customer_location=context.get("location", "online")
                )
                
                results["inventory"] = inventory
        
        return results
    
    async def _synthesize_response(
        self,
        sales_response: Dict[str, Any],
        worker_results: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize final response from all agent results
        """
        # Base response from sales agent
        response = {
            "success": True,
            "message": sales_response.get("response", ""),
            "intent": sales_response.get("intent"),
            "suggestions": sales_response.get("suggestions", []),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add recommendations if available
        if "recommendations" in worker_results:
            rec_data = worker_results["recommendations"]
            if rec_data.get("success"):
                response["recommendations"] = rec_data.get("recommendations", [])[:3]  # Top 3
                response["total_recommendations"] = rec_data.get("total_items", 0)
        
        # Add inventory information
        if "inventory" in worker_results:
            inv_data = worker_results["inventory"]
            if inv_data.get("success"):
                response["inventory_status"] = inv_data.get("data", {}).get("availability", {})
        
        # Add loyalty information
        if "loyalty" in worker_results:
            loyalty_data = worker_results["loyalty"]
            if loyalty_data.get("success"):
                response["loyalty_info"] = {
                    "tier": loyalty_data.get("loyalty_tier"),
                    "points": loyalty_data.get("loyalty_points"),
                    "benefits": loyalty_data.get("benefits")
                }
        
        # Add payment result if available
        if "payment" in worker_results:
            payment_data = worker_results["payment"]
            response["payment_result"] = payment_data

        if context.get("session_id"):
            from services.context_manager import ContextManager
            context_manager = ContextManager()
            cart_data = context_manager.get_cart(context["session_id"])
            if cart_data.get("success"):
                response["cart"] = cart_data
        
        # Add actions based on intent
        response["actions"] = self._determine_next_actions(
            intent=sales_response.get("intent"),
            worker_results=worker_results
        )
        
        return response
    
    def _extract_occasion(self, message: str) -> str:
        """Extract occasion from customer message"""
        message_lower = message.lower()
        
        occasions = {
            "wedding": ["wedding", "marriage", "bridal"],
            "birthday": ["birthday", "bday"],
            "work": ["work", "office", "professional", "job"],
            "party": ["party", "celebration", "event"],
            "date": ["date", "romantic", "dinner"],
            "casual": ["casual", "everyday", "weekend"]
        }
        
        for occasion, keywords in occasions.items():
            if any(keyword in message_lower for keyword in keywords):
                return occasion
        
        return ""
    
    def _determine_next_actions(
        self,
        intent: str,
        worker_results: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Determine what actions customer should do next"""
        actions = []
        
        if intent == "browsing":
            if worker_results.get("recommendations"):
                actions.append({
                    "type": "view_product",
                    "label": "View Details",
                    "description": "See more about these items"
                })
                actions.append({
                    "type": "add_to_cart",
                    "label": "Add to Cart",
                    "description": "Add items you like"
                })
        
        elif intent == "purchase_intent":
            if worker_results.get("inventory"):
                actions.append({
                    "type": "proceed_checkout",
                    "label": "Proceed to Checkout",
                    "description": "Complete your purchase"
                })
            
            if worker_results.get("payment"):
                payment_data = worker_results["payment"]
                if payment_data.get("success"):
                    actions.append({
                        "type": "view_order",
                        "label": "View Order",
                        "description": "See your order details"
                    })
        
        return actions
    
    async def handle_conversation(
        self,
        message: str,
        customer_id: int = None,
        session_id: str = None,
        cart_items: List[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method for handling complete conversation
        
        Args:
            message: Customer's message
            customer_id: Customer ID
            session_id: Session ID
            cart_items: Items in cart
            **kwargs: Additional context
            
        Returns:
            Complete orchestrated response
        """
        # Build complete context
        context = {
            "message": message,
            "customer_id": customer_id,
            "session_id": session_id,
            "cart_items": cart_items or [],
            **kwargs
        }
        
        # Get customer info if available
        if customer_id:
            from database import SessionLocal
            from models.models import Customer
            
            db = SessionLocal()
            try:
                customer = db.query(Customer).filter(Customer.id == customer_id).first()
                if customer:
                    context["customer_info"] = {
                        "name": customer.name,
                        "loyalty_tier": customer.loyalty_tier,
                        "preferences": customer.preferences or {},
                        "loyalty_points": customer.loyalty_points
                    }
            finally:
                db.close()
        
        return await self.execute(context)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration method - routes to appropriate workflow
        """
        self._log("Orchestrating customer interaction...")
        
        try:
            # Get customer message and context
            message = context.get("message", "")
            customer_id = context.get("customer_id")
            session_id = context.get("session_id")
            conversation_history = context.get("conversation_history", [])
            
            # Step 1: Sales agent analyzes intent
            sales_response = await self.sales_agent.execute({
                "message": message,
                "customer_info": context.get("customer_info", {}),
                "conversation_history": conversation_history
            })
            
            intent = sales_response.get("intent")
            required_agents = sales_response.get("requires_worker_agents", [])
            
            self._log(f"Intent detected: {intent}, Required agents: {required_agents}")
            
            # Step 2: Call required worker agents based on intent
            worker_results = {}
            
            if intent == "browsing":
                worker_results = await self._handle_browsing(context, required_agents)
            
            elif intent == "purchase_intent":
                worker_results = await self._handle_purchase(context, required_agents)
            
            elif intent == "needs_help":
                worker_results = await self._handle_help(context, required_agents)
            
            elif intent == "view_cart":
                # Handle cart viewing - ADD THIS
                if session_id:
                    from services.context_manager import ContextManager
                    context_manager = ContextManager()
                    cart_data = context_manager.get_cart(session_id)
                    
                    if cart_data.get("success") and cart_data.get("cart_count", 0) > 0:
                        # Update sales response to show cart
                        items_text = f"You have {cart_data['cart_count']} items in your cart:\n"
                        for item in cart_data.get("cart", []):
                            items_text += f"• {item['name']} x{item['quantity']} - ${item['subtotal']}\n"
                        items_text += f"\nSubtotal: ${cart_data.get('subtotal', 0)}"
                        
                        sales_response["response"] = items_text
                    else:
                        sales_response["response"] = "Your cart is empty. Would you like me to recommend some items?"
            
            # Step 3: Synthesize final response
            final_response = await self._synthesize_response(
                sales_response=sales_response,
                worker_results=worker_results,
                context=context
            )
            
            return final_response
            
        except Exception as e:
            self._log(f"Orchestration error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "response": "I'm having trouble processing that right now. Let me help you differently.",
                "error": str(e)
            }
    

    # Add to the Orchestrator class in backend/agents/orchestrator.py

    async def handle_channel_conversation(
        self,
        message: str,
        channel: str,
        customer_id: int = None,
        session_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Handle conversation with channel-specific formatting
        
        Args:
            message: Customer's message
            channel: Channel name (web, whatsapp, instore, mobile)
            customer_id: Customer ID
            session_id: Session ID
            **kwargs: Additional context
            
        Returns:
            Channel-formatted response
        """
        # Get base AI response
        ai_response = await self.handle_conversation(
            message=message,
            customer_id=customer_id,
            session_id=session_id,
            **kwargs
        )
        
        # Get channel adapter
        from services.channel_adapters import get_channel_adapter
        adapter = get_channel_adapter(channel)
        
        # Format response for channel
        formatted_response = adapter.format_message(ai_response)
        
        return formatted_response