To run the project, make sure that React and Django are installed. 
Then open a terminal or command prompt. Move to the directory 'erisa_recovery' of this project. 
Run the following command 
python manage.py runserver 
The frontend server will start running on the host http://127.0.0.1:8000/
In a new terminal window, run the following command
python manage.py import_claims
This will start the backend server and load the claims in the SQL database if not already present, otherwise it will delete the old claims and then load the new.
A patient can be searched using their name, using the available filter, and the view tab will display the details of the patient from the backend server, and it also contains an option to flag or unflag the patient.
