# Specialties Module

This module manages Desbravadores (Pathfinders) specialties and their assignment to users.

## Overview

Specialties (Especialidades) are achievements that Desbravadores members can earn. Each specialty has:
- **ID**: Unique identifier (UUID)
- **Code**: A unique code following the MD format (e.g., `EN-001`, `AR-002`)
- **Name**: The name of the specialty (e.g., "Acampamento", "Primeiros Socorros")

Specialties can be assigned to users, creating a many-to-many relationship between users and specialties.

## Database Schema

### Tables

#### `specialties`
- `id` (UUID, PK): Unique identifier
- `code` (VARCHAR(20), UNIQUE): MD code for the specialty
- `name` (VARCHAR(200)): Name of the specialty
- `created_at` (TIMESTAMP): Creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp
- `deleted_at` (TIMESTAMP): Soft delete timestamp

#### `user_specialties`
- `id` (UUID, PK): Unique identifier
- `user_id` (UUID, FK → users.id): Reference to user
- `specialty_id` (UUID, FK → specialties.id): Reference to specialty
- `created_at` (TIMESTAMP): When the specialty was assigned
- `updated_at` (TIMESTAMP): Last update timestamp
- `deleted_at` (TIMESTAMP): Soft delete timestamp
- **Unique Constraint**: (`user_id`, `specialty_id`) - A user can only have each specialty once

## API Endpoints

### Specialty Management

#### `POST /specialties`
Create a new specialty (Admin only)
```json
{
  "code": "EN-001",
  "name": "Acampamento"
}
```

#### `GET /specialties`
List all specialties with optional search and pagination (Authenticated users)

**Query Parameters:**
- `search` (optional): Search by specialty code or name (partial match)
- `page` (optional, default: 0): Page index (0-based)
- `page_size` (optional, default: 20, max: 100): Number of items per page

**Response:**
```json
{
  "status": 200,
  "message": "Specialties retrieved successfully",
  "data": {
    "items": [
      {
        "id_": "123e4567-e89b-12d3-a456-426614174000",
        "code": "EN-001",
        "name": "Acampamento",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": null,
        "deleted_at": null
      }
    ],
    "total": 150,
    "page": 0,
    "page_size": 20
  }
}
```

#### `GET /specialties/{specialty_id}`
Get a specific specialty by ID (Authenticated users)

#### `PUT /specialties/{specialty_id}`
Update a specialty (Admin only)
```json
{
  "code": "EN-002",
  "name": "Acampamento Avançado"
}
```

#### `DELETE /specialties/{specialty_id}`
Delete a specialty (Admin only)

### User Specialty Assignment

#### `POST /specialties/users/{user_id}`
Assign a specialty to a user (Admin only)
```json
{
  "specialty_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### `GET /specialties/users/{user_id}`
List all specialties for a specific user (Authenticated users)

#### `DELETE /specialties/users/{user_id}/{user_specialty_id}`
Remove a specialty from a user (Admin only)

## Module Structure

```
app/specialties/
├── __init__.py          # Module initialization
├── entities.py          # SQLAlchemy ORM models
├── schemas.py           # Pydantic schemas for validation
├── repository.py        # Database operations
├── domain.py            # Business logic (use cases)
├── routes.py            # FastAPI route definitions
└── README.md            # This file
```

## Business Rules

1. **Unique Specialty Codes**: Each specialty must have a unique code
2. **User-Specialty Relationship**: A user can only be assigned the same specialty once
3. **Cascading Deletes**: Deleting a user or specialty will remove associated user_specialty records
4. **Soft Deletes**: Records are marked as deleted rather than physically removed
5. **Search**: Supports partial matching on both code and name fields (case-insensitive)
6. **Pagination**: All list endpoints support pagination to handle large datasets efficiently

## Usage Examples

### Creating a Specialty
```python
from app.specialties.domain import CreateSpecialtyUseCase
from app.specialties.schemas import CreateSpecialtySchema

payload = CreateSpecialtySchema(
    code="EN-001",
    name="Acampamento"
)
result = await CreateSpecialtyUseCase(payload, session).execute()
```

### Searching Specialties with Pagination
```python
from app.specialties.domain import ListSpecialtiesUseCase

# Search for specialties containing "acampamento"
result = await ListSpecialtiesUseCase(
    query="acampamento",
    page=0,
    page_size=20,
    session=session
).execute()

# Returns paginated results with total count
items = result.data["items"]
total = result.data["total"]
```

### Assigning a Specialty to a User
```python
from app.specialties.domain import AssignSpecialtyToUserUseCase
from app.specialties.schemas import CreateUserSpecialtySchema

payload = CreateUserSpecialtySchema(
    specialty_id=specialty_uuid
)
result = await AssignSpecialtyToUserUseCase(user_id, payload, session).execute()
```

## Reference

Based on the official Desbravadores Specialty Manual:
https://www.adventistas.org/pt/desbravadores/manual-de-especialidades/

## Migration

Migration file: `migrations/versions/0006_created_specialties_tables.py`

To apply the migration:
```bash
alembic upgrade head
```

To rollback:
```bash
alembic downgrade -1
```
