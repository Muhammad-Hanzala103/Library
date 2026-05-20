# KICSIT Library Management System - Deployment & Installation Guide

This deployment and installation manual provides comprehensive, step-by-step instructions for installing, configuring, running, and exposing the **KICSIT Library Management System** over a local network.

---

## 1. Prerequisites & Environment Setup

The system is optimized for **Windows 10/11** and is designed to operate seamlessly in a university intranet environment.

### A. Python Installation
1. Download **Python 3.10** or higher (3.10.x - 3.12.x recommended) from the [Official Python Website](https://www.python.org/downloads/).
2. Run the installer and **CRITICAL**: Check the box **"Add Python.exe to PATH"** before proceeding with the installation.
3. Verify the installation via PowerShell:
   ```powershell
   python --version
   pip --version
   ```

### B. MySQL Database Installation (XAMPP / Laragon / Native)
The system requires a running **MySQL Server** instance. You can install it natively or via a bundled stack:
* **Option A (Recommended): XAMPP**
  1. Download and install [XAMPP for Windows](https://www.apachefriends.org/index.html).
  2. Open the **XAMPP Control Panel** and click **Start** next to the **MySQL** module.
  3. Ensure it runs on default port `3306`.
* **Option B: Native MySQL Server**
  1. Download and install MySQL Community Server.
  2. Setup root user credentials.

---

## 2. Codebase Initialization & Dependency Management

1. Extract the project codebase (`kicsitLibrarySystem`) into your target directory:
   ```powershell
   cd c:\Projects\Library\kicsitLibrarySystem
   ```
2. **Create a Python Virtual Environment (`.venv`):**
   ```powershell
   python -m venv .venv
   ```
3. **Activate the Virtual Environment:**
   * In PowerShell:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   * In command prompt:
     ```cmd
     .venv\Scripts\activate.bat
     ```
4. **Install Required Packages:**
   With active `.venv`, run:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 3. Configuration of Environment Files (`.env`)

Create a `.env` file in the root folder `c:\Projects\Library\kicsitLibrarySystem` by copying `.env.example`:

```ini
DATABASE_URL=mysql+pymysql://root:@localhost:3306/kicsit_library
SECRET_KEY=kicsit_super_secure_secret_hash_key_2026_hanzala
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
APP_NAME="KICSIT Library System"
```

*Note: If your MySQL server has a password, update the URL: `mysql+pymysql://username:password@localhost:3306/kicsit_library`.*

---

## 4. Database Setup, Migrations & Seeding

1. **Create the Database:**
   Open a MySQL shell or `phpMyAdmin` (typically at `http://localhost/phpmyadmin` via XAMPP) and run:
   ```sql
   CREATE DATABASE kicsit_library CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. **Execute Alembic Database Migrations:**
   Generate the tables, relationships, constraints, and indexes:
   ```powershell
   alembic upgrade head
   ```
3. **Seed Database Defaults & Accounts:**
   Seed system settings, permissions, roles, and pre-configured administrative accounts:
   ```powershell
   python -m app.seed
   ```

### Default Accounts Seeded:
* **Super Admin**: Username `superadmin` | Password `ChangeMe@123` (Full systems access + Backup/Restore controls)
* **Admin**: Username `admin` | Password `ChangeMe@123` (Access to settings and forms)
* **Librarian**: Username `librarian` | Password `ChangeMe@123` (Standard borrowing actions)
* **Assistant**: Username `assistant` | Password `ChangeMe@123` (Basic check-in/check-out)

---

## 5. Local Network (Intranet) Sharing & Access

To allow other computers (librarian terminals, student laptops, student clearance counters) on the KICSIT intranet to access the system:

### Step A: Find the Server Host's Local IP Address
In PowerShell, run:
```powershell
ipconfig
```
Locate the IPv4 Address under your active network adapter (e.g., `192.168.10.45`).

### Step B: Configure Windows Defender Firewall
To allow incoming traffic on Uvicorn's port (default `8000`):
1. Press `Win + R`, type `wf.msc`, and press **Enter** to open **Windows Defender Firewall with Advanced Security**.
2. Click **Inbound Rules** (left panel), then click **New Rule...** (right panel).
3. Select **Port** and click **Next**.
4. Select **TCP** and specify **Specific local ports**: `8000`. Click **Next**.
5. Select **Allow the connection** and click **Next**.
6. Keep all profile checkboxes (Domain, Private, Public) checked and click **Next**.
7. Name the rule **"KICSIT Library Server Access"** and click **Finish**.

### Step C: Run the Application Bound to Host IP
By default, running `uvicorn` binds to `127.0.0.1` (localhost only). To host it to the network, bind to `0.0.0.0` (all adapters):
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step D: Access the Web App on Client Machines
On any other client machine connected to the same KICSIT Wi-Fi/Intranet network, open a web browser and navigate to:
```
http://192.168.10.45:8000/
```
*(Replace `192.168.10.45` with the server's actual local IP address)*.

---

## 6. Configuring Database Backups & Restore Binary Utilities

The system utilizes native MySQL utilities (`mysqldump.exe` and `mysql.exe`) for database backup and recovery.

1. **Verify Binary Availability:**
   Ensure `mysqldump` and `mysql` can be resolved in your system path.
   * If you are using XAMPP, they are located at `C:\xampp\mysql\bin`.
   * Add this folder to the **Windows System Environment PATH Variable** to allow immediate script execution.
2. **Dynamic Backup Path Settings:**
   * Navigate to **System Settings** in the dashboard navigation.
   * Set **Backup Directory File Path** to a folder where dumps should reside (e.g., `C:\Projects\Library\kicsitLibrarySystem\backups`).
   * The system will auto-create this folder upon the first backup trigger.
