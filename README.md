# Project ZetaX

Project ZetaX is an online C Programme Evaluation Software

Firstly, We are required to install all the dependencies using the following command:

pip install -r requirements.txt

For the first time when we are starting the host machine to launch the
website on a local network, we have to ensure that the database tables
are created.Also, We are required to create an admin for the website.

Run the following commands in the bash shell for creating an admin as well as databases:

python3 create_admin.py

For running the app, just run the app.py file

NOTE 1: Make sure that all the environment variable are listed in the .env file and 
      run "source .env" on the bash shell to ensure all the environment variable are
      defined. 

NOTE 2: Host machine should be running UNIX OS as the commands used for running the C files
are compatible only with UNIX bash shell.
