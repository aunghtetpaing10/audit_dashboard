# Transaction Audit Dashboard

A Django-based transaction monitoring and audit system with real-time updates, interactive visualizations, and role-based access control.

## Features

- 🔒 **Secure Authentication**
  - JWT-based authentication
  - Role-based access control (Admin/Regular users)
  - Automatic token refresh

- 📊 **Interactive Dashboard**
  - Real-time transaction monitoring
  - Status distribution visualization
  - Top merchants analysis
  - Dynamic filtering and search

- 🔄 **Real-time Updates**
  - HTMX-powered live updates
  - Optimistic UI updates
  - Smooth animations

- 👥 **Role-Based Actions**
  - Admin-only transaction approval
  - Universal transaction flagging
  - Audit trail with historical records

## Tech Stack

- **Backend**: Django + Django REST Framework
- **Frontend**: TailwindCSS + HTMX
- **Database**: PostgreSQL
- **Visualization**: Plotly.js
- **Containerization**: Docker

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- PostgreSQL 13+

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd audit_dashboard
```

2. Create a `.env` file in the root directory:
```env
DEBUG=1
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@db:5432/audit_dashboard
DJANGO_SETTINGS_MODULE=transaction_audit.settings
```

3. Build and start the containers:
```bash
docker-compose up --build
```

4. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

5. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

### Development Setup

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
python manage.py runserver
```

## Key Technical Decisions

### Database Design

1. **Indexing Strategy**
   - Composite index on `status` and `merchant` for efficient filtering
   - B-tree index on `timestamp` for chronological queries
   - Index on `merchant` for text search operations

2. **Historical Records**
   - Using `django-simple-history` for audit trail
   - Tracks all changes to transactions
   - Maintains who made changes and when

### Security Implementation

1. **Authentication**
   - JWT-based authentication for API security
   - Token refresh mechanism to maintain sessions
   - Secure token storage in session

2. **Authorization**
   - Role-based access control using Django's permissions
   - Admin-only approval functionality
   - Universal flagging capability

### Performance Optimizations

1. **Query Optimization**
   - Efficient aggregation queries for analytics
   - Selective field loading
   - Optimized database indexes

2. **Frontend Performance**
   - Debounced search inputs
   - Optimistic UI updates
   - Efficient chart rendering

### Real-time Updates

1. **HTMX Integration**
   - Partial page updates for better performance
   - Real-time transaction status updates
   - Smooth transitions and animations

2. **Transaction Processing**
   - Atomic operations for status updates
   - Optimistic locking for concurrent modifications
   - Validation before state changes

## API Endpoints

### Transaction Management
- `GET /api/transactions/` - List transactions
- `PUT /api/transactions/{id}/approve/` - Approve transaction (Admin only)
- `PUT /api/transactions/{id}/flag/` - Flag transaction
- `GET /api/transactions/{id}/history/` - Get transaction history

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
