# backend/agents/inventory_agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any, List, Optional
from database import SessionLocal
from models.models import Product
import json
from datetime import datetime, timedelta

class InventoryAgent(BaseAgent):
    """
    Inventory Agent - manages stock checking, reservations, and alternatives
    Critical for preventing out-of-stock disappointments
    """
    
    def __init__(self):
        super().__init__("InventoryAgent")
        self._log("Inventory Agent initialized")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check inventory and provide stock information
        
        Args:
            context: Product IDs, quantities, locations, etc.
            
        Returns:
            Stock availability, alternatives, fulfillment options
        """
        self._log("Checking inventory...")
        
        try:
            # Extract context
            product_ids = context.get("product_ids", [])
            quantities = context.get("quantities", {})
            customer_location = context.get("customer_location", "online")
            
            if not product_ids:
                return {
                    "success": False,
                    "message": "No products specified",
                    "availability": {}
                }
            
            # Check availability for each product
            availability_results = {}
            
            for product_id in product_ids:
                quantity_needed = quantities.get(str(product_id), 1)
                
                availability = await self._check_product_availability(
                    product_id=product_id,
                    quantity_needed=quantity_needed,
                    customer_location=customer_location
                )
                
                availability_results[str(product_id)] = availability
            
            self._log(f"Checked availability for {len(product_ids)} products")
            
            return {
                "success": True,
                "availability": availability_results,
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self._log(f"Error checking inventory: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "message": f"Inventory check failed: {str(e)}",
                "availability": {}
            }
    
    async def _check_product_availability(
        self,
        product_id: int,
        quantity_needed: int,
        customer_location: str
    ) -> Dict[str, Any]:
        """
        Check if specific product is available
        
        Args:
            product_id: Product to check
            quantity_needed: How many needed
            customer_location: Customer's location preference
            
        Returns:
            Detailed availability information
        """
        db = SessionLocal()
        
        try:
            # Get product from database
            product = db.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                return {
                    "available": False,
                    "reason": "Product not found",
                    "alternatives": []
                }
            
            # Parse inventory data
            inventory_by_location = self._parse_inventory(product.inventory)
            
            # Check stock at each location
            location_availability = []
            total_available = 0
            
            for location, stock_info in inventory_by_location.items():
                available_qty = stock_info.get("quantity", 0) - stock_info.get("reserved", 0)
                total_available += available_qty
                
                if available_qty >= quantity_needed:
                    location_availability.append({
                        "location": location,
                        "available_quantity": available_qty,
                        "can_fulfill": True,
                        "fulfillment_options": self._get_fulfillment_options(
                            location, 
                            customer_location
                        ),
                        "estimated_delivery": self._estimate_delivery_time(
                            location,
                            customer_location
                        )
                    })
                else:
                    location_availability.append({
                        "location": location,
                        "available_quantity": available_qty,
                        "can_fulfill": False,
                        "reason": f"Only {available_qty} available, need {quantity_needed}"
                    })
            
            # Overall availability
            is_available = total_available >= quantity_needed
            
            result = {
                "product_id": product_id,
                "product_name": product.name,
                "available": is_available,
                "total_stock": total_available,
                "quantity_requested": quantity_needed,
                "locations": location_availability
            }
            
            # Add alternatives if not available
            if not is_available:
                result["alternatives"] = await self._find_alternatives(product)
                result["suggestion"] = "Consider these similar items in stock"
            
            return result
            
        except Exception as e:
            self._log(f"Error checking product {product_id}: {e}", "ERROR")
            return {
                "available": False,
                "reason": f"Error: {str(e)}",
                "alternatives": []
            }
        finally:
            db.close()
    
    def _parse_inventory(self, inventory_data: Any) -> Dict[str, Dict[str, int]]:
        """
        Parse inventory data from various formats
        
        Args:
            inventory_data: Inventory data (could be JSON string, list, or dict)
            
        Returns:
            Dictionary of location -> stock info
        """
        try:
            # Handle string (JSON)
            if isinstance(inventory_data, str):
                inventory_list = json.loads(inventory_data)
            # Handle list
            elif isinstance(inventory_data, list):
                inventory_list = inventory_data
            # Handle None
            elif inventory_data is None:
                return {}
            else:
                return {}
            
            # Convert to location-based dict
            result = {}
            for item in inventory_list:
                if isinstance(item, dict):
                    location = item.get("location", "unknown")
                    result[location] = {
                        "quantity": item.get("quantity", 0),
                        "reserved": item.get("reserved", 0)
                    }
            
            return result
            
        except Exception as e:
            self._log(f"Error parsing inventory: {e}", "ERROR")
            return {}
    
    def _get_fulfillment_options(
        self,
        stock_location: str,
        customer_location: str
    ) -> List[str]:
        """
        Determine fulfillment options based on locations
        
        Args:
            stock_location: Where item is in stock
            customer_location: Customer's preferred location
            
        Returns:
            List of fulfillment options
        """
        options = []
        
        if stock_location == "online":
            options.append("ship_to_home")
            options.append("express_shipping")
        elif "store" in stock_location.lower():
            options.append("pickup_in_store")
            options.append("ship_from_store")
            options.append("try_in_store")
        
        return options
    
    def _estimate_delivery_time(
        self,
        stock_location: str,
        customer_location: str
    ) -> str:
        """
        Estimate delivery timeframe
        
        Args:
            stock_location: Where item is stocked
            customer_location: Customer's location
            
        Returns:
            Estimated delivery description
        """
        if stock_location == "online":
            return "3-5 business days"
        elif "store" in stock_location.lower():
            if customer_location == stock_location:
                return "Available today"
            else:
                return "1-2 business days from store"
        else:
            return "Standard shipping"
    
    async def _find_alternatives(self, product: Product) -> List[Dict[str, Any]]:
        """
        Find alternative products when item is out of stock
        
        Args:
            product: The out-of-stock product
            
        Returns:
            List of alternative products in stock
        """
        db = SessionLocal()
        
        try:
            # Find similar products in same category
            alternatives = db.query(Product).filter(
                Product.category == product.category,
                Product.id != product.id
            ).order_by(
                Product.rating.desc()
            ).limit(3).all()
            
            result = []
            for alt in alternatives:
                # Check if alternative is in stock
                inventory = self._parse_inventory(alt.inventory)
                total_stock = sum(
                    loc.get("quantity", 0) - loc.get("reserved", 0) 
                    for loc in inventory.values()
                )
                
                if total_stock > 0:
                    result.append({
                        "product_id": alt.id,
                        "name": alt.name,
                        "price": float(alt.price),
                        "brand": alt.brand,
                        "rating": float(alt.rating) if alt.rating else 0.0,
                        "in_stock": True,
                        "reason": f"Similar {alt.category.lower()} by {alt.brand}"
                    })
            
            return result
            
        except Exception as e:
            self._log(f"Error finding alternatives: {e}", "ERROR")
            return []
        finally:
            db.close()
    
    async def reserve_items(
        self,
        items: List[Dict[str, Any]],
        session_id: str,
        duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Reserve items for a customer during checkout
        
        Args:
            items: List of items to reserve (product_id, quantity, location)
            session_id: Session ID for tracking
            duration_minutes: How long to hold reservation
            
        Returns:
            Reservation confirmation
        """
        self._log(f"Reserving {len(items)} items for session {session_id}")
        
        db = SessionLocal()
        reservations = []
        
        try:
            for item in items:
                product_id = item.get("product_id")
                quantity = item.get("quantity", 1)
                location = item.get("location", "online")
                
                # Get product
                product = db.query(Product).filter(Product.id == product_id).first()
                
                if product:
                    # Parse inventory
                    inventory = self._parse_inventory(product.inventory)
                    
                    # Update reserved quantity
                    if location in inventory:
                        inventory[location]["reserved"] = inventory[location].get("reserved", 0) + quantity
                    
                    # Save back to database
                    product.inventory = json.dumps([
                        {"location": loc, "quantity": info["quantity"], "reserved": info.get("reserved", 0)}
                        for loc, info in inventory.items()
                    ])
                    
                    db.commit()
                    
                    reservations.append({
                        "product_id": product_id,
                        "product_name": product.name,
                        "quantity": quantity,
                        "location": location,
                        "reserved_until": (datetime.now() + timedelta(minutes=duration_minutes)).isoformat(),
                        "status": "reserved"
                    })
            
            return {
                "success": True,
                "reservations": reservations,
                "session_id": session_id,
                "expires_in_minutes": duration_minutes
            }
            
        except Exception as e:
            self._log(f"Error reserving items: {e}", "ERROR")
            db.rollback()
            return {
                "success": False,
                "message": f"Reservation failed: {str(e)}",
                "reservations": []
            }
        finally:
            db.close()
    
    async def check_multiple_products(
        self,
        product_ids: List[int],
        quantities: Dict[str, int] = None,
        customer_location: str = "online"
    ) -> Dict[str, Any]:
        """
        Convenience method to check multiple products
        
        Args:
            product_ids: List of product IDs
            quantities: Dict of product_id -> quantity needed
            customer_location: Customer's location
            
        Returns:
            Availability results
        """
        context = {
            "product_ids": product_ids,
            "quantities": quantities or {},
            "customer_location": customer_location
        }
        
        return await self.execute(context)