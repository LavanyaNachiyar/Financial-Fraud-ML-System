from app import app, db, Transaction
import sys

print("=" * 60)
print("Database Migration - Adding Transaction History")
print("=" * 60)

try:
    with app.app_context():
        # Create all tables (will only create new ones)
        db.create_all()
        print("\n✅ Transaction table created successfully!")
        print("\nNew features added:")
        print("  - Transaction history storage")
        print("  - Analytics dashboard")
        print("  - CSV export")
        print("\nAccess at:")
        print("  - Analytics: http://localhost:5000/analytics")
        print("  - Transactions: http://localhost:5000/transactions")
        print("  - Export CSV: http://localhost:5000/export-csv")
        print("\n" + "=" * 60)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
