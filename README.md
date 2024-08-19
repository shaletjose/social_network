# Social Networking API

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run migrations:
    ```bash
    python manage.py migrate
    ```

4. Start the development server:
    ```bash
    python manage.py runserver
    ```

## Docker

1. Build and run the Docker container:
    ```bash
    docker-compose up --build
    ```

## API Endpoints

- **Signup**: `POST /api/users/signup/`
- **Login**: `POST /api/users/login/`
- **Search Users**: `GET /api/users/search/`
- **Send Friend Request**: `POST /api/users/friend-request/send/`
- **Respond to Friend Request**: `POST /api/users/friend-request/respond/`
- **List Friends**: `GET /api/users/friends//`
- **Search Users**: `GET /api/users/search/`
- **List Pending Requests**: `GET /api/users/pending-requests/`

