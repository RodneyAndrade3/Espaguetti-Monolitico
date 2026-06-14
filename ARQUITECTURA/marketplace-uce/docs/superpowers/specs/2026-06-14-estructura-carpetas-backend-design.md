# Diseño: Estructura de Carpetas y Módulos del Backend
## Marketplace Inteligente Universitario — UCE

**Fecha:** 2026-06-14
**Autor:** Rodney Andrade
**Estado:** Aprobado
**Repositorio:** https://github.com/RodneyAndrade3/MarketPlace-UCE.git

---

## 1. Contexto y decisiones de diseño

### Decisiones tomadas

| Decisión | Elección | Razón |
|----------|----------|-------|
| Separación de capas Maven | Paquetes dentro de un único módulo por BC | Suficiente para monolito modular académico; evita ~24 pom.xml |
| Módulo orquestador | `bootstrap/` | Nombre semántico — composition root de la arquitectura hexagonal |
| Organización del monorepo | `backend/` + `frontend-web/` + `frontend-mobile/` en misma raíz | Un solo repo para facilitar revisión académica y `docker-compose` unificado |
| Paquete base Java | `uce.edu.ec.marketplace` | Convención de dominio invertido de la UCE |
| Bloques tácticos DDD | Carpetas separadas por tipo (`aggregate/`, `entity/`, `valueobject/`, `enums/`, `event/`, `exception/`) | Visibilidad inmediata del tipo de bloque táctico de cada clase |

---

## 2. Estructura del monorepo

```
marketplace-uce/
├── backend/                    ← Maven multi-módulo (Spring Boot 3.x, Java 21)
├── frontend-web/               ← React.js SPA (scaffold vacío por ahora)
├── frontend-mobile/            ← React Native / Flutter (scaffold vacío por ahora)
├── docker-compose.yml          ← levanta backend + PostgreSQL
├── .env.example                ← plantilla de variables de entorno
├── .gitignore
└── README.md
```

---

## 3. Módulos Maven del backend

```
backend/
├── pom.xml                     ← parent POM
├── shared-kernel/
├── identity/
├── catalog/
├── trade/
├── reputation/
├── messaging/
├── fraud-detection/
├── recommendation/
├── notifications/
└── bootstrap/
```

### Grafo de dependencias Maven

```
shared-kernel   ←── todos los módulos BC
catalog         ←── fraud-detection  (implementa FraudAnalysisPort de Catalog)
catalog         ←── trade            (consume ListingId y tipos de Catalog)
todos los BC    ←── bootstrap        (composition root)
```

**Regla:** ningún BC importa clases internas de otro BC — solo tipos del `shared-kernel`.

---

## 4. Estructura interna de cada Bounded Context

Patrón hexagonal uniforme para todos los BCs. Ejemplo con `catalog`:

```
catalog/
├── pom.xml
└── src/
    ├── main/java/uce/edu/ec/marketplace/catalog/
    │   ├── domain/                            ← CERO dependencias de framework
    │   │   ├── aggregate/
    │   │   │   └── Listing.java
    │   │   ├── entity/
    │   │   │   └── Category.java
    │   │   ├── valueobject/
    │   │   │   ├── ListingDetails.java        ← sealed interface
    │   │   │   ├── ProductDetails.java        ← record
    │   │   │   ├── ServiceDetails.java        ← record
    │   │   │   ├── TradeDetails.java          ← record
    │   │   │   ├── CategoryId.java            ← record
    │   │   │   ├── ImageRef.java              ← record
    │   │   │   └── TradeItemDescription.java  ← record
    │   │   ├── enums/
    │   │   │   ├── ListingStatus.java
    │   │   │   ├── ListingType.java
    │   │   │   └── ItemCondition.java
    │   │   ├── event/
    │   │   │   ├── ListingDrafted.java
    │   │   │   ├── ListingSubmittedForReview.java
    │   │   │   ├── ListingPublished.java
    │   │   │   ├── ListingUpdated.java
    │   │   │   ├── ListingPaused.java
    │   │   │   ├── ListingReserved.java
    │   │   │   ├── ListingCompleted.java
    │   │   │   ├── ListingRemoved.java
    │   │   │   └── ListingSuspended.java
    │   │   ├── service/                       ← Domain Services (vacío en MVP)
    │   │   └── exception/
    │   │       ├── ListingNotFoundException.java
    │   │       └── InvalidListingTransitionException.java
    │   │
    │   ├── application/
    │   │   ├── port/
    │   │   │   ├── in/                        ← Puertos de entrada (interfaces)
    │   │   │   │   ├── CreateListingUseCase.java
    │   │   │   │   ├── SubmitListingForReviewUseCase.java
    │   │   │   │   ├── PublishListingUseCase.java
    │   │   │   │   ├── UpdateListingUseCase.java
    │   │   │   │   ├── PauseListingUseCase.java
    │   │   │   │   ├── ResumeListingUseCase.java
    │   │   │   │   ├── RemoveListingUseCase.java
    │   │   │   │   ├── GetListingUseCase.java
    │   │   │   │   └── SearchListingsUseCase.java
    │   │   │   └── out/                       ← Puertos de salida (interfaces)
    │   │   │       ├── ListingRepositoryPort.java
    │   │   │       ├── CategoryRepositoryPort.java
    │   │   │       ├── FraudAnalysisPort.java
    │   │   │       └── DomainEventPublisherPort.java
    │   │   ├── service/                       ← Implementan puertos de entrada
    │   │   │   ├── CreateListingService.java
    │   │   │   ├── SubmitListingForReviewService.java
    │   │   │   └── ...
    │   │   └── dto/
    │   │       ├── command/
    │   │       │   ├── CreateListingCommand.java
    │   │       │   └── UpdateListingCommand.java
    │   │       └── query/
    │   │           └── ListingSearchQuery.java
    │   │
    │   └── infrastructure/
    │       └── adapter/
    │           ├── in/
    │           │   ├── rest/
    │           │   │   ├── ListingController.java
    │           │   │   └── dto/
    │           │   │       ├── CreateListingRequest.java
    │           │   │       ├── UpdateListingRequest.java
    │           │   │       └── ListingResponse.java
    │           │   └── event/
    │           │       └── TradeEventListener.java
    │           └── out/
    │               ├── persistence/
    │               │   ├── entity/
    │               │   │   ├── ListingJpaEntity.java
    │               │   │   ├── ProductDetailsJpaEntity.java
    │               │   │   ├── ServiceDetailsJpaEntity.java
    │               │   │   ├── TradeDetailsJpaEntity.java
    │               │   │   └── ListingImageJpaEntity.java
    │               │   ├── repository/
    │               │   │   └── ListingJpaRepository.java
    │               │   ├── mapper/
    │               │   │   └── ListingPersistenceMapper.java
    │               │   └── ListingPersistenceAdapter.java
    │               └── eventpublisher/
    │                   └── SpringDomainEventPublisher.java
    │
    └── test/java/uce/edu/ec/marketplace/catalog/
        ├── domain/aggregate/
        │   └── ListingTest.java
        └── application/service/
            └── CreateListingServiceTest.java
```

