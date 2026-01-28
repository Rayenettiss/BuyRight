"""
Verify database tables and schema.
Run: python verify_db.py
"""

from sqlalchemy import inspect, text
from app.dependencies import engine

def verify_database():
    """Check database tables and users table schema."""
    
    inspector = inspect(engine)
    
    # Get all tables
    print("=" * 60)
    print("DATABASE TABLES")
    print("=" * 60)
    tables = inspector.get_table_names()
    for table in tables:
        print(f"✅ {table}")
    print()
    
    # Check if users table exists
    if 'users' in tables:
        print("=" * 60)
        print("USERS TABLE SCHEMA")
        print("=" * 60)
        columns = inspector.get_columns('users')
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"  {col['name']:<20} {str(col['type']):<20} {nullable}")
        print()
        
        # Get indexes
        print("INDEXES:")
        indexes = inspector.get_indexes('users')
        for idx in indexes:
            print(f"  {idx['name']}: {idx['column_names']}")
        print()
    
    # Test a simple query
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"✅ Connection successful!")
            print(f"✅ Users table exists with {count} rows")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_database()