# Projects-Core-Service

**Projects-Core-Service** is a web application created with Flask for managing users, projects and tasks.

### Requirements 📋

- Python 3.10.12. It’s recommended to use [pyenv](https://github.com/pyenv/pyenv) to easily install the desired Python version.
- A `.env` file created at the project root containing the required environment variables.
- Docker compose installed.

---

### Stack ⚙️

Main frameworks and libraries:

- Flask
- SQLAlchemy
- Pytest
- Pydantic

---

### Running the Application 💻

It’s recommended to create a virtual environment (virtualenv) to isolate the application dependencies.

On the root folder run the following command:
```jsx
python -m venv .venv
```

After the creation of the virtual environment, it should be activated with the following command:
```jsx
source .venv/bin/activate
```

With the virtual environment created and activated, run the following command to install the dependencies:
```jsx
pip install -r requirements.txt
```

Start the docker container with the following command:
```jsx
docker compose up
```

To run the application locally on http://127.0.0.1:5000/ and create the database tables automatically, run the following command in a new terminal:

```jsx
python main.py
```

To run unit tests and integration tests, run the following command on the root folder in a different terminal or with the application stopped:

```jsx
pytest
```

---

### Documentation ️📖

The documentation for the available endpoints were created using `Sphinx` and can be generated with the following commands:
```jsx
cd docs
```
```jsx
make html
```

The documentation can be viewed by opening the file `docs/build/html/index.html` with a browser.

On linux, the following command will open the documentation file automatically when executed on the `/docs` folder:
```jsx
xdg-open build/html/index.html
```
Alternatively on macOS:
```jsx
open build/html/index.html
```
And on Windows (PowerShell):
```jsx
start build\html\index.html
```

---

### Postman 🔁

The Postman project with all the endpoints of the application can be accessed with the URL:

- https://www.postman.com/bruno-9497913/projects-apis/overview

With the application running after the command `python main.py`, all the endpoints in Postman will be executed at http://127.0.0.1:5000/.

---

### Endpoints 🌐

The endpoints with the `GET` method can be executed by any user and do not require a logged user.

The endpoints with the `POST`, `PUT` and `DELETE` methods can only be executed by a user with the user type `manager`. Therefore, they require a manager to be logged in.

---

### Users 👤

A manager user is automatically created on the database when the application is started for the first time, therefore the first login can be done with the endpoint `POST /auth/login` with the following credentials:
```jsx
{
    "email": "admin@admin.com",
    "password": "admin"
}
```

With the manager user logged in, a new user can be created with the create user endpoint `POST /users/` with the following body request structure:
```jsx
{
    "email": "new_user@email.com",
    "password": "password",
    "username": "new_user",
    "name": "New User",
    "user_type": 1
}
```

After the creation of this user, the password will be safely stored in the database with encryption. Therefore, the manager user can be logged out with the endpoint `POST /auth/logout` and the new created user can perform the login to start using the application with its own user.

---

### Architecture 🗒

The architecture follows the principles of Clean Architecture, where the database and API layers are isolated from the business logic and each entity is isolated to maintain the code clear and maintainable.

Therefore, each entity has its own model, repository, resources and database table, allowing for single responsibility, easier testing and safer modifications. 

### User Type

The `user_type` table was created to ensure proper relation of user types with users, using a foreign key, and at the same time avoid redundancy.

### User 

The `user` table was created to store information about the users including name, email, username and encrypted password.

### Project

The `project` table was created to store information about the projects including name, subject, due_date and start_date. It has a foreign key with the table `user` to properly store which user created and edited every project.

### Task

The `task` table was created to store information about the tasks including name, description, due_date and start_date. It has a foreign key with the table `user` to properly store which user created and edited every task.


---

### Extra Functionality ✨

- User authentication, including login and logout endpoints, have been added due to the relation between the type of the user and the permissions of several endpoints.
- Password encryption has been added for extra security when creating a user.
