# Estructura de Carpetas y Módulos Backend — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear la estructura completa del monorepo: raíz, backend Maven multi-módulo (10 módulos), Shared Kernel con Value Objects implementados y testeados, skeletons de los 8 Bounded Contexts, y módulo bootstrap — verificando que `mvn clean install` pase sin errores al final.

**Architecture:** Monorepo con `backend/` (Maven multi-módulo), `frontend-web/` y `frontend-mobile/`. Cada BC es un módulo Maven con capas `domain/`, `application/` e `infrastructure/` separadas por paquetes (no por sub-módulos). El Shared Kernel es el único módulo con implementación real en este plan; el resto son skeletons vacíos listos para los planes de dominio e infraestructura.

**Tech Stack:** Java 21, Spring Boot 3.3.5, Maven 3.9.x, JUnit 5, PostgreSQL 15 (Docker), Flyway

**Spec de referencia:** `docs/superpowers/specs/2026-06-14-estructura-carpetas-backend-design.md`

---

## Mapa de archivos

| Archivo | Responsabilidad |
|---------|----------------|
| `docker-compose.yml` | Levanta PostgreSQL 15 para desarrollo local |
| `.env.example` | Plantilla de variables de entorno |
| `backend/pom.xml` | Parent POM — gestiona versiones y declara los 10 módulos |
| `backend/shared-kernel/pom.xml` | Módulo pure-Java sin Spring |
| `backend/shared-kernel/.../UserId.java` | Value Object identificador de usuario |
| `backend/shared-kernel/.../ListingId.java` | Value Object identificador de publicación |
| `backend/shared-kernel/.../OrderId.java` | Value Object identificador de orden |
| `backend/shared-kernel/.../TradeId.java` | Value Object identificador de trueque |
| `backend/shared-kernel/.../ServiceContractId.java` | Value Object identificador de contrato de servicio |
| `backend/shared-kernel/.../Money.java` | Value Object monetario con suma y validación |
| `backend/shared-kernel/.../TransactionType.java` | Enum de tipo de transacción |
| `backend/shared-kernel/.../TransactionRef.java` | Value Object referencia a transacción |
| `backend/shared-kernel/.../MutualConfirmation.java` | Value Object con lógica de confirmación y timeout |
| `backend/{identity,catalog,trade,...}/pom.xml` | POMs de BC (8 módulos skeleton) |
| `backend/bootstrap/pom.xml` | Composition root — depende de todos los BCs |
| `backend/bootstrap/.../MarketplaceApplication.java` | Punto de entrada Spring Boot |
| `backend/bootstrap/resources/application.yml` | Configuración base |
| `backend/bootstrap/resources/application-local.yml` | Perfil local (BD local, logs DEBUG) |

---

## Tarea 1: Conectar GitHub remoto y estructura raíz del monorepo

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `frontend-web/.gitkeep`
- Create: `frontend-mobile/.gitkeep`

- [ ] **Paso 1: Conectar el repositorio GitHub remoto**

```powershell
git remote add origin https://github.com/RodneyAndrade3/MarketPlace-UCE.git
git remote -v
```

Resultado esperado:
```
origin  https://github.com/RodneyAndrade3/MarketPlace-UCE.git (fetch)
origin  https://github.com/RodneyAndrade3/MarketPlace-UCE.git (push)
```

> Si ya existe un remoto con ese nombre: `git remote set-url origin https://github.com/RodneyAndrade3/MarketPlace-UCE.git`

- [ ] **Paso 2: Crear `docker-compose.yml`**

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: marketplace-postgres
    environment:
      POSTGRES_DB: marketplace_uce
      POSTGRES_USER: ${DB_USER:-marketplace}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-marketplace}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U marketplace"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

- [ ] **Paso 3: Crear `.env.example`**

```env
# .env.example — copiar a .env y completar con valores reales
DB_USER=marketplace
DB_PASSWORD=marketplace
DB_URL=jdbc:postgresql://localhost:5432/marketplace_uce
JWT_SECRET=cambia-esto-en-produccion-minimo-256-bits
```

- [ ] **Paso 4: Crear stubs de frontend**

```powershell
New-Item -ItemType Directory -Force "frontend-web"
New-Item -ItemType File -Path "frontend-web\.gitkeep" -Force
New-Item -ItemType Directory -Force "frontend-mobile"
New-Item -ItemType File -Path "frontend-mobile\.gitkeep" -Force
```

- [ ] **Paso 5: Actualizar `.gitignore`**

Crear (o reemplazar) el `.gitignore` en la raíz del repo con:

```gitignore
# Maven
target/
*.class
*.jar
*.war

# IDE
.idea/
*.iml
.vscode/
*.code-workspace

# Entorno
.env
*.env.local

# Node / Frontend
node_modules/
dist/
build/
.expo/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Docker
docker-compose.override.yml
```

- [ ] **Paso 6: Commit**

```powershell
git add docker-compose.yml .env.example frontend-web/.gitkeep frontend-mobile/.gitkeep .gitignore
git commit -m "chore: estructura raiz del monorepo con docker-compose y frontend stubs"
```

---

## Tarea 2: Parent POM del backend

**Files:**
- Create: `backend/pom.xml`

