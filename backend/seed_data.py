# backend/seed_data.py
from database import SessionLocal
from models.models import Customer, Product
from datetime import datetime

def seed_database():
    """Add sample data for testing"""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database with sample data...")
        
        # Sample customers
        customers = [
            Customer(
                name="Sarah Johnson",
                email="sarah.j@email.com",
                phone="+1234567890",
                preferences={
                    "styles": ["elegant", "casual-chic"],
                    "colors": ["blue", "green", "black"],
                    "sizes": {"dress": "M", "shoes": 8}
                },
                loyalty_tier="Silver",
                loyalty_points=1250
            ),
            Customer(
                name="Mike Chen",
                email="mike.c@email.com",
                phone="+1234567891",
                preferences={
                    "styles": ["casual", "sporty"],
                    "colors": ["black", "gray", "navy"]
                },
                loyalty_tier="Gold",
                loyalty_points=2500
            )
        ]
        
        # Sample products
        products = [
            Product(
                name="Emerald Silk Midi Dress",
                sku="DRESS-001",
                category="Dresses",
                brand="EliteWear",
                price=180.00,
                original_price=199.00,
                attributes={
                    "color": "Emerald Green",
                    "sizes": ["XS", "S", "M", "L", "XL"],
                    "material": "Silk",
                    "occasion": ["formal", "party", "date-night"]
                },
                inventory=[
                    {"location": "online", "quantity": 45},
                    {"location": "store_downtown", "quantity": 8},
                    {"location": "store_mall", "quantity": 12}
                ],
                description="Elegant emerald green silk midi dress perfect for special occasions.",
                images=["emerald_dress_1.jpg", "emerald_dress_2.jpg"],
                views=1250,
                purchases=45,
                rating=4.8
            ),
            Product(
                name="Classic Black Pumps",
                sku="SHOES-001",
                category="Shoes",
                brand="StyleFeet",
                price=89.00,
                original_price=120.00,
                attributes={
                    "color": "Black",
                    "sizes": [6, 7, 8, 9, 10],
                    "heel_height": "3 inches",
                    "occasion": ["formal", "work", "party"]
                },
                inventory=[
                    {"location": "online", "quantity": 30},
                    {"location": "store_downtown", "quantity": 5}
                ],
                description="Timeless black pumps that complement any outfit.",
                images=["black_pumps_1.jpg"],
                views=890,
                purchases=67,
                rating=4.6
            ),
            Product(
                name="Gold Statement Necklace",
                sku="ACC-001",
                category="Accessories",
                brand="GlamAccessories",
                price=45.00,
                attributes={
                    "color": "Gold",
                    "material": "Gold-plated",
                    "occasion": ["party", "formal", "date-night"]
                },
                inventory=[
                    {"location": "online", "quantity": 100},
                    {"location": "store_downtown", "quantity": 15}
                ],
                description="Elegant gold statement necklace to elevate any outfit.",
                images=["gold_necklace_1.jpg"],
                views=450,
                purchases=34,
                rating=4.5
            )
        ]
        
        # Add to database
        db.add_all(customers)
        db.add_all(products)
        db.commit()
        
        print("✅ Sample data added successfully!")
        print(f"   • {len(customers)} customers")
        print(f"   • {len(products)} products")
        print()
        print("🎉 Database is ready for testing!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()