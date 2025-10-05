# backend/agents/recommendation_agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any, List, Optional
from database import SessionLocal
from models.models import Product, Customer
import json

class RecommendationAgent(BaseAgent):
    """
    Recommendation Agent - suggests products based on customer preferences
    This is our main revenue driver - smart recommendations = higher sales
    """
    
    def __init__(self):
        super().__init__("RecommendationAgent")
        self._log("Recommendation Agent initialized")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized product recommendations
        
        Args:
            context: Customer info, preferences, occasion, budget, etc.
            
        Returns:
            List of recommended products with reasoning
        """
        self._log("Generating recommendations...")
        
        try:
            # Extract context with safe defaults
            customer_info = context.get("customer_info", {}) if isinstance(context, dict) else {}
            intent = context.get("intent", "general") if isinstance(context, dict) else "general"
            occasion = context.get("occasion", "") if isinstance(context, dict) else ""
            budget = context.get("budget") if isinstance(context, dict) else None
            category = context.get("category") if isinstance(context, dict) else None
            
            # Get products from database
            products = self._get_products_from_db(category=category, budget=budget)
            
            if not products:
                return {
                    "success": False,
                    "message": "No products found matching criteria",
                    "recommendations": []
                }
            
            # Use AI to analyze and recommend
            recommendations = await self._generate_smart_recommendations(
                products=products,
                customer_info=customer_info,
                occasion=occasion,
                budget=budget
            )
            
            # Add complementary items (upselling)
            if recommendations:
                recommendations = self._add_complementary_items(recommendations, products)
            
            self._log(f"Generated {len(recommendations)} recommendations")
            
            return {
                "success": True,
                "recommendations": recommendations,
                "total_items": len(recommendations),
                "reasoning": "Based on customer preferences and occasion"
            }
            
        except Exception as e:
            self._log(f"Error in execute: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            
            # Return fallback recommendations
            products = self._get_products_from_db(limit=3)
            if products:
                fallback_recs = self._fallback_recommendations(products)
                return {
                    "success": True,
                    "recommendations": fallback_recs,
                    "total_items": len(fallback_recs),
                    "reasoning": "Popular items",
                    "note": "Using fallback recommendations"
                }
            
            return {
                "success": False,
                "message": f"Error generating recommendations: {str(e)}",
                "recommendations": []
            }
    
    def _get_products_from_db(
        self, 
        category: str = None, 
        budget: float = None,
        limit: int = 20
    ) -> List[Product]:
        """
        Fetch products from database with filters
        
        Args:
            category: Filter by category (optional)
            budget: Maximum price (optional)
            limit: Maximum products to return
            
        Returns:
            List of Product objects
        """
        db = SessionLocal()
        
        try:
            query = db.query(Product)
            
            # Apply filters
            if category:
                query = query.filter(Product.category.ilike(f"%{category}%"))
            
            if budget:
                query = query.filter(Product.price <= budget)
            
            # Order by rating and purchases (most popular first)
            query = query.order_by(Product.rating.desc(), Product.purchases.desc())
            
            # Limit results
            products = query.limit(limit).all()
            
            self._log(f"Found {len(products)} products in database")
            
            return products
            
        except Exception as e:
            self._log(f"Error fetching products: {e}", "ERROR")
            return []
        finally:
            db.close()
    
    async def _generate_smart_recommendations(
        self,
        products: List[Product],
        customer_info: Dict[str, Any],
        occasion: str,
        budget: float
    ) -> List[Dict[str, Any]]:
        """
        Use AI to intelligently recommend and rank products
        
        Args:
            products: Available products
            customer_info: Customer preferences
            occasion: What they're shopping for
            budget: Price limit
            
        Returns:
            Ranked list of recommendations with reasoning
        """
        try:
            # Prepare product data for AI
            product_descriptions = []
            for p in products[:10]:  # Limit to top 10 to fit in prompt
                product_descriptions.append({
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "category": p.category,
                    "brand": p.brand,
                    "rating": p.rating,
                    "purchases": p.purchases
                })
            
            # Build AI prompt
            system_prompt = """You are an expert personal shopper and stylist.