- [ ] **Paso 1: Crear `backend/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.3.5</version>
        <relativePath/>
    </parent>

    <groupId>uce.edu.ec</groupId>
    <artifactId>marketplace-parent</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <packaging>pom</packaging>
    <name>Marketplace UCE - Parent</name>

    <modules>
        <module>shared-kernel</module>
        <module>identity</module>
        <module>catalog</module>
        <module>trade</module>
        <module>reputation</module>
        <module>messaging</module>
        <module>fraud-detection</module>
        <module>recommendation</module>
        <module>notifications</module>
        <module>bootstrap</module>
    </modules>

    <properties>
        <java.version>21</java.version>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>uce.edu.ec</groupId>
                <artifactId>shared-kernel</artifactId>
                <version>${project.version}</version>
            </dependency>
            <dependency>
                <groupId>uce.edu.ec</groupId>
                <artifactId>identity</artifactId>
                <version>${project.version}</version>
            </dependency>
            <dependency>
                <groupId>uce.edu.ec</groupId>
                <artifactId>catalog</artifactId>
                <version>${project.version}</version>
            </dependency>
            <dependency>
                <groupId>uce.edu.ec</groupId>
                <artifactId>trade</artifactId>
                <version>${project.version}</version>
            </dependency>
            <dependency>
                <groupId>uce.edu.ec</groupId>
                <artifactId>reputation</artifactId>
                <version>${project.version}</version>
            </dependency>
            <dependency>
                <groupId>uce.edu.ec</groupId>
                <artifactId>messaging</artifactId>
                <version>${project.version}</version>
            </dependency>
            <dependency>
                <groupId>uce.edu.ec</groupId>
                <artifactId>fraud-detection</artifactId>
                <version>${project.version}</version>
            </dependency>
            <dependency>
                <groupId>uce.edu.ec</groupId>
                <artifactId>recommendation</artifactId>
                <version>${project.version}</version>
            </dependency>
            <dependency>
                <groupId>uce.edu.ec</groupId>
                <artifactId>notifications</artifactId>
                <version>${project.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
```

- [ ] **Paso 2: Generar Maven Wrapper**

```powershell
cd backend
mvn wrapper:wrapper
cd ..
```

Resultado esperado: se crean `backend/mvnw`, `backend/mvnw.cmd` y `backend/.mvn/wrapper/maven-wrapper.properties`.

- [ ] **Paso 3: Commit**

```powershell
git add backend/pom.xml backend/mvnw backend/mvnw.cmd backend/.mvn/
git commit -m "build: parent POM del backend con 10 modulos y Maven Wrapper"
```

---

## Tarea 3: Shared Kernel — pom.xml y Value Objects de IDs

**Files:**
- Create: `backend/shared-kernel/pom.xml`
- Create: `backend/shared-kernel/src/main/java/uce/edu/ec/marketplace/shared/valueobject/UserId.java`
- Create: `backend/shared-kernel/src/main/java/uce/edu/ec/marketplace/shared/valueobject/ListingId.java`
- Create: `backend/shared-kernel/src/main/java/uce/edu/ec/marketplace/shared/valueobject/OrderId.java`
- Create: `backend/shared-kernel/src/main/java/uce/edu/ec/marketplace/shared/valueobject/TradeId.java`
- Create: `backend/shared-kernel/src/main/java/uce/edu/ec/marketplace/shared/valueobject/ServiceContractId.java`
- Test: `backend/shared-kernel/src/test/java/uce/edu/ec/marketplace/shared/valueobject/IdValueObjectsTest.java`

- [ ] **Paso 1: Crear estructura de directorios del shared-kernel**

```powershell
$base = "backend/shared-kernel/src"
New-Item -ItemType Directory -Force "$base/main/java/uce/edu/ec/marketplace/shared/valueobject"
New-Item -ItemType Directory -Force "$base/main/java/uce/edu/ec/marketplace/shared/enums"
New-Item -ItemType Directory -Force "$base/test/java/uce/edu/ec/marketplace/shared/valueobject"
```

- [ ] **Paso 2: Crear `backend/shared-kernel/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>uce.edu.ec</groupId>
        <artifactId>marketplace-parent</artifactId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>

    <artifactId>shared-kernel</artifactId>
    <name>Marketplace UCE - Shared Kernel</name>

    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

- [ ] **Paso 3: Escribir el test de IDs (primero — TDD)**

`backend/shared-kernel/src/test/java/uce/edu/ec/marketplace/shared/valueobject/IdValueObjectsTest.java`:

```java
package uce.edu.ec.marketplace.shared.valueobject;

import org.junit.jupiter.api.Test;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

class IdValueObjectsTest {

    @Test
    void userId_no_acepta_uuid_nulo() {
        assertThrows(IllegalArgumentException.class, () -> new UserId(null));
    }

    @Test
    void userId_generate_crea_ids_distintos() {
        assertNotEquals(UserId.generate(), UserId.generate());
    }

    @Test
    void userId_of_parsea_string_valido() {
        String uuidStr = "550e8400-e29b-41d4-a716-446655440000";
        assertEquals(UUID.fromString(uuidStr), UserId.of(uuidStr).value());
    }

    @Test
    void listingId_no_acepta_uuid_nulo() {
        assertThrows(IllegalArgumentException.class, () -> new ListingId(null));
    }

    @Test
    void listingId_generate_crea_ids_distintos() {
        assertNotEquals(ListingId.generate(), ListingId.generate());
    }

    @Test
    void orderId_generate_crea_ids_distintos() {
        assertNotEquals(OrderId.generate(), OrderId.generate());
    }

    @Test
    void tradeId_generate_crea_ids_distintos() {
        assertNotEquals(TradeId.generate(), TradeId.generate());
    }

