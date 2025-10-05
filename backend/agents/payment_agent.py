# backend/agents/payment_agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any, List, Optional
from database import SessionLocal
from models.models import Product, Customer
from datetime import datetime
import uuid
import random

class PaymentAgent(BaseAgent):
    """
    Payment Agent - handles checkout, pricing, discounts, and payment processing
    This is where we convert cart into revenue
    """
    
    def __init__(self):
        super().__init__("PaymentAgent")
        self._log("Payment Agent initialized")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment and complete purchase
        
        Args:
            context: Cart items, customer info, payment method, etc.
            
        Returns:
            Payment result, order confirmation, or error with recovery options
        """
        self._log("Processing payment...")
        
        try:
            # Extract context
            cart_items = context.get("cart_items", [])
            customer_id = context.get("customer_id")
            payment_method = context.get("payment_method", "card")
            apply_loyalty = context.get("apply_loyalty", True)
            coupon_code = context.get("coupon_code")
            
            if not cart_items:
                return {
                    "success": False,
                    "message": "Cart is empty",
                    "error_type": "empty_cart"
                }
            
            # Calculate pricing
            pricing = await self._calculate_pricing(
                cart_items=cart_items,
                customer_id=customer_id,
                apply_loyalty=apply_loyalty,
                coupon_code=coupon_code
            )
            
            # Validate payment method
            payment_validation = self._validate_payment_method(payment_method)
            if not payment_validation["valid"]:
                return {
                    "success": False,
                    "message": payment_validation["message"],
                    "error_type": "invalid_payment_method",
                    "alternatives": self._get_alternative_payment_methods()
                }
            
            # Process payment (mock for demo)
            payment_result = await self._process_payment(
                amount=pricing["final_total"],
                payment_method=payment_method,
                customer_id=customer_id
            )
            
            if payment_result["success"]:
                # Create order
                order = await self._create_order(
                    cart_items=cart_items,
                    customer_id=customer_id,
                    pricing=pricing,
                    payment_result=payment_result
                )
                
                self._log(f"Payment successful! Order {order['order_id']} created")
                
                return {
                    "success": True,
                    "message": "Payment successful!",
                    "order": order,
                    "pricing": pricing,
                    "payment_details": payment_result
                }
            else:
                # Payment failed - provide recovery options
                return {
                    "success": False,
                    "message": payment_result["error"],
                    "error_type": payment_result["error_type"],
                    "recovery_options": self._get_recovery_options(
                        payment_result["error_type"],
                        pricing
                    )
                }
            
        except Exception as e:
            self._log(f"Error processing payment: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "message": f"Payment processing failed: {str(e)}",
                "error_type": "system_error"
            }
    
    async def _calculate_pricing(
        self,
        cart_items: List[Dict[str, Any]],
        customer_id: int = None,
        apply_loyalty: bool = True,
        coupon_code: str = None
    ) -> Dict[str, Any]:
        """
        Calculate complete pricing with all discounts
        
        Args:
            cart_items: Items in cart
            customer_id: Customer for loyalty discounts
            apply_loyalty: Whether to use loyalty points
            coupon_code: Promotional code
            
        Returns:
            Complete pricing breakdown
        """
        db = SessionLocal()
        
        try:
            subtotal = 0.0
            items_detail = []
            
            # Calculate subtotal
            for item in cart_items:
                product_id = item.get("product_id")
                quantity = item.get("quantity", 1)
                
                # Get product price
                product = db.query(Product).filter(Product.id == product_id).first()
                if product:
                    item_price = float(product.price)
                    item_total = item_price * quantity
                    subtotal += item_total
                    
                    items_detail.append({
                        "product_id": product_id,
                        "name": product.name,
                        "price": item_price,
                        "quantity": quantity,
                        "total": item_total
                    })
            
            # Apply discounts
            discounts = []
            total_discount = 0.0
            
            # Bundle discount (if 3+ items)
            if len(cart_items) >= 3:
                bundle_discount = subtotal * 0.10  # 10% off
                discounts.append({
                    "type": "bundle_discount",
                    "description": "10% off for 3+ items",
                    "amount": bundle_discount
                })
                total_discount += bundle_discount
            
            # Loyalty points discount
            loyalty_discount = 0.0
            points_used = 0
            if apply_loyalty and customer_id:
                customer = db.query(Customer).filter(Customer.id == customer_id).first()
                if customer and customer.loyalty_points > 0:
                    # 100 points = $1 discount
                    max_points_usable = min(customer.loyalty_points, int(subtotal * 100))  # Can't exceed subtotal
                    points_used = max_points_usable
                    loyalty_discount = max_points_usable / 100
                    
                    discounts.append({
                        "type": "loyalty_points",
                        "description": f"{points_used} loyalty points redeemed",
                        "amount": loyalty_discount
                    })
                    total_discount += loyalty_discount
            
            # Coupon code discount
            if coupon_code:
                coupon_discount = self._apply_coupon(coupon_code, subtotal)
                if coupon_discount > 0:
                    discounts.append({
                        "type": "coupon_code",
                        "description": f"Coupon: {coupon_code}",
                        "amount": coupon_discount
                    })
                    total_discount += coupon_discount
            
            # Calculate tax (8% for demo)
            taxable_amount = subtotal - total_discount
            tax = taxable_amount * 0.08
            
            # Calculate final total
            final_total = subtotal - total_discount + tax
            
            # Calculate loyalty points earned (1 point per dollar spent)
            points_earned = int(final_total)
            
            return {
                "subtotal": round(subtotal, 2),
                "items": items_detail,
                "discounts": discounts,
                "total_discount": round(total_discount, 2),
                "tax": round(tax, 2),
                "final_total": round(final_total, 2),
                "loyalty": {
                    "points_used": points_used,
                    "points_earned": points_earned,
                    "discount_applied": round(loyalty_discount, 2)
                },
                "savings": round(total_discount, 2)
            }
            
        finally:
            db.close()
    
    def _apply_coupon(self, coupon_code: str, subtotal: float) -> float:
        """
        Apply coupon code discount (mock implementation)
        
        Args:
            coupon_code: Coupon code
            subtotal: Current subtotal
            
        Returns:
            Discount amount
        """
        # Mock coupon codes for demo
        coupons = {
            "WELCOME10": 0.10,  # 10% off
            "SAVE20": 0.20,     # 20% off
            "BIRTHDAY": 0.15,   # 15% off
            "VIP25": 0.25       # 25% off
        }
        
        discount_percent = coupons.get(coupon_code.upper(), 0)
        return subtotal * discount_percent
    
    def _validate_payment_method(self, payment_method: str) -> Dict[str, Any]:
        """
        Validate payment method
        
        Args:
            payment_method: Payment method type
            
        Returns:
            Validation result
        """
        valid_methods = ["card", "paypal", "apple_pay", "google_pay", "gift_card"]
        
        if payment_method.lower() in valid_methods:
            return {
                "valid": True,
                "message": "Payment method accepted"
            }
        else:
            return {
                "valid": False,
                "message": f"Payment method '{payment_method}' not supported"
            }
    
    async def _process_payment(
        self,
        amount: float,
        payment_method: str,
        customer_id: int = None
    ) -> Dict[str, Any]:
        """
        Process payment (mock implementation for demo)
        In production, this would integrate with Stripe, PayPal, etc.
        
        Args:
            amount: Amount to charge
            payment_method: Payment method
            customer_id: Customer ID
            
        Returns:
            Payment result
        """
        # Mock payment processing with 90% success rate
        success_rate = 0.90
        is_successful = random.random() < success_rate
        
        if is_successful:
            return {
                "success": True,
                "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
                "amount": amount,
                "payment_method": payment_method,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
        else:
            # Simulate different failure types
            failure_types = [
                {
                    "error_type": "insufficient_funds",
                    "error": "Payment declined - insufficient funds",
                    "retry_allowed": False
                },
                {
                    "error_type": "card_declined",
                    "error": "Payment declined by card issuer",
                    "retry_allowed": True
                },
                {
                    "error_type": "network_error",
                    "error": "Network error - please try again",
                    "retry_allowed": True
                }
            ]
            
            failure = random.choice(failure_types)
            
            return {
                "success": False,
                "error": failure["error"],
                "error_type": failure["error_type"],
                "retry_allowed": failure["retry_allowed"]
            }
    
    async def _create_order(
        self,
        cart_items: List[Dict[str, Any]],
        customer_id: int,
        pricing: Dict[str, Any],
        payment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create order record
        
        Args:
            cart_items: Items purchased
            customer_id: Customer ID
            pricing: Pricing details
            payment_result: Payment transaction details
            
        Returns:
            Order details
        """
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        order = {
            "order_id": order_id,
            "customer_id": customer_id,
            "items": pricing["items"],
            "pricing": {
                "subtotal": pricing["subtotal"],
                "discount": pricing["total_discount"],
                "tax": pricing["tax"],
                "total": pricing["final_total"]
            },
            "payment": {
                "method": payment_result["payment_method"],
                "transaction_id": payment_result["transaction_id"],
                "status": "paid"
            },
            "loyalty": pricing["loyalty"],
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
            "estimated_delivery": self._estimate_delivery()
        }
        
        # Update customer loyalty points
        if customer_id:
            db = SessionLocal()
            try:
                customer = db.query(Customer).filter(Customer.id == customer_id).first()
                if customer:
                    # Deduct used points
                    customer.loyalty_points -= pricing["loyalty"]["points_used"]
                    # Add earned points
                    customer.loyalty_points += pricing["loyalty"]["points_earned"]
                    db.commit()
            finally:
                db.close()
        
        return order
    
    def _estimate_delivery(self) -> str:
        """Estimate delivery date"""
        from datetime import timedelta
        delivery_date = datetime.now() + timedelta(days=3)
        return delivery_date.strftime("%B %d, %Y")
    
    def _get_alternative_payment_methods(self) -> List[str]:
        """Get alternative payment methods"""
        return ["card", "paypal", "apple_pay", "google_pay", "gift_card"]
    
    def _get_recovery_options(
        self,
        error_type: str,
        pricing: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Provide recovery options based on error type
        
        Args:
            error_type: Type of payment error
            pricing: Current pricing details
            
        Returns:
            List of recovery options
        """
        options = []
        
        if error_type == "insufficient_funds":
            options.append({
                "option": "use_loyalty_points",
                "description": f"Use loyalty points to reduce total to ${pricing['final_total'] - 20}"
            })
            options.append({
                "option": "remove_items",
                "description": "Remove some items to lower the total"
            })
            options.append({
                "option": "split_payment",
                "description": "Split payment across multiple cards"
            })
        
        elif error_type == "card_declined":
            options.append({
                "option": "try_different_card",
                "description": "Try a different payment card"
            })
            options.append({
                "option": "use_alternative_method",
                "description": "Use PayPal, Apple Pay, or Google Pay"
            })
        
        elif error_type == "network_error":
            options.append({
                "option": "retry_payment",
                "description": "Try payment again"
            })
        
        return options
    
    async def process_checkout(
        self,
        cart_items: List[Dict[str, Any]],
        customer_id: int = None,
        payment_method: str = "card",
        apply_loyalty: bool = True,
        coupon_code: str = None
    ) -> Dict[str, Any]:
        """
        Convenience method for checkout process
        
        Args:
            cart_items: Items to purchase
            customer_id: Customer ID
            payment_method: Payment method
            apply_loyalty: Use loyalty points
            coupon_code: Promotional code
            
        Returns:
            Checkout result
        """
        context = {
            "cart_items": cart_items,
            "customer_id": customer_id,
            "payment_method": payment_method,
            "apply_loyalty": apply_loyalty,
            "coupon_code": coupon_code
        }
        
        return await self.execute(context)