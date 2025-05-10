
# BECHDO - Marketplace Backend API

BECHDO is a powerful marketplace platform backend built with FastAPI and MongoDB, focusing on security, scalability, and performance.

## Features

- **User Management**
  - Registration with email verification
  - JWT authentication (access and refresh tokens)
  - Password reset functionality
  - Role-based access control (basic_user, seller, admin, moderator)
  - User profile management

- **Security Features**
  - Argon2 password hashing
  - Rate limiting on sensitive endpoints
  - JWT token management with blacklisting
  - Audit logging for administrative actions

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI (async REST API)
- **Database**: MongoDB with Motor async driver
- **Queue System**: Celery with Redis broker
- **Media Storage**: AWS S3
- **Authentication**: JWT
- **Testing**: Pytest

## Getting Started

### Prerequisites

- Python 3.11+
- MongoDB
- Redis
- AWS S3 account (for media storage)

### Setup with Docker

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/bechdo.git
   cd bechdo
   ```

2. **Set environment variables**:
   Create a `.env` file with the following variables:
   ```
   JWT_SECRET=your_secure_jwt_secret
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   ```

3. **Run with docker-compose**:
   ```bash
   docker-compose up
   ```

### Setup without Docker

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/bechdo.git
   cd bechdo
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**:
   Configure environment variables for JWT secret, database connections, etc.

5. **Run MongoDB and Redis**:
   Make sure MongoDB and Redis are running on your local machine.

6. **Run the API**:
   ```bash
   uvicorn src.main:app --reload
   ```

7. **Run Celery worker**:
   ```bash
   celery -A src.celery_config worker --loglevel=info
   ```

## API Documentation

Once the server is running, access the OpenAPI documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests

```bash
pytest
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/verify-email` - Verify email address
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user
- `POST /api/v1/auth/forgot-password` - Initiate password reset
- `POST /api/v1/auth/reset-password` - Reset password with token

### User Management

- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/profile/{user_id}` - Get public user profile
- `GET /api/v1/users/avatar-upload-url` - Get presigned URL for avatar upload

### Admin Endpoints

- `GET /api/v1/users/` - List all users (admin only)
- `PATCH /api/v1/users/{user_id}` - Update user (admin only)
- `GET /api/v1/users/audit-logs` - View audit logs (admin only)

## License

MIT