    @Test
    void serviceContractId_generate_crea_ids_distintos() {
        assertNotEquals(ServiceContractId.generate(), ServiceContractId.generate());
    }
}
```

- [ ] **Paso 4: Ejecutar el test — debe fallar**

```powershell
cd backend
.\mvnw.cmd test -pl shared-kernel -Dtest=IdValueObjectsTest
```

Resultado esperado: **COMPILACIÓN FALLA** — `UserId`, `ListingId`, etc. no existen aún.

- [ ] **Paso 5: Crear `UserId.java`**

```java
package uce.edu.ec.marketplace.shared.valueobject;

import java.util.UUID;

public record UserId(UUID value) {
    public UserId {
        if (value == null) throw new IllegalArgumentException("UserId no puede ser nulo");
    }
    public static UserId generate() { return new UserId(UUID.randomUUID()); }
    public static UserId of(String value) { return new UserId(UUID.fromString(value)); }
}
```

- [ ] **Paso 6: Crear `ListingId.java`**

```java
package uce.edu.ec.marketplace.shared.valueobject;

import java.util.UUID;

public record ListingId(UUID value) {
    public ListingId {
        if (value == null) throw new IllegalArgumentException("ListingId no puede ser nulo");
    }
    public static ListingId generate() { return new ListingId(UUID.randomUUID()); }
    public static ListingId of(String value) { return new ListingId(UUID.fromString(value)); }
}
```

- [ ] **Paso 7: Crear `OrderId.java`**

```java
package uce.edu.ec.marketplace.shared.valueobject;

import java.util.UUID;

public record OrderId(UUID value) {
    public OrderId {
        if (value == null) throw new IllegalArgumentException("OrderId no puede ser nulo");
    }
    public static OrderId generate() { return new OrderId(UUID.randomUUID()); }
    public static OrderId of(String value) { return new OrderId(UUID.fromString(value)); }
}
```

- [ ] **Paso 8: Crear `TradeId.java`**

```java
package uce.edu.ec.marketplace.shared.valueobject;

import java.util.UUID;

public record TradeId(UUID value) {
    public TradeId {
        if (value == null) throw new IllegalArgumentException("TradeId no puede ser nulo");
    }
    public static TradeId generate() { return new TradeId(UUID.randomUUID()); }
    public static TradeId of(String value) { return new TradeId(UUID.fromString(value)); }
}
```

- [ ] **Paso 9: Crear `ServiceContractId.java`**

```java
package uce.edu.ec.marketplace.shared.valueobject;

import java.util.UUID;

public record ServiceContractId(UUID value) {
    public ServiceContractId {
        if (value == null) throw new IllegalArgumentException("ServiceContractId no puede ser nulo");
    }
    public static ServiceContractId generate() { return new ServiceContractId(UUID.randomUUID()); }
    public static ServiceContractId of(String value) { return new ServiceContractId(UUID.fromString(value)); }
}
```

- [ ] **Paso 10: Ejecutar tests — deben pasar**

```powershell
.\mvnw.cmd test -pl shared-kernel -Dtest=IdValueObjectsTest
```

Resultado esperado:
```
[INFO] Tests run: 8, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

- [ ] **Paso 11: Commit**

```powershell
git add backend/shared-kernel/
git commit -m "feat(shared-kernel): value objects de IDs (UserId, ListingId, OrderId, TradeId, ServiceContractId)"
```

---

## Tarea 4: Shared Kernel — Money y TransactionRef

**Files:**
- Create: `backend/shared-kernel/src/main/java/uce/edu/ec/marketplace/shared/enums/TransactionType.java`
- Create: `backend/shared-kernel/src/main/java/uce/edu/ec/marketplace/shared/valueobject/Money.java`
- Create: `backend/shared-kernel/src/main/java/uce/edu/ec/marketplace/shared/valueobject/TransactionRef.java`
- Test: `backend/shared-kernel/src/test/java/uce/edu/ec/marketplace/shared/valueobject/MoneyTest.java`
- Test: `backend/shared-kernel/src/test/java/uce/edu/ec/marketplace/shared/valueobject/TransactionRefTest.java`

- [ ] **Paso 1: Escribir `MoneyTest.java` (TDD)**

```java
package uce.edu.ec.marketplace.shared.valueobject;

import org.junit.jupiter.api.Test;
import java.math.BigDecimal;
import static org.junit.jupiter.api.Assertions.*;

class MoneyTest {

    @Test
    void no_acepta_amount_nulo() {
        assertThrows(IllegalArgumentException.class, () -> new Money(null, "USD"));
    }

    @Test
    void no_acepta_currency_nula() {
        assertThrows(IllegalArgumentException.class, () -> new Money(BigDecimal.TEN, null));
    }

    @Test
    void no_acepta_monto_negativo() {
        assertThrows(IllegalArgumentException.class,
                () -> new Money(new BigDecimal("-0.01"), "USD"));
    }

    @Test
    void acepta_monto_cero() {
        assertDoesNotThrow(() -> new Money(BigDecimal.ZERO, "USD"));
    }

    @Test
    void suma_montos_misma_moneda() {
        Money a = new Money(new BigDecimal("10.00"), "USD");
        Money b = new Money(new BigDecimal("5.50"), "USD");
        assertEquals(new Money(new BigDecimal("15.50"), "USD"), a.add(b));
    }

    @Test
    void no_permite_sumar_monedas_distintas() {
        Money usd = new Money(new BigDecimal("10.00"), "USD");
        Money eur = new Money(new BigDecimal("5.00"), "EUR");
        assertThrows(IllegalArgumentException.class, () -> usd.add(eur));
    }
}
```

