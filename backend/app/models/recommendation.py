"""
Recommendation and Payment Method Models - PostgreSQL
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from app.database import Base


class Recommendation(Base):
    """
    Recommendation table - stores recommendation history with explanations.
    
    Hackathon Requirements:
    - Traceability: score, explanation for each recommendation
    - Feedback loop: track clicks for refinement
    """
    __tablename__ = "recommendations"
    
    # Primary Key
    rec_id = Column(String(36), primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.product_id"), nullable=False, index=True)
    
    # Recommendation Metadata
    score = Column(Float, nullable=False)  # Similarity score from Qdrant
    explanation = Column(Text)  # Why this product was recommended
    
    # Ranking Factors (for explainability)
    ranking_factors = Column(JSON)  # {"similarity": 0.89, "price_match": 0.95, "budget_fit": 1.0}
    
    # Feedback Loop
    clicked = Column(Boolean, default=False)
    purchased = Column(Boolean, default=False)
    
    # Context at time of recommendation
    query_context = Column(JSON)  # Store original query, filters, user state
    
    # Metadata
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<Recommendation(rec_id={self.rec_id}, score={self.score})>"
    
    def to_dict(self):
        return {
            "rec_id": self.rec_id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "score": self.score,
            "explanation": self.explanation,
            "ranking_factors": self.ranking_factors,
            "clicked": self.clicked,
            "purchased": self.purchased,
            "date": self.date.isoformat()
        }


class PaymentMethod(Base):
    """
    Payment Method table - stores user payment options.
    
    Hackathon Requirements:
    - Encrypted: credit limit, account numbers
    - Used for affordability calculations and installment matching
    """
    __tablename__ = "payment_methods"
    
    # Primary Key
    method_id = Column(String(36), primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    
    # Payment Method Details
    type = Column(String(50), nullable=False)  # "credit_card", "debit_card", "cash"
    
    # Encrypted Financial Data (Hackathon: Security/Privacy)
    limit_encrypted = Column(Text)  # Encrypted credit limit
    interest_rate = Column(Float)  # Annual interest rate for credit
    
    # Preferences
    preferred_for_installments = Column(Boolean, default=False)
    cashback_eligible = Column(Boolean, default=False)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PaymentMethod(method_id={self.method_id}, type={self.type})>"
    
    def to_dict(self):
        return {
            "method_id": self.method_id,
            "user_id": self.user_id,
            "type": self.type,
            "interest_rate": self.interest_rate,
            "preferred_for_installments": self.preferred_for_installments,
            "cashback_eligible": self.cashback_eligible,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }


class Transaction(Base):
    """
    Transaction table - stores purchase history.
    Used for budget tracking and preference learning.
    """
    __tablename__ = "transactions"
    
    # Primary Key
    transaction_id = Column(String(36), primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.product_id"), nullable=False)
    
    # Transaction Details
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    
    # Status
    status = Column(String(50), default="completed")  # "completed", "pending", "refunded"
    
    # Metadata
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<Transaction(transaction_id={self.transaction_id}, amount={self.amount})>"
    
    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "status": self.status,
            "date": self.date.isoformat()
        }