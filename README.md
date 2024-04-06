# Project ZetaX

Online C Programme Evaluation Software

For the first time when we are starting the host machine to lauch the
website on a local network, we have to ensure that the database tables
are created which needs to be done manually through python interpreter.

Run the following commands in the python shell:

> > > from Project import app,db app.app_context().push()
> > > db.create_all()

For running the app, just run the app.py file