- [ ] **Paso 2: Escribir `TransactionRefTest.java` (TDD)**

```java
package uce.edu.ec.marketplace.shared.valueobject;

import org.junit.jupiter.api.Test;
import uce.edu.ec.marketplace.shared.enums.TransactionType;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

class TransactionRefTest {

    @Test
    void no_acepta_type_nulo() {
        assertThrows(IllegalArgumentException.class,
                () -> new TransactionRef(null, UUID.randomUUID()));
    }

    @Test
    void no_acepta_id_nulo() {
        assertThrows(IllegalArgumentException.class,
                () -> new TransactionRef(TransactionType.ORDER, null));
    }

    @Test
    void crea_ref_valida() {
        UUID id = UUID.randomUUID();
        TransactionRef ref = new TransactionRef(TransactionType.TRADE, id);
        assertEquals(TransactionType.TRADE, ref.type());
        assertEquals(id, ref.id());
    }
}
```

- [ ] **Paso 3: Ejecutar tests — deben fallar**

```powershell
.\mvnw.cmd test -pl shared-kernel -Dtest="MoneyTest,TransactionRefTest"
```

Resultado esperado: **COMPILACIÓN FALLA** — clases no existen.

- [ ] **Paso 4: Crear `TransactionType.java`**

```java
package uce.edu.ec.marketplace.shared.enums;

public enum TransactionType {
    ORDER,
    SERVICE_CONTRACT,
    TRADE
}
```

- [ ] **Paso 5: Crear `Money.java`**

```java
package uce.edu.ec.marketplace.shared.valueobject;

import java.math.BigDecimal;
import java.util.Objects;

public record Money(BigDecimal amount, String currency) {

    public Money {
        Objects.requireNonNull(amount, "El monto no puede ser nulo");
        Objects.requireNonNull(currency, "La moneda no puede ser nula");
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("El monto no puede ser negativo");
        }
    }

    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException(
                    "No se pueden sumar montos en distintas monedas: " + this.currency + " y " + other.currency);
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }
}
```

- [ ] **Paso 6: Crear `TransactionRef.java`**

```java
package uce.edu.ec.marketplace.shared.valueobject;

import uce.edu.ec.marketplace.shared.enums.TransactionType;
import java.util.UUID;

public record TransactionRef(TransactionType type, UUID id) {
    public TransactionRef {
        if (type == null) throw new IllegalArgumentException("TransactionType no puede ser nulo");
        if (id == null) throw new IllegalArgumentException("El ID de transaccion no puede ser nulo");
    }
}
```

- [ ] **Paso 7: Ejecutar tests — deben pasar**

```powershell
.\mvnw.cmd test -pl shared-kernel -Dtest="MoneyTest,TransactionRefTest"
```

Resultado esperado:
```
[INFO] Tests run: 9, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

- [ ] **Paso 8: Commit**

```powershell
git add backend/shared-kernel/src/
git commit -m "feat(shared-kernel): Money, TransactionType y TransactionRef"
```

---

## Tarea 5: Shared Kernel — MutualConfirmation

**Files:**
- Create: `backend/shared-kernel/src/main/java/uce/edu/ec/marketplace/shared/valueobject/MutualConfirmation.java`
- Test: `backend/shared-kernel/src/test/java/uce/edu/ec/marketplace/shared/valueobject/MutualConfirmationTest.java`

- [ ] **Paso 1: Escribir `MutualConfirmationTest.java` (TDD)**

```java
package uce.edu.ec.marketplace.shared.valueobject;

import org.junit.jupiter.api.Test;
import java.time.Duration;
import java.time.Instant;
import static org.junit.jupiter.api.Assertions.*;

class MutualConfirmationTest {

    @Test
    void no_esta_completa_sin_confirmaciones() {
        assertFalse(MutualConfirmation.empty().isComplete());
    }

    @Test
    void esta_completa_cuando_ambas_partes_confirman() {
        Instant now = Instant.now();
        MutualConfirmation conf = MutualConfirmation.empty()
                .confirmByPartyA(now)
                .confirmByPartyB(now);
        assertTrue(conf.isComplete());
    }

    @Test
    void no_esta_completa_con_solo_una_confirmacion() {
        MutualConfirmation conf = MutualConfirmation.empty().confirmByPartyA(Instant.now());
        assertFalse(conf.isComplete());
    }

    @Test
    void expira_si_solo_partyA_confirmo_y_paso_el_timeout() {
        Instant hace6Dias = Instant.now().minus(Duration.ofDays(6));
        MutualConfirmation conf = MutualConfirmation.empty().confirmByPartyA(hace6Dias);
        assertTrue(conf.isExpired(Instant.now(), Duration.ofDays(5)));
    }

    @Test
    void expira_si_solo_partyB_confirmo_y_paso_el_timeout() {
        Instant hace6Dias = Instant.now().minus(Duration.ofDays(6));
        MutualConfirmation conf = MutualConfirmation.empty().confirmByPartyB(hace6Dias);
        assertTrue(conf.isExpired(Instant.now(), Duration.ofDays(5)));
    }

