# FindLessons

This is a Django project developed for the final test of the Web Technologies course.

## Abstract

FindLessons is a web app designed to facilitate the search and booking of private lessons.  
Students can search for teachers in their city, view their availability, book lessons, and communicate directly with the teachers via a chat feature.  
Teachers can promote their services by registering on the platform, managing their availability, and organizing lessons through the app.

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

# Testing
To run the tests for the _chat_ application, use the command:  
   ```bash
   python manage.py test
   ```

# Attributions
Icons used in this project are provided by Freepik via Flaticon:  
<a href="https://www.flaticon.com/free-icons/school" title="school icons">School icons created by Freepik - Flaticon</a>
