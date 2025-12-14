# UTAMU Voting System (UVS)

A desktop-based electronic voting system built for **UTAMU** using Python and Tkinter.  
The system supports **secure admin management**, **student self-registration**, **position-based voting**, and **real-time poll results**, all backed by an SQLite database.

##  Main Features

### Admin Module

- **Admin Login**
  - Default admin credentials (on first run):  
    - **Username:** `admin`  
    - **Password:** `admin123`
  - On first login with the default password, the system **forces a password change** for better security.
  - Admin can later change their password via:
    - **Forced change on first login**, and  
    - **“Forgot Password” → Reset password** if they forget it.

- **Forgot Password (Admin Password Reset and Student password Rest)**
  - From the login window, admin/student can click **“Forgot Password”**.
  - The system opens a **Reset Password** window and hides the login window.
  - Admin enters:
    - Username
    - Reset Key
    - New password
    - Confirm new password
  - Student Enters:
    - username
    - reg number
    - New password
    - confirm new password
  - If the username is valid, the password is updated in the database.
  - On success, the reset window closes and the **login window is shown again**.
  - A **“Cancel”** button allows the admin to go back to the login screen without changing anything.

- **Candidate Management**
  - Register new candidates with:
    - Name
    - Position (from managed positions table)
    - Photo (image file from disk)
    - Logo (optional image file from disk)
  - View all registered candidates with:
    - Photo
    - Logo
    - Name
    - Position
    - Total votes
  - Manage candidates:
    - Edit candidate details (name, position, photo, logo)
    - Delete candidate

- **Position Management**
  - Add new positions (e.g. *Guild President*, *Class Representative*, etc.)
  - Delete existing positions
  - Positions are used both in registration and the student voting interface.

- **Voting Duration**
  - Set a **start** and **end** date/time for the voting period.
  - System checks if voting is open before allowing students to vote.
  - Countdown timer displayed on student side.

- **Poll Status / Results**
  - View current poll results grouped by position.
  - Shows:
    - Candidate name
    - Photo & logo
    - Total votes
  - Ordered by position.

- **Reset Votes**
  - Admin can reset:
    - All candidate vote counts to `0`
    - All students’ `has_voted` status back to *not voted*


### Student Module

- **Student Registration**
  - Students can create their own accounts with:
    - Full name
    - Username
    - Registration number
    - Password (with confirmation)

- **Login**
  - Students log in with their username and password.
  - After logging in, they access the **Vote Dashboard**.

- **Cast Vote**
  - For each position (e.g. *Guild President*, *Class Representative*), students:
    - See candidate **photos**, **logos**, and **names**
    - Select **at most one candidate per position**
    - Can **change their mind before submitting**:
      - Clicking the big checkbox-style label (☐ / ☑) selects/unselects a candidate.
  - Once votes are submitted:
    - Votes are recorded per candidate
    - Student is marked as **has_voted = 1**
    - Student cannot vote again.

- **View Poll Status**
  - Students can see current poll results (same data as admin view, but read-only).

- **Logout**
  - Returns to login window.

## Tech Stack

- **Language:** Python 3.x
- **GUI:** Tkinter
- **Database:** SQLite (`voting_system.db`)
- **Images:** Pillow (`PIL` / `Pillow` package)

## Project Structure

Typical project layout:

```text
UVS_version_5/
├─ main.py
├─ admin_panel.py
├─ student_panel.py
├─ database.py
├─ utils.py
├─ voting_system.db         # Auto-created if not present (SQLite DB)
└─ (Optional image folders, icons, etc.)