    @Test
    void no_expira_si_esta_completa_aunque_haya_pasado_el_tiempo() {
        Instant hace6Dias = Instant.now().minus(Duration.ofDays(6));
        MutualConfirmation conf = MutualConfirmation.empty()
                .confirmByPartyA(hace6Dias)
                .confirmByPartyB(hace6Dias);
        assertFalse(conf.isExpired(Instant.now(), Duration.ofDays(5)));
    }

    @Test
    void no_expira_si_no_hay_ninguna_confirmacion() {
        assertFalse(MutualConfirmation.empty().isExpired(Instant.now(), Duration.ofDays(5)));
    }

    @Test
    void no_expira_si_una_parte_confirmo_dentro_del_window() {
        Instant haceUnDia = Instant.now().minus(Duration.ofDays(1));
        MutualConfirmation conf = MutualConfirmation.empty().confirmByPartyA(haceUnDia);
        assertFalse(conf.isExpired(Instant.now(), Duration.ofDays(5)));
    }
}
```

- [ ] **Paso 2: Ejecutar test — debe fallar**

```powershell
.\mvnw.cmd test -pl shared-kernel -Dtest=MutualConfirmationTest
```

Resultado esperado: **COMPILACIÓN FALLA** — `MutualConfirmation` no existe.

- [ ] **Paso 3: Crear `MutualConfirmation.java`**

```java
package uce.edu.ec.marketplace.shared.valueobject;

import java.time.Duration;
import java.time.Instant;
import java.util.Optional;

public record MutualConfirmation(
        boolean confirmedByPartyA,
        boolean confirmedByPartyB,
        Optional<Instant> confirmedAtA,
        Optional<Instant> confirmedAtB
) {
    public static MutualConfirmation empty() {
        return new MutualConfirmation(false, false, Optional.empty(), Optional.empty());
    }

    public boolean isComplete() {
        return confirmedByPartyA && confirmedByPartyB;
    }

    public boolean isExpired(Instant now, Duration timeoutWindow) {
        if (isComplete()) return false;
        if (confirmedByPartyA && confirmedAtA.isPresent()) {
            return now.isAfter(confirmedAtA.get().plus(timeoutWindow));
        }
        if (confirmedByPartyB && confirmedAtB.isPresent()) {
            return now.isAfter(confirmedAtB.get().plus(timeoutWindow));
        }
        return false;
    }

    public MutualConfirmation confirmByPartyA(Instant at) {
        return new MutualConfirmation(true, confirmedByPartyB, Optional.of(at), confirmedAtB);
    }

    public MutualConfirmation confirmByPartyB(Instant at) {
        return new MutualConfirmation(confirmedByPartyA, true, confirmedAtA, Optional.of(at));
    }
}
```

- [ ] **Paso 4: Ejecutar todos los tests del shared-kernel**

```powershell
.\mvnw.cmd test -pl shared-kernel
```

Resultado esperado:
```
[INFO] Tests run: 17, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

- [ ] **Paso 5: Commit**

```powershell
git add backend/shared-kernel/src/
git commit -m "feat(shared-kernel): MutualConfirmation con logica de confirmacion y timeout"
```

---

## Tarea 6: Skeletons de BCs Core — identity, catalog, trade

**Files:**
- Create: `backend/identity/pom.xml`
- Create: `backend/catalog/pom.xml`
- Create: `backend/trade/pom.xml`

- [ ] **Paso 1: Crear `backend/identity/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>uce.edu.ec</groupId>
        <artifactId>marketplace-parent</artifactId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>

    <artifactId>identity</artifactId>
    <name>Marketplace UCE - Identity and Access BC</name>

    <dependencies>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>shared-kernel</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

- [ ] **Paso 2: Crear estructura de paquetes de identity**

```powershell
$pkg = "backend/identity/src/main/java/uce/edu/ec/marketplace/identity"
New-Item -ItemType Directory -Force "$pkg/domain/aggregate"
New-Item -ItemType Directory -Force "$pkg/domain/entity"
New-Item -ItemType Directory -Force "$pkg/domain/valueobject"
New-Item -ItemType Directory -Force "$pkg/domain/enums"
New-Item -ItemType Directory -Force "$pkg/domain/event"
New-Item -ItemType Directory -Force "$pkg/domain/exception"
New-Item -ItemType Directory -Force "$pkg/application/port/in"
New-Item -ItemType Directory -Force "$pkg/application/port/out"
New-Item -ItemType Directory -Force "$pkg/application/service"
New-Item -ItemType Directory -Force "$pkg/application/dto/command"
New-Item -ItemType Directory -Force "$pkg/application/dto/query"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/in/rest/dto"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/entity"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/repository"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/mapper"
New-Item -ItemType Directory -Force "backend/identity/src/test/java/uce/edu/ec/marketplace/identity"
```

- [ ] **Paso 3: Crear `backend/catalog/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>uce.edu.ec</groupId>
        <artifactId>marketplace-parent</artifactId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>

    <artifactId>catalog</artifactId>
    <name>Marketplace UCE - Catalog BC</name>

    <dependencies>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>shared-kernel</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

- [ ] **Paso 4: Crear estructura de paquetes de catalog**

