from Project.models import User
from Project.routes import generate_password_hash
from Project import db,app
import getpass

# To create Admin
def create_admin():
    app.app_context().push()
    adminname = input("Enter Admin name: ")
    email = input("Enter email address: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Enter password again: ")
    if password != confirm_password:
        print("Passwords don't match")
        return 1
    
    try:
        user = User()
        user.name = adminname
        user.email = email
        user.password = generate_password_hash(str(password))
        user.type='Admin'
        user.is_confirmed = True
                
        db.session.add(user)
        db.session.commit()
        return 0
    except:
        print("Couldn't create admin user")

create_admin()