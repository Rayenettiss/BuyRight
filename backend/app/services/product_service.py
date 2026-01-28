"""
Product service - CRUD operations for products in PostgreSQL.
"""

from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.product import Product


def create_product(
    db: Session,
    title: str,
    url: str,
    description: Optional[str] = None,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    price: Optional[float] = None,
    currency: str = "TND",
    image_url: Optional[str] = None,
    stars: Optional[float] = None,
    reviews_count: Optional[int] = 0,
    source: str = "manual",
) -> Product:
    """
    Create a new product in the database.
    
    Args:
        db: Database session
        title: Product title
        url: Product URL (must be unique)
        external_id: External identifier (ASIN, eBay ID, etc.)
        description: Product description
        brand: Brand name
        category: Product category
        price: Product price
        currency: Currency code (default: TND)
        image_url: Image URL
        stars: Rating (0-5)
        reviews_count: Number of reviews
        source: Source platform (amazon, ebay, jumia, etc.)
    
    Returns:
        Created Product instance
    
    Raises:
        IntegrityError: If URL already exists
    """
    product = Product(
        title=title,
        description=description,
        brand=brand,
        category=category,
        price=price,
        currency=currency,
        url=url,
        image_url=image_url,
        stars=stars,
        reviews_count=reviews_count,
        source=source,
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product


def get_product_by_url(db: Session, url: str) -> Optional[Product]:
    """
    Get product by URL.
    
    Args:
        db: Database session
        url: Product URL
    
    Returns:
        Product instance or None if not found
    """
    return db.query(Product).filter(Product.url == url).first()


def get_product_by_id(db: Session, product_id: UUID) -> Optional[Product]:
    """
    Get product by ID.
    
    Args:
        db: Database session
        product_id: Product UUID
    
    Returns:
        Product instance or None if not found
    """
    return db.query(Product).filter(Product.id == product_id).first()


def update_product(
    db: Session,
    product_id: UUID,
    data: Dict[str, Any]
) -> Optional[Product]:
    """
    Update product fields.
    
    Args:
        db: Database session
        product_id: Product UUID
        data: Dictionary of fields to update
    
    Returns:
        Updated Product instance or None if not found
    """
    product = get_product_by_id(db, product_id)
    
    if not product:
        return None
    
    # Update allowed fields
    allowed_fields = {
        'external_id', 'title', 'description', 'brand', 'category',
        'price', 'currency', 'url', 'image_url', 'stars',
        'reviews_count', 'source', 'scraped_at', 'updated_at'
    }
    
    for key, value in data.items():
        if key in allowed_fields and hasattr(product, key):
            setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    return product