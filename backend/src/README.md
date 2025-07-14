# Clean Architecture - Port-Adapters Pattern

This project follows the Clean Architecture principles with a Port-Adapters (Hexagonal) architecture pattern.

## Directory Structure

```
src/
├── domain/          # Core business logic and entities
├── application/     # Use cases and application services
└── adapters/        # External interfaces
    ├── inbound/     # Inbound adapters (receive requests from outside)
    └── outbound/    # Outbound adapters (make calls to external systems)
```

## Layer Descriptions

### Domain Layer
- Contains core business entities, value objects, and domain services
- No dependencies on external frameworks or infrastructure
- Pure business logic

### Application Layer
- Contains use cases and application services
- Orchestrates domain objects to fulfill business requirements
- Defines ports (interfaces) for external dependencies

### Adapters Layer

#### Inbound Adapters (Driving Adapters)
- Web controllers (FastAPI endpoints)
- CLI interfaces
- Event handlers
- Message queue consumers

#### Outbound Adapters (Driven Adapters)
- Database implementations
- External API clients
- File system operations
- Message queue producers

## Dependency Flow

Dependencies flow inward: Adapters → Application → Domain

- Domain layer has no external dependencies
- Application layer depends only on Domain
- Adapters depend on Application and Domain layers 