### Reglas de dependencia entre capas (orden estricto)

```
domain  ←  application  ←  infrastructure
```

- `domain/` importa solo Java estándar (sin Spring, sin JPA, sin anotaciones de framework)
- `application/` importa `domain/` y define puertos — nunca importa `infrastructure/`
- `infrastructure/` importa `application/` y `domain/` — aquí viven Spring, JPA, etc.

---

## 5. Shared Kernel

```
shared-kernel/
├── pom.xml
└── src/main/java/uce/edu/ec/marketplace/shared/
    ├── valueobject/
    │   ├── UserId.java
    │   ├── ListingId.java
    │   ├── OrderId.java
    │   ├── TradeId.java
    │   ├── ServiceContractId.java
    │   ├── Money.java
    │   ├── TransactionRef.java
    │   └── MutualConfirmation.java
    └── enums/
        └── TransactionType.java
```

---

## 6. Bootstrap

```
bootstrap/
├── pom.xml                              ← depende de TODOS los módulos BC
└── src/
    ├── main/
    │   ├── java/uce/edu/ec/marketplace/
    │   │   └── MarketplaceApplication.java
    │   └── resources/
    │       ├── application.yml
    │       ├── application-local.yml
    │       ├── application-prod.yml
    │       └── db/migration/
    │           ├── V1__create_identity_schema.sql
    │           ├── V2__create_catalog_schema.sql
    │           ├── V3__create_trade_schema.sql
    │           ├── V4__create_reputation_schema.sql
    │           ├── V5__create_messaging_schema.sql
    │           └── V6__create_notifications_schema.sql
    └── test/java/uce/edu/ec/marketplace/
        └── MarketplaceApplicationTest.java
```

**Flyway vive en bootstrap** porque necesita una única conexión a la BD para ejecutar todos los scripts en orden — el único módulo que conoce todos los schemas es el composition root.

---

## 7. Inventario de clases por BC (referencia rápida)

| BC | Aggregates | Entities | Value Objects clave |
|----|-----------|---------|---------------------|
| `catalog` | `Listing` | `Category` | `ListingDetails`, `ProductDetails`, `ServiceDetails`, `TradeDetails`, `ImageRef`, `TradeItemDescription` |
| `trade` | `Order`, `ServiceContract`, `Trade` | — | `MonetaryAdjustment`, `TradeOfferTerms` |
| `identity` | `Account` | `Profile` | — |
| `reputation` | `ReputationProfile` | `Review` | — |
| `messaging` | `Conversation` | `Message` | — |
| `notifications` | `Notification` | — | — |
| `fraud-detection` | — | — | `RiskAssessmentSummary`, `ListingSnapshot` (stub MVP) |
| `recommendation` | — | — | (stub MVP) |
| `shared-kernel` | — | — | `UserId`, `ListingId`, `Money`, `TransactionRef`, `MutualConfirmation` |
