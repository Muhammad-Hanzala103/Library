# KICSIT Library Management System - Viva Preparation QA

**Prepared for**: Muhammad Hanzala  
**Department**: Computer Sciences, Dr A Q Khan Institute (KICSIT)  
**Exam Scope**: Final Project Thesis Viva, System Architecture, & Code Defense

---

### Category A: Core Framework & FastAPI Concepts

#### Q1: Why did you choose FastAPI over Flask or Django for this ERP project?
*   **Answer**: FastAPI is built on modern asynchronous standards (ASGI) using **Starlette** and **Pydantic**. It supports concurrent request processing via Python's `async/await` syntax, which makes it far faster than WSGI-based frameworks like Flask. Additionally, FastAPI provides automatic request validation, serialization, and generates interactive OpenAPI (Swagger) documentation natively.

#### Q2: How does FastAPI leverage Pydantic?
*   **Answer**: FastAPI uses Pydantic for data validation and parsing. Pydantic schemas define the data structures for incoming request bodies (POST/PUT) and outgoing response payloads. If a client submits data with missing or invalid fields, Pydantic intercepts the request and returns structured validation errors (HTTP 422 Unprocessable Entity) before executing the router logic.

#### Q3: What is the difference between ASGI and WSGI servers?
*   **Answer**: WSGI (Web Server Gateway Interface) is a synchronous standard where each incoming request is blocked until it returns a response, utilizing thread pools to scale. ASGI (Asynchronous Server Gateway Interface) supports asynchronous, non-blocking requests, making it capable of handling persistent connections like WebSockets, server-sent events, and massive numbers of concurrent HTTP requests using a single thread via the event loop.

#### Q4: How is dependency injection implemented in FastAPI?
*   **Answer**: Dependency injection is handled using FastAPI's `Depends` function. For example, database sessions (`get_db`) or security verification routines (`require_permission`) are injected directly into the parameters of route functions. This ensures clean separation of concerns, simplifies testing, and guarantees resource clean-up (like closing database sessions) after the request is fulfilled.

#### Q5: What is Uvicorn, and what is its role in your deployment?
*   **Answer**: Uvicorn is a lightning-fast ASGI web server implementation for Python. It acts as the HTTP server that listens for network traffic on host adapters (like `0.0.0.0` or `127.0.0.1` on port `8000`), translates incoming HTTP payloads into standard ASGI dictionary contexts, passes them to our FastAPI application, and serves the returned responses back to clients over TCP.

---

### Category B: Relational Database, SQLAlchemy & Alembic

#### Q6: Explain the difference between `joinedload` and `lazy` loading in SQLAlchemy.
*   **Answer**: By default, SQLAlchemy uses **lazy loading**, meaning linked relationships (e.g., fetching the copies of a book) are not loaded from the database until they are explicitly accessed in the Python code, generating separate SQL queries (the N+1 query problem). **Joined loading** (`joinedload`) uses SQL `LEFT OUTER JOIN` statements to fetch parent records and all associated child entities in a single SQL query, which significantly optimizes database performance.

#### Q7: What are database migrations, and why do we use Alembic?
*   **Answer**: Database migrations track incremental modifications to the relational schema (tables, columns, indexes, constraints) over time. Alembic maps our SQLAlchemy models to the physical MySQL schema, generating step-by-step revision files (`upgrade` and `downgrade` scripts). This allows us to modify database structures safely without losing existing production data or having to rebuild tables manually.

#### Q8: How does SQLAlchemy handle transaction isolation and connection pooling?
*   **Answer**: SQLAlchemy manages database connections using a Connection Pool (default: `QueuePool`). It maintains a pool of persistent connections to the MySQL server to avoid the high overhead of establishing new TCP handshakes for every HTTP request. Transactions are managed using the SQLAlchemy `Session`. Each session is bound to a single transaction block; executing `.commit()` persists the transactions to MySQL, while `.rollback()` undoes all uncommitted transactions in the current session.

#### Q9: Why is it important to use `db.commit()` and `db.rollback()` within a `try-except` block?
*   **Answer**: Using them inside a `try-except` block ensures transactional integrity (ACID). If any database modification fails midway due to a constraint or logical error, invoking `db.rollback()` clears all temporary modifications in that transaction block, preventing database pollution and partial updates. Only when all operations succeed is `db.commit()` invoked to persist changes permanently.

