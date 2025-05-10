
# BECHDO - Marketplace Backend API

BECHDO is a powerful marketplace platform built with FastAPI and MongoDB, focusing on security, scalability, and performance.

## Project Structure

The project is organized into two main directories:

- `client/`: Frontend application (React)
- `server/`: Backend API (FastAPI)

## Features

- **User Management**
  - Registration with email verification
  - JWT authentication (access and refresh tokens)
  - Password reset functionality
  - Role-based access control (basic_user, seller, admin, moderator)
  - User profile management

- **Storage Options**
  - AWS S3 for production
  - Local file storage for development
  - Configurable via environment variables

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
- **Media Storage**: AWS S3 or Local Storage
- **Authentication**: JWT
- **Testing**: Pytest
- **Frontend**: React (client folder)

## Getting Started

### Prerequisites

- Python 3.11+
- MongoDB
- Redis
- (Optional) AWS S3 account for production media storage

### Setup with Docker

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/bechdo.git
   cd bechdo
   ```

2. **Set environment variables**:
   Copy the example env file and update values:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run with docker-compose**:
   ```bash
   docker-compose up
   ```

4. **Access the application**:
   - Frontend: http://localhost:80
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

### Setup without Docker

#### Backend Setup

1. **Navigate to server directory**:
   ```bash
   cd server
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

#### Frontend Setup

1. **Navigate to client directory**:
   ```bash
   cd client
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

## API Documentation

Once the server is running, access the OpenAPI documentation:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Storage Configuration

BECHDO supports two storage modes:

1. **AWS S3 (default in production)**
   - Set `STORAGE_MODE=s3` in your .env file
   - Configure AWS credentials:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`
     - `S3_BUCKET_NAME`

2. **Local Storage (for development)**
   - Set `STORAGE_MODE=local` in your .env file
   - Files will be saved to `LOCAL_STORAGE_PATH` (default: ./local_storage)
   - Access files via API endpoints

## Running Tests

```bash
cd server
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

### Storage

- `POST /api/v1/storage/local-upload/{file_path}` - Upload file to local storage (dev mode)
- `GET /api/v1/storage/files/{file_path}` - Get file from local storage (dev mode)

### Admin Endpoints

- `GET /api/v1/users/` - List all users (admin only)
- `PATCH /api/v1/users/{user_id}` - Update user (admin only)
- `GET /api/v1/users/audit-logs` - View audit logs (admin only)

## License

MIT
