# FindLessons

This is a Django project developed for the final test of the Web Technologies course.

## Abstract

FindLessons is a web app designed to facilitate the search and booking of private lessons.  
Students can search for teachers in their city, view their availability, book lessons, and communicate directly with the teachers via a chat feature.  
Teachers can promote their services by registering on the platform, managing their availability, and organizing lessons through the app.

## Create and Set Up `.env` file

To enable the teacher registration feature, follow the steps below to create and set up a `.env` file.

1. Create the `.env` file in the root directory of yor project.

2. Generate an encryption key:

   ```bash
   from cryptography.fernet import Fernet

   # Generate a key
   key = Fernet.generate_key()
   # Print or save the key
   print(key.decode())
   ```
   
3. Choose an email address and generate an application-specific password (if using a service like Gmail, generate this through your account's security settings).

4. Set up the `.env` file with the following details:

   ```bash
   ENCRYPTION_KEY="your_generated_fernet_key"

   EMAIL_HOST = "smtp.gmail.com"
   EMAIL_PORT = 587
   EMAIL_HOST_USER = "your_email_address"
   EMAIL_HOST_PASSWORD = "your_generated_application_password"
   EMAIL_USE_TLS = True
   ADMIN_USER_EMAIL=""
   ```
Make sure to replace `your_generated_fernet_key`, `your_email_address`, and `your_generated_application_password` with the actual values you've generated.

## Startup

To start the project:

1. Install all dependencies and open the virtual environment shell by running:
   ```bash
   pipenv shell
    ```
2. Set up the initial database by executing:
   ```bash
   python manage.py init_db
    ```

3. Prepare the static files with:  
   ```bash
   python manage.py collectstatic
    ```

4. Start the server using:  
   ```bash
   daphne -p 8000 findLessons.asgi:application
    ```
  
5. To login as _admin_ use the password _techweb_.

## Testing
To run the tests for the _chat_ application, use the command:  
   ```bash
   python manage.py test
   ```


# Attributions
Icons used in this project are provided by Freepik via Flaticon:  
<a href="https://www.flaticon.com/free-icons/school" title="school icons">School icons created by Freepik - Flaticon</a>