#### Q10: How does the system handle many-to-many relationships? Give an example from your code.
*   **Answer**: The relationship between `User` roles and `Permission` is a classic many-to-many relationship. A single role can have multiple permissions, and a single permission can belong to multiple roles. This is implemented via an association table (`role_permissions` or similar) that maps `role_id` to `permission_id` as foreign keys. In SQLAlchemy, this is mapped using the `secondary` argument inside the `relationship` definition.

---

### Category C: Security, JWT, & Role-Based Access Control (RBAC)

#### Q11: What is JWT, and what are its three components?
*   **Answer**: A JSON Web Token (JWT) is a compact, URL-safe means of representing claims securely between two parties. Its three components are:
    1.  **Header**: Specifies the token type (JWT) and the signing algorithm (e.g., HS256).
    2.  **Payload**: Contains claims (user identifiers like `sub`, username, expiration time `exp`).
    3.  **Signature**: Generated by hashing the encoded Header and Payload using a secret key, verifying the authenticity of the token to prevent tampering.

#### Q12: How are passwords secured in the database?
*   **Answer**: Passwords are never stored as plain text. The system hashes them using **bcrypt** via the `passlib` library. Bcrypt is a slow-hashing algorithm that automatically incorporates a unique random salt for every password, generating a fixed-length cryptographic hash. When a user logs in, the entered plain text password is cryptographically compared against the stored hash.

#### Q13: Explain how Role-Based Access Control (RBAC) is implemented in your system.
*   **Answer**: RBAC is implemented using a granular permissions table linked to user roles. The backend defines explicit permissions (e.g., `catalog.manage`, `settings.manage`, `system.manage_all`). Users are assigned specific Roles. A custom helper route decorator `require_permission(permission_code)` acts as a security guard. When a user requests a protected route, the middleware extracts their JWT token, queries their permissions in the database, and blocks access with an HTTP 403 Forbidden exception if the required permission is not present.

#### Q14: How does the `has_permission` model helper work in templates?
*   **Answer**: The `User` model includes a dynamic method `has_permission(self, permission_code: str) -> bool`. When Jinja2 renders a template, it receives the active `current_user` object. Inside the template, we can selectively render UI elements (like the "System Settings" sidebar button) by executing `{% if current_user.has_permission('settings.manage') %}`, keeping the client interface secure and aligned with backend rules.

#### Q15: What is a Replay Attack, and how does your JWT configuration mitigate this?
*   **Answer**: A replay attack occurs when an unauthorized user intercepts a valid JWT and replays it to impersonate the target. The system mitigates this by setting a strict Token Expiration claim (`exp`), configured via `.env` (e.g., 480 minutes). Once expired, the server automatically rejects the token, requiring the user to re-authenticate and preventing attackers from indefinitely using stolen credentials.

---

### Category D: Intranet Deployment, Networking & Windows Services

#### Q16: What does binding to host `0.0.0.0` mean?
*   **Answer**: Binding to `0.0.0.0` tells the ASGI web server (Uvicorn) to listen for incoming connections on **all** active network interfaces of the host machine (e.g., localhost, Ethernet adapters, Wi-Fi adapters). If bound to `127.0.0.1`, the server would reject any external network request, limiting access exclusively to the server machine itself.

#### Q17: How did you configure Windows Defender Firewall to allow local network users?
*   **Answer**: In Windows Defender Firewall, I configured an **Inbound Rule** specifically for port `8000` (TCP protocol). This instructs the Windows networking kernel to allow incoming network traffic directed at Uvicorn's port from other client machines on the local network, bypassing default firewall blocking.

#### Q18: What is DHCP, and how does it affect your deployment? How do you solve it?
*   **Answer**: DHCP (Dynamic Host Configuration Protocol) automatically assigns temporary IP addresses to devices on a network. If the KICSIT library server reboots, the network router might assign it a different local IP address, breaking client connections. To solve this, the server machine should be assigned a **Static IP Address** in Windows network adapter settings or mapped via a DHCP reservation in the router.

#### Q19: What is the purpose of CORS middleware? Why might you need it in the future?
*   **Answer**: Cross-Origin Resource Sharing (CORS) is a browser security mechanism that restricts scripts on one domain from making API requests to a different domain. If the KICSIT Library System transitions to a decoupled React or mobile frontend hosted on a separate server, FastAPI's CORS middleware must be configured to whitelist the client's origin, allowing seamless API communication.

#### Q20: How do you handle static assets (CSS, JS, Images) in FastAPI?
*   **Answer**: Static assets are mounted under a specific directory prefix using FastAPI's `StaticFiles` class:
   ```python
   app.mount("/static", StaticFiles(directory="app/static"), name="static")
   ```
   FastAPI handles these paths directly, routing them efficiently to the local file system without passing them through custom dynamic database middlewares.

