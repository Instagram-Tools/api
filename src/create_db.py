from server import db, database

# Drop all of the existing database tables
# print("db.drop_all()")
# db.drop_all()

# Create the database and the database table
print("db.create_all()")
db.create_all()

def init_discount_codes():
    try:
        code = database.models.DiscountCode(code="CASHBACK30", discount=20, active=True)
        db.session.add(code)
        db.session.commit()
    except Exception as exc:
        print("Exception while init_discount_codes():")
        print(exc)

init_discount_codes()