```powershell
$pkg = "backend/catalog/src/main/java/uce/edu/ec/marketplace/catalog"
New-Item -ItemType Directory -Force "$pkg/domain/aggregate"
New-Item -ItemType Directory -Force "$pkg/domain/entity"
New-Item -ItemType Directory -Force "$pkg/domain/valueobject"
New-Item -ItemType Directory -Force "$pkg/domain/enums"
New-Item -ItemType Directory -Force "$pkg/domain/event"
New-Item -ItemType Directory -Force "$pkg/domain/service"
New-Item -ItemType Directory -Force "$pkg/domain/exception"
New-Item -ItemType Directory -Force "$pkg/application/port/in"
New-Item -ItemType Directory -Force "$pkg/application/port/out"
New-Item -ItemType Directory -Force "$pkg/application/service"
New-Item -ItemType Directory -Force "$pkg/application/dto/command"
New-Item -ItemType Directory -Force "$pkg/application/dto/query"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/in/rest/dto"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/in/event"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/entity"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/repository"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/mapper"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/eventpublisher"
New-Item -ItemType Directory -Force "backend/catalog/src/test/java/uce/edu/ec/marketplace/catalog"
```

- [ ] **Paso 5: Crear `backend/trade/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>uce.edu.ec</groupId>
        <artifactId>marketplace-parent</artifactId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>

    <artifactId>trade</artifactId>
    <name>Marketplace UCE - Trade and Transactions BC</name>

    <dependencies>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>shared-kernel</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

- [ ] **Paso 6: Crear estructura de paquetes de trade**

```powershell
$pkg = "backend/trade/src/main/java/uce/edu/ec/marketplace/trade"
New-Item -ItemType Directory -Force "$pkg/domain/aggregate"
New-Item -ItemType Directory -Force "$pkg/domain/valueobject"
New-Item -ItemType Directory -Force "$pkg/domain/enums"
New-Item -ItemType Directory -Force "$pkg/domain/event"
New-Item -ItemType Directory -Force "$pkg/domain/exception"
New-Item -ItemType Directory -Force "$pkg/application/port/in"
New-Item -ItemType Directory -Force "$pkg/application/port/out"
New-Item -ItemType Directory -Force "$pkg/application/service"
New-Item -ItemType Directory -Force "$pkg/application/dto/command"
New-Item -ItemType Directory -Force "$pkg/application/dto/query"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/in/rest/dto"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/in/event"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/entity"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/repository"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/mapper"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/eventpublisher"
New-Item -ItemType Directory -Force "backend/trade/src/test/java/uce/edu/ec/marketplace/trade"
```

- [ ] **Paso 7: Compilar los tres módulos**

```powershell
.\mvnw.cmd install -pl shared-kernel
.\mvnw.cmd compile -pl identity,catalog,trade
```

Resultado esperado:
```
[INFO] BUILD SUCCESS
```

- [ ] **Paso 8: Commit**

```powershell
git add backend/identity/ backend/catalog/ backend/trade/
git commit -m "chore: skeletons de BCs core (identity, catalog, trade)"
```

---

## Tarea 7: Skeletons de BCs Supporting — reputation, messaging, notifications

**Files:**
- Create: `backend/reputation/pom.xml`
- Create: `backend/messaging/pom.xml`
- Create: `backend/notifications/pom.xml`

- [ ] **Paso 1: Crear `backend/reputation/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>uce.edu.ec</groupId>
        <artifactId>marketplace-parent</artifactId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>
    <artifactId>reputation</artifactId>
    <name>Marketplace UCE - Reputation BC</name>
    <dependencies>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>shared-kernel</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

- [ ] **Paso 2: Crear estructura de paquetes de reputation**

```powershell
$pkg = "backend/reputation/src/main/java/uce/edu/ec/marketplace/reputation"
New-Item -ItemType Directory -Force "$pkg/domain/aggregate"
New-Item -ItemType Directory -Force "$pkg/domain/entity"
New-Item -ItemType Directory -Force "$pkg/domain/valueobject"
New-Item -ItemType Directory -Force "$pkg/domain/enums"
New-Item -ItemType Directory -Force "$pkg/domain/event"
New-Item -ItemType Directory -Force "$pkg/domain/exception"
New-Item -ItemType Directory -Force "$pkg/application/port/in"
New-Item -ItemType Directory -Force "$pkg/application/port/out"
New-Item -ItemType Directory -Force "$pkg/application/service"
New-Item -ItemType Directory -Force "$pkg/application/dto/command"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/in/rest/dto"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/in/event"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/entity"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/repository"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/mapper"
New-Item -ItemType Directory -Force "backend/reputation/src/test/java/uce/edu/ec/marketplace/reputation"
```

- [ ] **Paso 3: Crear `backend/messaging/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>uce.edu.ec</groupId>
        <artifactId>marketplace-parent</artifactId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>
    <artifactId>messaging</artifactId>
    <name>Marketplace UCE - Messaging BC</name>
    <dependencies>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>shared-kernel</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-websocket</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

- [ ] **Paso 4: Crear estructura de paquetes de messaging**

```powershell
$pkg = "backend/messaging/src/main/java/uce/edu/ec/marketplace/messaging"
New-Item -ItemType Directory -Force "$pkg/domain/aggregate"
New-Item -ItemType Directory -Force "$pkg/domain/entity"
New-Item -ItemType Directory -Force "$pkg/domain/valueobject"
New-Item -ItemType Directory -Force "$pkg/domain/event"
New-Item -ItemType Directory -Force "$pkg/domain/exception"
New-Item -ItemType Directory -Force "$pkg/application/port/in"
New-Item -ItemType Directory -Force "$pkg/application/port/out"
New-Item -ItemType Directory -Force "$pkg/application/service"
New-Item -ItemType Directory -Force "$pkg/application/dto/command"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/in/rest/dto"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/in/websocket"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/in/event"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/entity"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/repository"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/mapper"
New-Item -ItemType Directory -Force "backend/messaging/src/test/java/uce/edu/ec/marketplace/messaging"
```

- [ ] **Paso 5: Crear `backend/notifications/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>uce.edu.ec</groupId>
        <artifactId>marketplace-parent</artifactId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>
    <artifactId>notifications</artifactId>
    <name>Marketplace UCE - Notifications BC</name>
    <dependencies>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>shared-kernel</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

