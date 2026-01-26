"""
Product Model - PostgreSQL
Stores product information scraped from Tunisianet
Hackathon: Source of truth for relational data, synced to Qdrant for vector search
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
import enum
from app.database import Base


class StockStatus(str, enum.Enum):
    """Product stock status"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    PREORDER = "preorder"


class Product(Base):
    """
    Product table - stores e-commerce product data.
    
    Hackathon Requirements:
    - Multimodal: text (title, description, features) + image_url
    - Financial: price, payment_options, installment_terms, cashback
    - Quality: rating, review_count, durability_score, resale_value
    - Embeddings stored in Qdrant, metadata here
    """
    __tablename__ = "products"
    
    # Primary Key
    product_id = Column(String(36), primary_key=True, index=True)
    
    # Basic Information
    title = Column(String(500), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False, index=True)
    
    # Categorization (for filtering)
    category = Column(String(100), index=True)  # "Electronics", "Computing", etc.
    subcategory = Column(String(100))  # "Laptops", "Gaming Consoles", etc.
    
    # Product Details
    specs = Column(JSON)  # {"RAM": "16GB", "Storage": "512GB SSD", "CPU": "Intel i7"}
    features = Column(ARRAY(String))  # ["Backlit keyboard", "Thunderbolt 4", "Wi-Fi 6"]
    
    # Social Proof & Quality
    rating = Column(Float)  # 0-5 stars
    review_count = Column(Integer, default=0)
    
    # Visual
    image_url = Column(Text)  # URL to product image
    
    # Financial Options (Hackathon: Payment preferences)
    payment_options = Column(ARRAY(String))  # ["credit_card", "installment", "cash"]
    installment_terms = Column(JSON)  # {"3_months": 0, "6_months": 0, "12_months": 5.5}
    cashback_percentage = Column(Float, default=0.0)  # 2.5 = 2.5% cashback
    
    # Availability
    stock_status = Column(SQLEnum(StockStatus), default=StockStatus.IN_STOCK)
    
    # Durability & Value (Hackathon: Cost-per-use scenario)
    durability_score = Column(Float)  # 0-10, estimated product lifespan
    resale_value = Column(Float)  # Estimated resale value percentage (e.g., 60.0 = 60%)
    
    # Embeddings Metadata (actual vectors in Qdrant)
    text_embedding_version = Column(String(50))  # "text-embedding-004"
    image_embedding_version = Column(String(50))  # "multimodalembedding@001"
    embeddings_last_updated = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product(product_id={self.product_id}, title={self.title[:30]})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "product_id": self.product_id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "subcategory": self.subcategory,
            "specs": self.specs,
            "features": self.features,
            "rating": self.rating,
            "review_count": self.review_count,
            "image_url": self.image_url,
            "payment_options": self.payment_options,
            "installment_terms": self.installment_terms,
            "cashback_percentage": self.cashback_percentage,
            "stock_status": self.stock_status.value if self.stock_status else None,
            "durability_score": self.durability_score,
            "resale_value": self.resale_value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def calculate_true_cost(self, installment_months: int = None) -> float:
        """
        Calculate true cost including interest if using installments.
        
        Hackathon: Affordability - show true cost with interest
        """
        if not installment_months or not self.installment_terms:
            return self.price
        
        interest_rate = self.installment_terms.get(f"{installment_months}_months", 0)
        true_cost = self.price * (1 + interest_rate / 100)
        return round(true_cost, 2)
    
    def get_monthly_payment(self, installment_months: int) -> float:
        """Calculate monthly payment for installment plan"""
        if not installment_months:
            return self.price
        
        true_cost = self.calculate_true_cost(installment_months)
        return round(true_cost / installment_months, 2)