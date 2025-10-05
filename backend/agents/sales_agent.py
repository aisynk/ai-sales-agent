# backend/agents/sales_agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any, List

class SalesAgent(BaseAgent):
    """
    Main Sales Agent - orchestrates conversation and coordinates worker agents
    This is the customer-facing AI that manages the whole experience
    """
    
    def __init__(self):
        super().__init__("SalesAgent")
        self._log("Sales Agent initialized")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method - handles customer conversation
        
        Args:
            context: Contains customer message, history, preferences, etc.
            
        Returns:
            AI response with suggestions and next actions
        """
        message = context.get("message", "")
        customer_info = context.get("customer_info", {})
        conversation_history = context.get("conversation_history", [])
        
        # Build context-aware system prompt
        system_prompt = self._build_system_prompt(customer_info)
        
        # Get AI response
        ai_response = await self._call_ai(
            system_prompt=system_prompt,
            user_message=message,
            temperature=0.7,
            max_tokens=300
        )
        
        # Detect customer intent
        intent = self._detect_intent(message)
        
        # Extract suggestions from response
        suggestions = self._extract_suggestions(ai_response, intent)
        
        return {
            "response": ai_response,
            "intent": intent,
            "suggestions": suggestions,
            "next_actions": self._determine_next_actions(intent),
            "requires_worker_agents": self._needs_worker_agents(intent)
        }
    
    def _build_system_prompt(self, customer_info: Dict[str, Any]) -> str:
        """Build context-aware system prompt"""
        
        base_prompt = """You are an expert sales associate for a premium retail brand.

Your goals:
1. Understand customer needs through friendly, open-ended questions
2. Suggest products that match their style, occasion, and budget
3. Create gentle urgency without being pushy
4. Naturally upsell complementary items
5. Guide customers toward purchase decisions
6. Handle objections with empathy and alternatives

Conversation style:
- Warm, enthusiastic, and helpful
- Ask one question at a time
- Listen carefully to preferences
- Suggest specific items with compelling reasons
- Use social proof ("This is our bestseller...")
- Create FOMO when appropriate ("Only a few left...")

Remember: Your goal is to help them find the perfect items and increase their cart value naturally."""

        # Add customer context if available
        if customer_info:
            context_addition = "\n\nCustomer Information:"
            if customer_info.get("name"):
                context_addition += f"\n- Name: {customer_info['name']}"
            if customer_info.get("loyalty_tier"):
                context_addition += f"\n- Loyalty Status: {customer_info['loyalty_tier']} member"
            if customer_info.get("preferences"):
                context_addition += f"\n- Preferences: {customer_info['preferences']}"
            if customer_info.get("budget"):
                context_addition += f"\n- Budget: ${customer_info['budget']}"
            
            base_prompt += context_addition
        
        return base_prompt
    
    def _detect_intent(self, message: str) -> str:
        """Detect what the customer wants to do"""
        message_lower = message.lower()
        
        # Cart viewing intent - ADD THIS
        if any(word in message_lower for word in ["cart", "basket", "bag", "what did i add", "show cart", "view cart", "my items"]):
            return "view_cart"
        
        # Purchase intent
        if any(word in message_lower for word in ["buy", "purchase", "checkout", "order"]):
            return "purchase_intent"
        
        # Browsing intent
        elif any(word in message_lower for word in ["looking", "browse", "show", "find", "search", "need"]):
            return "browsing"
        
        # Question/help intent
        elif any(word in message_lower for word in ["help", "question", "how", "what", "where", "when", "available", "stock"]):
            return "needs_help"
        
        # Greeting
        elif any(word in message_lower for word in ["hi", "hello", "hey", "good morning", "good afternoon"]):
            return "greeting"
        
        # Problem/complaint
        elif any(word in message_lower for word in ["problem", "issue", "wrong", "broken", "return", "refund"]):
            return "complaint"
        
        else:
            return "general"
        

    
    def _extract_suggestions(self, ai_response: str, intent: str) -> List[str]:
        """Extract actionable suggestions from AI response"""
        suggestions = []
        response_lower = ai_response.lower()
        
        # Product category suggestions
        if "dress" in response_lower:
            suggestions.append("Browse Dresses")
        if "shoes" in response_lower or "footwear" in response_lower:
            suggestions.append("Browse Shoes")
        if "accessories" in response_lower or "jewelry" in response_lower:
            suggestions.append("Browse Accessories")
        
        # Action suggestions based on intent
        if intent == "browsing":
            suggestions.append("See Recommendations")
        elif intent == "purchase_intent":
            suggestions.append("View Cart")
            suggestions.append("Checkout")
        elif intent == "needs_help":
            suggestions.append("Talk to Specialist")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _determine_next_actions(self, intent: str) -> List[str]:
        """Determine what actions should happen next"""
        actions = []
        
        if intent == "browsing":
            actions.append("get_recommendations")
            actions.append("check_inventory")
        
        elif intent == "purchase_intent":
            actions.append("prepare_checkout")
            actions.append("apply_discounts")
        
        elif intent == "needs_help":
            actions.append("check_inventory")
            actions.append("get_product_details")
        
        return actions
    
    def _needs_worker_agents(self, intent: str) -> List[str]:
        """Determine which worker agents should be called"""
        agents_needed = []
        
        if intent in ["browsing", "general"]:
            agents_needed.append("recommendation")
            agents_needed.append("inventory")
        
        elif intent == "purchase_intent":
            agents_needed.append("inventory")
            agents_needed.append("loyalty")
            agents_needed.append("payment")
        
        elif intent == "needs_help":
            agents_needed.append("inventory")
        
        return agents_needed
    
    async def chat(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Convenience method for simple chat (backward compatible)
        
        Args:
            message: Customer's message
            context: Optional context
            
        Returns:
            Chat response
        """
        if context is None:
            context = {}
        
        context["message"] = message
        
        return await self.execute(context)