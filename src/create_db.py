from server import db, database

# Drop all of the existing database tables
# print("db.drop_all()")
# db.drop_all()

# Create the database and the database table
print("db.create_all()")
db.create_all()

#init DiscountCodes
code = database.models.DiscountCode(code="CASHBACK30", discount=20, active=True)
db.session.add(code)
db.session.commit()