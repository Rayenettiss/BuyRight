import pandas as pd
import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
from app.models.product import NormalizedProduct, ProductChunk
from chonkie import SentenceChunker
from config.settings import get_settings
import logging
import re
import base64
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)
settings = get_settings()


# Column mapping for normalization (supports Amazon, eBay, and other formats)
COLUMN_MAPPINGS = {
    'title': ['title', 'product_name', 'name', 'product_title', 'titre', 'nom'],
    'description': ['description', 'desc', 'product_description', 'details', 'about', 'category'],
    'price': ['price', 'prix', 'cost', 'amount', 'product_price'],
    'currency': ['currency', 'devise', 'curr'],
    'url': ['url', 'link', 'product_url', 'product_link', 'lien'],
    'image_url': ['image_url', 'image', 'img_url', 'picture', 'photo', 'image_link', 'imageurl'],
    'id': ['id', 'product_id', 'item_id', 'sku', 'asin'],
    'brand': ['brand', 'marque', 'manufacturer'],
    'stars': ['stars', 'rating', 'note'],
    'reviews_count': ['reviewscount', 'reviews_count', 'reviews', 'nb_reviews']
}


def normalize_column_name(columns: List[str], target: str) -> Optional[str]:
    """Find the matching column name for a target field"""
    possible_names = COLUMN_MAPPINGS.get(target, [])
    columns_lower = [col.lower() for col in columns]
    
    for possible in possible_names:
        if possible in columns_lower:
            return columns[columns_lower.index(possible)]
    
    return None


def extract_source_from_filename(filename: str) -> str:
    """Extract source identifier from filename"""
    filename_lower = filename.lower()
    
    if 'ebay' in filename_lower:
        return 'ebay'
    elif 'amazon' in filename_lower:
        return 'amazon'
    elif 'avare' in filename_lower or 'lavare' in filename_lower:
        return 'lavare'
    else:
        # Use filename without extension as source
        return filename.rsplit('.', 1)[0]


def normalize_price(price_str: Any) -> Optional[float]:
    """Normalize price string to float"""
    if pd.isna(price_str):
        return None
    
    try:
        # Convert to string if not already
        price_str = str(price_str)
        
        # Remove currency symbols and whitespace
        price_str = re.sub(r'[$€£¥,\s]', '', price_str)
        
        # Convert to float
        return float(price_str)
    except (ValueError, AttributeError):
        return None


def normalize_csv_data(df: pd.DataFrame, source: str) -> List[NormalizedProduct]:
    """Normalize CSV/XLSX data to standard schema"""
    normalized_products = []
    
    columns = df.columns.tolist()
    
    # Find matching columns
    title_col = normalize_column_name(columns, 'title')
    desc_col = normalize_column_name(columns, 'description')
    price_col = normalize_column_name(columns, 'price')
    currency_col = normalize_column_name(columns, 'currency')
    url_col = normalize_column_name(columns, 'url')
    image_col = normalize_column_name(columns, 'image_url')
    id_col = normalize_column_name(columns, 'id')
    brand_col = normalize_column_name(columns, 'brand')
    stars_col = normalize_column_name(columns, 'stars')
    reviews_col = normalize_column_name(columns, 'reviews_count')
    category_col = normalize_column_name(columns, 'description')  # category maps to description
    
    for idx, row in df.iterrows():
        try:
            # Build description from category if no explicit description
            description_text = None
            if desc_col and pd.notna(row.get(desc_col)):
                description_text = str(row[desc_col])
            elif category_col and pd.notna(row.get(category_col)):
                description_text = str(row[category_col])
            
            # Parse currency
            currency_value = "USD"
            if currency_col and pd.notna(row.get(currency_col)):
                curr = str(row[currency_col]).strip()
                if curr == "$":
                    currency_value = "USD"
                elif curr == "€":
                    currency_value = "EUR"
                elif curr == "£":
                    currency_value = "GBP"
                else:
                    currency_value = curr
            
            # Parse stars (rating)
            stars_value = None
            if stars_col and pd.notna(row.get(stars_col)):
                try:
                    stars_value = float(row[stars_col])
                except (ValueError, TypeError):
                    pass
            
            # Parse reviews count
            reviews_value = None
            if reviews_col and pd.notna(row.get(reviews_col)):
                try:
                    reviews_value = int(row[reviews_col])
                except (ValueError, TypeError):
                    pass
            
            product = NormalizedProduct(
                title=str(row[title_col]) if title_col and pd.notna(row.get(title_col)) else None,
                description=description_text,
                price=normalize_price(row[price_col]) if price_col else None,
                currency=currency_value,
                url=str(row[url_col]) if url_col and pd.notna(row.get(url_col)) else None,
                image_url=str(row[image_col]) if image_col and pd.notna(row.get(image_col)) else None,
                source=source,
                original_id=str(row[id_col]) if id_col and pd.notna(row.get(id_col)) else str(idx),
                brand=str(row[brand_col]) if brand_col and pd.notna(row.get(brand_col)) else None,
                stars=stars_value,
                reviews_count=reviews_value,
                category=str(row[category_col]) if category_col and pd.notna(row.get(category_col)) else None
            )
            normalized_products.append(product)
        except Exception as e:
            logger.warning(f"Error normalizing row {idx}: {e}")
            continue
    
    return normalized_products