- [ ] **Paso 6: Crear estructura de paquetes de notifications**

```powershell
$pkg = "backend/notifications/src/main/java/uce/edu/ec/marketplace/notifications"
New-Item -ItemType Directory -Force "$pkg/domain/aggregate"
New-Item -ItemType Directory -Force "$pkg/domain/enums"
New-Item -ItemType Directory -Force "$pkg/domain/event"
New-Item -ItemType Directory -Force "$pkg/domain/exception"
New-Item -ItemType Directory -Force "$pkg/application/port/in"
New-Item -ItemType Directory -Force "$pkg/application/port/out"
New-Item -ItemType Directory -Force "$pkg/application/service"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/in/event"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/entity"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/persistence/repository"
New-Item -ItemType Directory -Force "backend/notifications/src/test/java/uce/edu/ec/marketplace/notifications"
```

- [ ] **Paso 7: Compilar los tres módulos**

```powershell
.\mvnw.cmd compile -pl reputation,messaging,notifications --also-make
```

Resultado esperado:
```
[INFO] BUILD SUCCESS
```

- [ ] **Paso 8: Commit**

```powershell
git add backend/reputation/ backend/messaging/ backend/notifications/
git commit -m "chore: skeletons de BCs supporting (reputation, messaging, notifications)"
```

---

## Tarea 8: Skeletons de BCs de IA — fraud-detection y recommendation

**Files:**
- Create: `backend/fraud-detection/pom.xml`
- Create: `backend/recommendation/pom.xml`

- [ ] **Paso 1: Crear `backend/fraud-detection/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>uce.edu.ec</groupId>
        <artifactId>marketplace-parent</artifactId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>
    <artifactId>fraud-detection</artifactId>
    <name>Marketplace UCE - Fraud Detection BC (stub MVP)</name>
    <dependencies>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>shared-kernel</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

- [ ] **Paso 2: Crear estructura de paquetes de fraud-detection**

```powershell
$pkg = "backend/fraud-detection/src/main/java/uce/edu/ec/marketplace/fraud"
New-Item -ItemType Directory -Force "$pkg/domain/valueobject"
New-Item -ItemType Directory -Force "$pkg/domain/enums"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/stub"
New-Item -ItemType Directory -Force "backend/fraud-detection/src/test/java/uce/edu/ec/marketplace/fraud"
```

- [ ] **Paso 3: Crear `backend/recommendation/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>uce.edu.ec</groupId>
        <artifactId>marketplace-parent</artifactId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>
    <artifactId>recommendation</artifactId>
    <name>Marketplace UCE - Recommendation Engine BC (stub MVP)</name>
    <dependencies>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>shared-kernel</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

- [ ] **Paso 4: Crear estructura de paquetes de recommendation**

```powershell
$pkg = "backend/recommendation/src/main/java/uce/edu/ec/marketplace/recommendation"
New-Item -ItemType Directory -Force "$pkg/infrastructure/adapter/out/stub"
New-Item -ItemType Directory -Force "backend/recommendation/src/test/java/uce/edu/ec/marketplace/recommendation"
```

- [ ] **Paso 5: Compilar**

```powershell
.\mvnw.cmd compile -pl fraud-detection,recommendation
```

Resultado esperado:
```
[INFO] BUILD SUCCESS
```

- [ ] **Paso 6: Commit**

```powershell
git add backend/fraud-detection/ backend/recommendation/
git commit -m "chore: skeletons de BCs de IA (fraud-detection, recommendation) con puertos stub listos para ADR-003"
```

---

## Tarea 9: Módulo bootstrap

**Files:**
- Create: `backend/bootstrap/pom.xml`
- Create: `backend/bootstrap/src/main/java/uce/edu/ec/marketplace/MarketplaceApplication.java`
- Create: `backend/bootstrap/src/main/resources/application.yml`
- Create: `backend/bootstrap/src/main/resources/application-local.yml`
- Create: `backend/bootstrap/src/main/resources/db/migration/.gitkeep`
- Test: `backend/bootstrap/src/test/java/uce/edu/ec/marketplace/MarketplaceApplicationTest.java`

