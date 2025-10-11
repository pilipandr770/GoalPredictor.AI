"""
Create test Premium user for development
"""
from app import create_app
from extensions import db
from models import User
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Check if user exists
    test_user = User.query.filter_by(email='test@premium.com').first()
    
    if test_user:
        print("✓ Test Premium user already exists")
        print(f"  Email: test@premium.com")
        print(f"  Username: {test_user.username}")
        print(f"  Premium: {test_user.is_premium}")
    else:
        # Create new Premium user
        test_user = User(
            email='test@premium.com',
            username='TestPremium',
            is_premium=True,
            subscription_end=datetime.utcnow() + timedelta(days=365),
            created_at=datetime.utcnow()
        )
        test_user.set_password('premium123')  # Simple password for testing
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Test Premium user created successfully!")
        print(f"  Email: test@premium.com")
        print(f"  Password: premium123")
        print(f"  Username: {test_user.username}")
        print(f"  Premium: {test_user.is_premium}")
        print(f"  Subscription until: {test_user.subscription_end}")
    
    print("\n🎾 Now you can test Tennis predictions:")
    print("  1. Login at http://localhost:5000")
    print("  2. Go to http://localhost:5000/tennis")
    print("  3. Click 'Prognose anzeigen' on any match")
