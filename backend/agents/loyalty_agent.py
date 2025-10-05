# backend/agents/loyalty_agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any, List, Optional
from database import SessionLocal
from models.models import Customer
from datetime import datetime, timedelta

class LoyaltyAgent(BaseAgent):
    """
    Loyalty Agent - manages loyalty program, points, and member benefits
    Drives repeat business and customer lifetime value
    """
    
    def __init__(self):
        super().__init__("LoyaltyAgent")
        self._log("Loyalty Agent initialized")
        
        # Loyalty tier benefits
        self.tier_benefits = {
            "Bronze": {
                "discount": 0.0,
                "points_multiplier": 1.0,
                "free_shipping_threshold": 100,
                "early_access": False
            },
            "Silver": {
                "discount": 0.05,  # 5% off
                "points_multiplier": 1.5,
                "free_shipping_threshold": 75,
                "early_access": True
            },
            "Gold": {
                "discount": 0.10,  # 10% off
                "points_multiplier": 2.0,
                "free_shipping_threshold": 50,
                "early_access": True
            },
            "Platinum": {
                "discount": 0.15,  # 15% off
                "points_multiplier": 3.0,
                "free_shipping_threshold": 0,  # Always free
                "early_access": True
            }
        }
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process loyalty-related request
        
        Args:
            context: Customer info, action type (check_benefits, apply_points, etc.)
            
        Returns:
            Loyalty information or action result
        """
        self._log("Processing loyalty request...")
        
        try:
            action = context.get("action", "check_benefits")
            customer_id = context.get("customer_id")
            
            if not customer_id:
                return {
                    "success": False,
                    "message": "Customer ID required"
                }
            
            if action == "check_benefits":
                return await self._get_customer_benefits(customer_id)
            
            elif action == "calculate_points":
                purchase_amount = context.get("purchase_amount", 0)
                return await self._calculate_points_earned(customer_id, purchase_amount)
            
            elif action == "redeem_points":
                points_to_redeem = context.get("points", 0)
                return await self._redeem_points(customer_id, points_to_redeem)
            
            elif action == "get_offers":
                return await self._get_personalized_offers(customer_id)
            
            else:
                return {
                    "success": False,
                    "message": f"Unknown action: {action}"
                }
            
        except Exception as e:
            self._log(f"Error in loyalty agent: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "message": f"Loyalty processing failed: {str(e)}"
            }
    
    async def _get_customer_benefits(self, customer_id: int) -> Dict[str, Any]:
        """
        Get customer's loyalty benefits
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Complete benefits information
        """
        db = SessionLocal()
        
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            
            if not customer:
                return {
                    "success": False,
                    "message": "Customer not found"
                }
            
            # Get tier benefits
            tier = customer.loyalty_tier or "Bronze"
            benefits = self.tier_benefits.get(tier, self.tier_benefits["Bronze"])
            
            # Calculate points value
            points_value = customer.loyalty_points / 100  # 100 points = $1
            
            # Check for birthday bonus
            birthday_bonus = self._check_birthday_bonus(customer)
            
            # Get next tier info
            next_tier_info = self._get_next_tier_info(tier, customer.loyalty_points)
            
            return {
                "success": True,
                "customer_name": customer.name,
                "loyalty_tier": tier,
                "loyalty_points": customer.loyalty_points,
                "points_value": round(points_value, 2),
                "benefits": {
                    "member_discount": f"{int(benefits['discount'] * 100)}%",
                    "points_multiplier": f"{benefits['points_multiplier']}x",
                    "free_shipping_threshold": f"${benefits['free_shipping_threshold']}" if benefits['free_shipping_threshold'] > 0 else "Always free",
                    "early_access": benefits['early_access']
                },
                "birthday_bonus": birthday_bonus,
                "next_tier": next_tier_info
            }
            
        finally:
            db.close()
    
    def _check_birthday_bonus(self, customer: Customer) -> Optional[Dict[str, Any]]:
        """Check if customer has birthday bonus available"""
        # This is a mock - in production would check actual birthday
        # For demo, randomly assign birthday bonuses
        import random
        if random.random() < 0.2:  # 20% chance
            return {
                "available": True,
                "bonus_points": 500,
                "special_discount": 0.15,  # 15% off
                "message": "🎉 Happy Birthday! Enjoy your special discount!"
            }
        return None
    
    def _get_next_tier_info(self, current_tier: str, current_points: int) -> Dict[str, Any]:
        """Calculate progress to next tier"""
        tier_thresholds = {
            "Bronze": {"next": "Silver", "points_needed": 1000},
            "Silver": {"next": "Gold", "points_needed": 2500},
            "Gold": {"next": "Platinum", "points_needed": 5000},
            "Platinum": {"next": None, "points_needed": 0}
        }
        
        tier_info = tier_thresholds.get(current_tier, tier_thresholds["Bronze"])
        
        if tier_info["next"]:
            points_to_next = tier_info["points_needed"] - current_points
            progress = (current_points / tier_info["points_needed"]) * 100
            
            return {
                "next_tier": tier_info["next"],
                "points_needed": max(0, points_to_next),
                "progress_percent": min(100, round(progress, 1)),
                "message": f"Earn {max(0, points_to_next)} more points to reach {tier_info['next']}!"
            }
        else:
            return {
                "next_tier": None,
                "message": "You're at the highest tier! 🏆"
            }
    
    async def _calculate_points_earned(
        self, 
        customer_id: int, 
        purchase_amount: float
    ) -> Dict[str, Any]:
        """
        Calculate points earned for a purchase
        
        Args:
            customer_id: Customer ID
            purchase_amount: Purchase amount in dollars
            
        Returns:
            Points calculation
        """
        db = SessionLocal()
        
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            
            if not customer:
                return {
                    "success": False,
                    "message": "Customer not found"
                }
            
            # Get tier multiplier
            tier = customer.loyalty_tier or "Bronze"
            benefits = self.tier_benefits.get(tier, self.tier_benefits["Bronze"])
            multiplier = benefits["points_multiplier"]
            
            # Base: 1 point per dollar
            base_points = int(purchase_amount)
            
            # Apply multiplier
            total_points = int(base_points * multiplier)
            
            # Bonus for large purchases
            if purchase_amount >= 200:
                bonus_points = 100
                total_points += bonus_points
                bonus_message = "🎁 Bonus: +100 points for purchase over $200!"
            else:
                bonus_points = 0
                bonus_message = None
            
            return {
                "success": True,
                "purchase_amount": purchase_amount,
                "base_points": base_points,
                "multiplier": multiplier,
                "bonus_points": bonus_points,
                "total_points_earned": total_points,
                "bonus_message": bonus_message,
                "new_total_points": customer.loyalty_points + total_points
            }
            
        finally:
            db.close()
    
    async def _redeem_points(
        self, 
        customer_id: int, 
        points_to_redeem: int
    ) -> Dict[str, Any]:
        """
        Redeem loyalty points for discount
        
        Args:
            customer_id: Customer ID
            points_to_redeem: Number of points to redeem
            
        Returns:
            Redemption result
        """
        db = SessionLocal()
        
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            
            if not customer:
                return {
                    "success": False,
                    "message": "Customer not found"
                }
            
            if customer.loyalty_points < points_to_redeem:
                return {
                    "success": False,
                    "message": f"Insufficient points. You have {customer.loyalty_points} points.",
                    "available_points": customer.loyalty_points
                }
            
            # Calculate discount value (100 points = $1)
            discount_amount = points_to_redeem / 100
            
            # Update customer points (actual update would happen in payment agent)
            # This is just for validation
            
            return {
                "success": True,
                "points_redeemed": points_to_redeem,
                "discount_amount": round(discount_amount, 2),
                "remaining_points": customer.loyalty_points - points_to_redeem,
                "message": f"✅ {points_to_redeem} points redeemed for ${discount_amount:.2f} discount"
            }
            
        finally:
            db.close()
    
    async def _get_personalized_offers(self, customer_id: int) -> Dict[str, Any]:
        """
        Get personalized offers for customer
        
        Args:
            customer_id: Customer ID
            
        Returns:
            List of personalized offers
        """
        db = SessionLocal()
        
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            
            if not customer:
                return {
                    "success": False,
                    "message": "Customer not found"
                }
            
            tier = customer.loyalty_tier or "Bronze"
            offers = []
            
            # Tier-based offers
            if tier in ["Gold", "Platinum"]:
                offers.append({
                    "type": "exclusive_access",
                    "title": "VIP Early Access",
                    "description": "Shop new arrivals 48 hours before everyone else",
                    "valid_until": (datetime.now() + timedelta(days=7)).strftime("%B %d, %Y")
                })
            
            if tier in ["Silver", "Gold", "Platinum"]:
                offers.append({
                    "type": "free_shipping",
                    "title": "Free Express Shipping",
                    "description": f"On orders over ${self.tier_benefits[tier]['free_shipping_threshold']}",
                    "valid_until": "Always active"
                })
            
            # Points-based offers
            if customer.loyalty_points >= 500:
                offers.append({
                    "type": "points_bonus",
                    "title": "Double Points Weekend",
                    "description": "Earn 2x points on all purchases this weekend",
                    "valid_until": (datetime.now() + timedelta(days=3)).strftime("%B %d, %Y")
                })
            
            # Category-based offers (from purchase history)
            if customer.purchase_history:
                offers.append({
                    "type": "category_discount",
                    "title": "20% Off Your Favorites",
                    "description": "Special discount on categories you love",
                    "valid_until": (datetime.now() + timedelta(days=14)).strftime("%B %d, %Y")
                })
            
            # Birthday offer
            birthday_bonus = self._check_birthday_bonus(customer)
            if birthday_bonus and birthday_bonus.get("available"):
                offers.append({
                    "type": "birthday",
                    "title": "🎂 Birthday Special",
                    "description": birthday_bonus["message"],
                    "bonus_points": birthday_bonus["bonus_points"],
                    "discount": f"{int(birthday_bonus['special_discount'] * 100)}%",
                    "valid_until": (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y")
                })
            
            return {
                "success": True,
                "customer_name": customer.name,
                "loyalty_tier": tier,
                "total_offers": len(offers),
                "offers": offers
            }
            
        finally:
            db.close()
    
    async def get_customer_loyalty_info(self, customer_id: int) -> Dict[str, Any]:
        """
        Convenience method to get complete loyalty information
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Complete loyalty profile
        """
        context = {
            "action": "check_benefits",
            "customer_id": customer_id
        }
        
        return await self.execute(context)