- [ ] **Paso 1: Crear `backend/bootstrap/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>uce.edu.ec</groupId>
        <artifactId>marketplace-parent</artifactId>
        <version>0.0.1-SNAPSHOT</version>
    </parent>

    <artifactId>bootstrap</artifactId>
    <name>Marketplace UCE - Bootstrap</name>

    <dependencies>
        <!-- Todos los Bounded Contexts -->
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>shared-kernel</artifactId>
        </dependency>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>identity</artifactId>
        </dependency>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>catalog</artifactId>
        </dependency>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>trade</artifactId>
        </dependency>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>reputation</artifactId>
        </dependency>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>messaging</artifactId>
        </dependency>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>fraud-detection</artifactId>
        </dependency>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>recommendation</artifactId>
        </dependency>
        <dependency>
            <groupId>uce.edu.ec</groupId>
            <artifactId>notifications</artifactId>
        </dependency>

        <!-- Spring Boot Web + JPA -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>

        <!-- PostgreSQL -->
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Flyway -->
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
        </dependency>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-database-postgresql</artifactId>
        </dependency>

        <!-- Test -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

- [ ] **Paso 2: Crear directorios del bootstrap**

```powershell
New-Item -ItemType Directory -Force "backend/bootstrap/src/main/java/uce/edu/ec/marketplace"
New-Item -ItemType Directory -Force "backend/bootstrap/src/main/resources/db/migration"
New-Item -ItemType Directory -Force "backend/bootstrap/src/test/java/uce/edu/ec/marketplace"
New-Item -ItemType File -Path "backend/bootstrap/src/main/resources/db/migration/.gitkeep" -Force
```

- [ ] **Paso 3: Crear `MarketplaceApplication.java`**

```java
package uce.edu.ec.marketplace;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "uce.edu.ec.marketplace")
public class MarketplaceApplication {
    public static void main(String[] args) {
        SpringApplication.run(MarketplaceApplication.class, args);
    }
}
```

- [ ] **Paso 4: Crear `application.yml`**

```yaml
spring:
  application:
    name: marketplace-uce
  datasource:
    url: ${DB_URL:jdbc:postgresql://localhost:5432/marketplace_uce}
    username: ${DB_USER:marketplace}
    password: ${DB_PASSWORD:marketplace}
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    open-in-view: false
  flyway:
    enabled: true
    locations: classpath:db/migration

server:
  port: 8080

logging:
  level:
    uce.edu.ec.marketplace: INFO
```

- [ ] **Paso 5: Crear `application-local.yml`**

```yaml
spring:
  jpa:
    show-sql: true
  flyway:
    enabled: false

logging:
  level:
    uce.edu.ec.marketplace: DEBUG
    org.springframework.web: DEBUG
```

- [ ] **Paso 6: Crear `MarketplaceApplicationTest.java`**

```java
package uce.edu.ec.marketplace;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

class MarketplaceApplicationTest {

    @Test
    void main_class_existe_y_tiene_metodo_main() {
        assertDoesNotThrow(() ->
            MarketplaceApplication.class.getMethod("main", String[].class)
        );
    }
}
```

- [ ] **Paso 7: Compilar el módulo bootstrap**

```powershell
.\mvnw.cmd install -pl shared-kernel,identity,catalog,trade,reputation,messaging,fraud-detection,recommendation,notifications
.\mvnw.cmd compile -pl bootstrap
```

Resultado esperado:
```
[INFO] BUILD SUCCESS
```

- [ ] **Paso 8: Commit**

```powershell
git add backend/bootstrap/
git commit -m "feat(bootstrap): composition root con Spring Boot main, application.yml y Flyway configurado"
```

---

## Tarea 10: Verificación end-to-end

- [ ] **Paso 1: Ejecutar `mvn clean install` completo desde backend/**

```powershell
.\mvnw.cmd clean install
```

Resultado esperado:
```
[INFO] Reactor Summary:
[INFO] Marketplace UCE - Parent ........................ SUCCESS
[INFO] Marketplace UCE - Shared Kernel ................. SUCCESS
[INFO] Marketplace UCE - Identity and Access BC ........ SUCCESS
[INFO] Marketplace UCE - Catalog BC .................... SUCCESS
[INFO] Marketplace UCE - Trade and Transactions BC ..... SUCCESS
[INFO] Marketplace UCE - Reputation BC ................. SUCCESS
[INFO] Marketplace UCE - Messaging BC .................. SUCCESS
[INFO] Marketplace UCE - Fraud Detection BC ............ SUCCESS
[INFO] Marketplace UCE - Recommendation Engine BC ...... SUCCESS
[INFO] Marketplace UCE - Notifications BC .............. SUCCESS
[INFO] Marketplace UCE - Bootstrap ..................... SUCCESS
[INFO] BUILD SUCCESS
[INFO] Tests run: 17, Failures: 0, Errors: 0, Skipped: 0
```

- [ ] **Paso 2: Verificar estructura generada**

```powershell
Get-ChildItem backend/ -Directory | Select-Object Name
```

Resultado esperado: 10 directorios (`shared-kernel`, `identity`, `catalog`, `trade`, `reputation`, `messaging`, `fraud-detection`, `recommendation`, `notifications`, `bootstrap`).

- [ ] **Paso 3: Push al repositorio GitHub**

```powershell
git push -u origin main
```

- [ ] **Paso 4: Commit final si hay archivos pendientes**

```powershell
git status
git add .
git commit -m "chore: verificacion end-to-end exitosa - estructura base del monorepo completa"
git push origin main
```

---

## Errores comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `Could not find artifact uce.edu.ec:shared-kernel` | No se instaló shared-kernel antes de compilar otros módulos | Ejecutar `.\mvnw.cmd install -pl shared-kernel` primero |
| `Unsupported class file major version 65` | Java 21 compilado con Maven usando JDK anterior | Verificar `java -version` y que `JAVA_HOME` apunta a JDK 21 |
| `remote: Repository not found` en el push | El remote no está configurado correctamente | Verificar con `git remote -v` y re-ejecutar Paso 1 de Tarea 1 |
| `Permission to RodneyAndrade3/MarketPlace-UCE.git denied` | Sin credenciales GitHub configuradas | Configurar `git credential.helper` o usar SSH key |
