from Project import app
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")

# import os
# if (os.path.exists("./instance") is False):
#     from Project import app,db
#     app.app_context().push()
#     db.create_all()