def chunk_product_text(product: NormalizedProduct, product_id: str) -> List[ProductChunk]:
    """Chunk product text using chonkie library"""
    # Combine title, brand, category, and description for richer embeddings
    text_parts = []
    if product.title:
        text_parts.append(f"Title: {product.title}")
    if product.brand:
        text_parts.append(f"Brand: {product.brand}")
    if product.category:
        text_parts.append(f"Category: {product.category}")
    if product.description:
        text_parts.append(f"Description: {product.description}")
    if product.stars:
        text_parts.append(f"Rating: {product.stars} stars")
    if product.reviews_count:
        text_parts.append(f"Reviews: {product.reviews_count}")
    
    full_text = "\n\n".join(text_parts)
    
    if not full_text.strip():
        return []
    
    # Initialize chonkie SentenceChunker with appropriate size
    # SentenceChunker respects sentence boundaries for better semantic coherence
    chunker = SentenceChunker(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    # Use chonkie to chunk the text
    # Returns a list of Chunk objects with .text attribute
    chunks = chunker(full_text)
    
    # Create ProductChunk objects from chonkie chunks
    product_chunks = []
    for i, chunk in enumerate(chunks):
        # chonkie Chunk objects have a .text attribute
        chunk_text = chunk.text if hasattr(chunk, 'text') else str(chunk)
        
        product_chunk = ProductChunk(
            product_id=product_id,
            chunk_index=i,
            text_content=chunk_text,
            title=product.title,
            price=product.price,
            currency=product.currency,
            url=product.url,
            image_url=product.image_url,
            source=product.source,
            original_id=product.original_id,
            brand=product.brand,
            stars=product.stars,
            reviews_count=product.reviews_count,
            category=product.category
        )
        product_chunks.append(product_chunk)
    
    return product_chunks if product_chunks else []


async def download_image(url: str, session: aiohttp.ClientSession) -> Optional[bytes]:
    """Download image from URL and return bytes"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'image' in content_type:
                    image_bytes = await response.read()
                    
                    # Validate it's a valid image and resize if needed
                    try:
                        img = Image.open(BytesIO(image_bytes))
                        
                        # Resize if too large (max 1024x1024 for Vertex AI)
                        max_size = 1024
                        if img.width > max_size or img.height > max_size:
                            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                            
                            # Convert back to bytes
                            output = BytesIO()
                            img_format = img.format if img.format else 'JPEG'
                            img.save(output, format=img_format)
                            image_bytes = output.getvalue()
                        
                        return image_bytes
                    except Exception as e:
                        logger.warning(f"Invalid image from {url}: {e}")
                        return None
                else:
                    logger.warning(f"URL does not point to an image: {url}")
                    return None
            else:
                logger.warning(f"Failed to download image from {url}: {response.status}")
                return None
    except asyncio.TimeoutError:
        logger.warning(f"Timeout downloading image from {url}")
        return None
    except Exception as e:
        logger.warning(f"Error downloading image from {url}: {e}")
        return None


async def download_images_batch(urls: List[str]) -> Dict[str, Optional[bytes]]:
    """Download multiple images concurrently"""
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(url, session) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map URLs to results
        return {
            url: result if isinstance(result, bytes) else None 
            for url, result in zip(urls, results)
        }