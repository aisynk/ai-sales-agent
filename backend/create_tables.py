# backend/create_tables.py
from database import engine, Base
from models.models import Customer, Product, ChatSession

def create_all_tables():
    """
    Create all database tables defined in our models
    """
    print("🗄️  Creating database tables...")
    print(f"📂 Database location: ai_sales_agent.db")
    print()
    
    # This creates all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully!")
    print()
    print("📋 Tables created:")
    print("   • customers          - Customer profiles and preferences")
    print("   • products           - Product catalog")
    print("   • chat_sessions      - Conversation history and context")
    print()
    print("🎉 Database is ready to use!")
    
    return True

if __name__ == "__main__":
    create_all_tables()