Analyze the customer's preferences and occasion, then recommend the BEST products from the list.

For each recommendation, provide:
1. Why it perfectly matches their needs
2. How it fits the occasion
3. What makes it special
4. Style/pairing suggestions

Return ONLY a JSON array with this structure (no other text):
[
  {
    "product_id": 1,
    "confidence": 95,
    "reason": "This emerald dress is perfect because...",
    "occasion_fit": "Ideal for a birthday celebration...",
    "styling_tip": "Pair with gold accessories...",
    "priority": 1
  }
]

Only recommend products that TRULY match. Quality over quantity."""

            user_message = f"""Customer Profile:
{json.dumps(customer_info, indent=2) if customer_info else "No specific preferences"}

Occasion: {occasion if occasion else "General shopping"}
Budget: ${budget if budget else "Not specified"}

Available Products:
{json.dumps(product_descriptions, indent=2)}

Recommend the TOP 3-5 products that best match this customer."""

            # Get AI recommendations
            ai_response = await self._call_ai(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.6,
                max_tokens=800
            )
            
            self._log(f"AI Response received: {ai_response[:100]}...")
            
            # Parse AI response
            ai_recommendations = self._extract_json_from_text(ai_response)
            
            if not ai_recommendations or not isinstance(ai_recommendations, list):
                self._log("AI parsing failed, using fallback", "WARNING")
                return self._fallback_recommendations(products[:3])
            
            # Merge AI recommendations with product data
            final_recommendations = []
            for rec in ai_recommendations:
                if not isinstance(rec, dict):
                    continue
                    
                product_id = rec.get("product_id")
                product = next((p for p in products if p.id == product_id), None)
                
                if product:
                    final_recommendations.append({
                        "product_id": product.id,
                        "name": product.name,
                        "price": float(product.price),
                        "original_price": float(product.original_price) if product.original_price else float(product.price),
                        "brand": product.brand or "Unknown",
                        "category": product.category or "General",
                        "image": product.images[0] if product.images and len(product.images) > 0 else None,
                        "rating": float(product.rating) if product.rating else 0.0,
                        "in_stock": self._check_stock(product),
                        "confidence": int(rec.get("confidence", 80)),
                        "reason": str(rec.get("reason", "Great match for your style")),
                        "occasion_fit": str(rec.get("occasion_fit", "Perfect for your needs")),
                        "styling_tip": str(rec.get("styling_tip", "")),
                        "priority": int(rec.get("priority", 99))
                    })
            
            # Sort by priority
            final_recommendations.sort(key=lambda x: x["priority"])
            
            return final_recommendations if final_recommendations else self._fallback_recommendations(products[:3])
            
        except Exception as e:
            self._log(f"Error in smart recommendations: {e}", "ERROR")
            return self._fallback_recommendations(products[:3])
    
    def _add_complementary_items(
        self, 
        recommendations: List[Dict[str, Any]], 
        all_products: List[Product]
    ) -> List[Dict[str, Any]]:
        """
        Add complementary items for upselling
        
        Args:
            recommendations: Current recommendations
            all_products: All available products
            
        Returns:
            Recommendations with complementary items added
        """
        if not recommendations:
            return recommendations
        
        try:
            # Get categories of recommended items
            recommended_categories = set(r.get("category", "") for r in recommendations)
            
            # Complementary category rules
            complementary_rules = {
                "Dresses": ["Shoes", "Accessories"],
                "Shoes": ["Accessories"],
                "Accessories": ["Dresses", "Shoes"]
            }
            
            # Find complementary items
            for rec_category in recommended_categories:
                complementary_categories = complementary_rules.get(rec_category, [])
                
                for comp_category in complementary_categories:
                    # Find products in complementary category
                    comp_products = [p for p in all_products if p.category == comp_category]
                    
                    if comp_products:
                        # Add best complementary item
                        best_comp = comp_products[0]  # Already sorted by rating
                        
                        # Only add if not already in recommendations
                        if not any(r.get("product_id") == best_comp.id for r in recommendations):
                            recommendations.append({
                                "product_id": best_comp.id,
                                "name": best_comp.name,
                                "price": float(best_comp.price),
                                "original_price": float(best_comp.original_price) if best_comp.original_price else float(best_comp.price),
                                "brand": best_comp.brand or "Unknown",
                                "category": best_comp.category or "General",
                                "image": best_comp.images[0] if best_comp.images and len(best_comp.images) > 0 else None,
                                "rating": float(best_comp.rating) if best_comp.rating else 0.0,
                                "in_stock": self._check_stock(best_comp),
                                "is_complementary": True,
                                "reason": f"Pairs perfectly with your {rec_category.lower()}",
                                "confidence": 75
                            })
                            break  # Only add one complementary per category
            
            return recommendations[:5]  # Limit to 5 total recommendations
            
        except Exception as e:
            self._log(f"Error adding complementary items: {e}", "ERROR")
            return recommendations
    
    def _check_stock(self, product: Product) -> bool:
        """
        Check if product is in stock
        
        Args:
            product: Product to check
            
        Returns:
            True if in stock, False otherwise
        """
        try:
            if not product.inventory:
                return True  # Assume in stock if no inventory data
            
            # Handle if inventory is a string (JSON stored as string)
            if isinstance(product.inventory, str):
                try:
                    inventory_list = json.loads(product.inventory)
                except:
                    return True  # Assume in stock if can't parse
            elif isinstance(product.inventory, list):
                inventory_list = product.inventory
            else:
                return True  # Unknown format, assume in stock
            
            # Calculate total stock
            total_stock = 0
            for inv in inventory_list:
                if isinstance(inv, dict):
                    total_stock += inv.get("quantity", 0)
            
            return total_stock > 0
            
        except Exception as e:
            self._log(f"Error checking stock: {e}", "ERROR")
            return True  # Default to in stock on error
    
    def _fallback_recommendations(self, products: List[Product]) -> List[Dict[str, Any]]:
        """
        Simple fallback if AI recommendation fails
        
        Args:
            products: Products to recommend
            
        Returns:
            Basic recommendations
        """
        recommendations = []
        
        try:
            for product in products:
                recommendations.append({
                    "product_id": product.id,
                    "name": product.name,
                    "price": float(product.price),
                    "original_price": float(product.original_price) if product.original_price else float(product.price),
                    "brand": product.brand or "Unknown",
                    "category": product.category or "General",
                    "image": product.images[0] if product.images and len(product.images) > 0 else None,
                    "rating": float(product.rating) if product.rating else 0.0,
                    "in_stock": self._check_stock(product),
                    "reason": "Popular choice based on ratings and reviews",
                    "confidence": 70
                })
        except Exception as e:
            self._log(f"Error in fallback: {e}", "ERROR")
        
        return recommendations
    
    async def recommend_for_customer(
        self, 
        customer_id: int = None,
        occasion: str = "",
        category: str = None,
        budget: float = None
    ) -> Dict[str, Any]:
        """
        Convenience method to get recommendations for a specific customer
        
        Args:
            customer_id: Customer ID (optional)
            occasion: Shopping occasion
            category: Specific category
            budget: Maximum price
            
        Returns:
            Recommendations
        """
        # Get customer info if ID provided
        customer_info = {}
        if customer_id:
            db = SessionLocal()
            try:
                customer = db.query(Customer).filter(Customer.id == customer_id).first()
                if customer:
                    customer_info = {
                        "name": customer.name,
                        "preferences": customer.preferences if customer.preferences else {},
                        "loyalty_tier": customer.loyalty_tier,
                        "purchase_history": customer.purchase_history if customer.purchase_history else []
                    }
            except Exception as e:
                self._log(f"Error fetching customer: {e}", "ERROR")
            finally:
                db.close()
        
        # Build context
        context = {
            "customer_info": customer_info,
            "occasion": occasion,
            "category": category,
            "budget": budget
        }
        
        return await self.execute(context)