---

### Category E: Settings, Backup & Disaster Recovery Architecture

#### Q21: Explain the system settings dynamic architecture implemented in Phase 9.
*   **Answer**: Rather than hardcoding borrow durations and fine amounts, Phase 9 utilizes a database-backed config model. Settings are stored as key-value pairs in a `settings` table. The `settings_service.py` provides typed helpers to fetch configurations dynamically, automatically parsing and casting values into target types (`int`, `Decimal`, `str`). When circulation calculations are triggered, the service queries this table, ensuring modifications made in the admin UI apply instantly across all transactions.

#### Q22: What is the risk of database backup restoration, and how is it secured?
*   **Answer**: A restore operation completely overwrites the existing database schema, reversing all transactions, issues, returns, and changes made since the backup was taken. To secure this, the route is protected by `system.manage_all` permissions (Super Admin only). Furthermore, the UI implements **double-confirmation safeguards**: the user must first confirm the popup prompt, and then type a specific validation phrase (`CONFIRM RESTORE` in all caps) before the server executes the script.

#### Q23: How does your Python service invoke MySQL's `mysqldump` on Windows?
*   **Answer**: The system uses Python's standard `subprocess.Popen` utility to execute OS-level command lines in the background. It dynamically resolves the path to MySQL's binaries (searching the system path or preconfigured settings) and launches:
   ```powershell
   mysqldump --user=root kicsit_library > filepath.sql
   ```
   The process captures execution streams (stdout/stderr) to log the backup results and reports errors immediately if the database snapshot fails.

#### Q24: What fields are logged in the `backups` history ledger?
*   **Answer**: The `backups` table logs comprehensive metadata: the backup filename, absolute file system path, file size in bytes, creation timestamp, status (Success/Failed), operator username (retrieved from the active JWT session), and any error logs or custom operator remarks.

#### Q25: How does the system resolve MySQL binary paths on Windows if they are not in the environment PATH?
*   **Answer**: The `backup_service` is built with a resilient fallback directory system. If a simple command call fails, the backup utility programmatically checks standard Windows folders where MySQL is commonly installed, such as XAMPP (`C:\xampp\mysql\bin`), Laragon (`C:\laragon\bin\mysql\mysql-X.X\bin`), or native Windows MySQL Server (`C:\Program Files\MySQL\MySQL Server X.X\bin`).

---

### Category F: Advanced ERP & Analytical Business Logic

#### Q26: How does your circulation system calculate daily overdue fines?
*   **Answer**: When a book copy is returned, the check-in service calculates the difference in days between the actual check-in date and the calculated due date. If the delta is positive (overdue), the service fetches the daily overdue fine constant from the dynamic settings table and multiplies it by the number of overdue days, logging the resulting balance as an unpaid item in the `fines` ledger.

#### Q27: How does the system handle book reservations and hold durations?
*   **Answer**: If a book copy is reserved, it is marked as `Reserved` in the copy status registry. A reservation record tracks the hold creation timestamp. When a librarian loads the circulation module, the system evaluates all active reservations. If a reservation has exceeded the "Reservation Hold Duration" (e.g., 3 days, as defined in system settings) without being picked up, the hold is marked as `Expired`, and the book copy's status is reset to `Available`.

#### Q28: How does Chart.js load data from your backend databases?
*   **Answer**: In the dashboard router, the database is queried to fetch structural datasets (e.g., counting book copies grouped by status). The lists are structured in the Python route, converted to JSON arrays, and safely injected into the Jinja2 JavaScript context using the `| tojson | safe` filters. This allows Chart.js to initialize visual charts instantly on the client side without needing separate asynchronous fetch requests.

#### Q29: What is an index in MySQL, and how did you optimize your schemas?
*   **Answer**: An index is a database data structure (typically a B-Tree) that improves the speed of data retrieval operations on a table at the cost of additional write overhead. In this system, indexes are created on heavily searched columns like `isbn` in the catalog table, `barcode` in the book copies table, and `username` in the users table, ensuring instant query execution even as the database grows to hundreds of thousands of entries.

#### Q30: What is your database normalization level? Explain why.
*   **Answer**: The database schema is designed in **Third Normal Form (3NF)**. Every table has a primary key, all columns represent atomic attributes, all non-key fields are fully dependent on the primary key, and no transitive functional dependencies exist (e.g., book copy information points to the primary book metadata key, and consumer profile entries are decoupled from circulation records). This prevents data anomalies, ensures consistency, and minimizes storage redundancy.
