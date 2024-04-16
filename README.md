# Project ZetaX

<h1 align="center">
  <img src="Project-ZetaX.png">
  <br>
  Project ZetaX: Online Judge
</h1>

Introduction
--------------
Project ZetaX is an online C Programme Judging and Evaluation Software.

This Online Judge System aims to provide a platform-independent environment for evaluating C programs based on time complexity, space complexity, and adherence to given specifications. It will facilitate competitive programming, training, and learning of programming concepts such as algorithms and data structures. Additionally, the system will overcome challenges related to handling errors, memory usage, and integration with an online Integrated Development Environment (IDE).

Running the App
----------------
To run the app in your local environment::

        1. Clone the repository::

              git clone https://github.com/laksh0820/Project-ZetaX.git
              cd Project-ZetaX

        2. Create and activate a virtual environment::

              python3 venv -m env
              source ./env/bin/activate

        3. Install requirements::

              pip install -r requirements.txt

        4. Create Database Tables and Admin::

              python3 create_admin.py

        5. Run the application::

              python3 app.py

> [!NOTE]
>  Make sure that all the environment variable are listed in the .env file and 
   run "source .env" on the bash shell to ensure all the environment variable are defined. 

> [!NOTE]
>  Host machine should be running UNIX OS as the commands used for running the C files
   are compatible only with UNIX bash shell.

3rd Party Stuff
----------------
This Online Judge system is built with the help of [Bootstrap](http://getbootstrap.com/)  and  [Ace Editor](https://ace.c9.io/).
