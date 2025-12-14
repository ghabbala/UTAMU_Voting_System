# main.py
import tkinter as tk
from tkinter import messagebox

from utils import THEME_RED, THEME_WHITE, center_window
from admin_panel import AdminPanel
from student_panel import StudentPanel
from database import DatabaseManager

# Secret reset key for admin forgotten-password
MASTER_RESET_KEY = "UTAMU-RESET-2025"  # <-- change this to whatever you want


class MainWindow:
    def __init__(self):
        self.db = DatabaseManager()
        self.student_panel = StudentPanel()
        self.root = None
        self.username_entry = None
        self.password_entry = None

    def run(self):
        self.root = tk.Tk()
        self.root.title("Login")
        center_window(self.root, 480, 420)
        self.root.configure(bg=THEME_WHITE)
        self.root.resizable(False, False)

        frame = tk.Frame(
            self.root,
            bg=THEME_WHITE,
            highlightbackground=THEME_RED,
            highlightthickness=2,
        )
        frame.place(relx=0.5, rely=0.5, anchor="center", width=380, height=380)

        tk.Label(
            frame,
            text="UTAMU Voting System",
            font=("Segoe UI", 15, "bold"),
            bg=THEME_WHITE,
            fg=THEME_RED,
        ).pack(pady=12)

        form = tk.Frame(frame, bg=THEME_WHITE)
        form.pack(pady=4)

        tk.Label(form, text="Username:", bg=THEME_WHITE, fg=THEME_RED).grid(
            row=0, column=0, sticky="e", padx=6, pady=8
        )
        self.username_entry = tk.Entry(form, width=26)
        self.username_entry.grid(row=0, column=1, padx=6, pady=8)

        tk.Label(form, text="Password:", bg=THEME_WHITE, fg=THEME_RED).grid(
            row=1, column=0, sticky="e", padx=6, pady=8
        )
        self.password_entry = tk.Entry(form, show="*", width=26)
        self.password_entry.grid(row=1, column=1, padx=6, pady=8)

        tk.Button(
            frame,
            text="Login",
            bg=THEME_RED,
            fg=THEME_WHITE,
            width=18,
            command=self._attempt_login,
        ).pack(pady=8)

        # Forgot Password button
        tk.Button(
            frame,
            text="Forgot Password?",
            bg=THEME_WHITE,
            fg=THEME_RED,
            relief="flat",
            command=self._show_forgot_password,
        ).pack(pady=(0, 4))

        tk.Label(
            frame,
            text="Don't have an account?",
            bg=THEME_WHITE,
        ).pack(pady=(4, 2))

        tk.Button(
            frame,
            text="Create Account",
            bg=THEME_WHITE,
            fg=THEME_RED,
            relief="flat",
            command=self.show_registration,
        ).pack()

        tk.Label(
            frame,
            text="© 2025 UTAMU Voting System",
            font=("Segoe UI", 8),
            bg=THEME_WHITE,
            fg="gray",
        ).pack(side="bottom", pady=2)

        self.root.mainloop()

    # ----------------- LOGIN LOGIC -----------------
    def _attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        # 1️⃣ Check if user is Admin first
        admin = self.db.verify_admin(username, password)
        if admin:
            # If still using the default password, force change
            if password == "admin123":
                self._show_change_admin_password(username)
                return

            # Otherwise proceed to admin dashboard
            self.root.withdraw()
            self.show_dashboard()
            return

        # 2️⃣ Otherwise check Student
        student = self.db.verify_student(username, password)
        if student:
            self.root.withdraw()
            # student[3] is regno (from your original code)
            self.show_voting_window(student[3])
            return

        # 3️⃣ Invalid credentials
        messagebox.showerror("Login Failed", "Invalid username or password.")

    # ----------------- FORCE CHANGE DEFAULT ADMIN PASSWORD -----------------
    def _show_change_admin_password(self, username):
        """Force admin to change default password before continuing."""
        win = tk.Toplevel(self.root)
        win.title("Change Default Admin Password")
        center_window(win, 420, 230)
        win.configure(bg=THEME_WHITE)
        win.resizable(False, False)

        frame = tk.Frame(win, bg=THEME_WHITE)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(
            frame,
            text="You are using the default admin password.\nPlease set a new password before continuing.",
            bg=THEME_WHITE,
            fg=THEME_RED,
            font=("Segoe UI", 10, "bold"),
            justify="left",
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        tk.Label(frame, text="New Password:", bg=THEME_WHITE).grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        new_pass_var = tk.StringVar()
        new_pass_entry = tk.Entry(frame, textvariable=new_pass_var, show="*", width=26)
        new_pass_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame, text="Confirm Password:", bg=THEME_WHITE).grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        confirm_var = tk.StringVar()
        confirm_entry = tk.Entry(
            frame, textvariable=confirm_var, show="*", width=26
        )
        confirm_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        def save_new_password():
            new_pwd = new_pass_var.get().strip()
            confirm_pwd = confirm_var.get().strip()

            if not new_pwd or not confirm_pwd:
                messagebox.showwarning("Input Error", "Please fill in both fields.")
                return

            if new_pwd != confirm_pwd:
                messagebox.showwarning("Mismatch", "Passwords do not match.")
                return

            if new_pwd == "admin123":
                messagebox.showwarning(
                    "Weak Password",
                    "You cannot use the default password again. Choose a different one.",
                )
                return

            if len(new_pwd) < 6:
                messagebox.showwarning(
                    "Weak Password",
                    "Password should be at least 6 characters long.",
                )
                return

            self.db.update_admin_password(username, new_pwd)
            messagebox.showinfo("Success", "Password updated successfully.")

            win.destroy()
            # After changing, go straight to admin dashboard
            self.root.withdraw()
            self.show_dashboard()

        tk.Button(
            frame,
            text="Save New Password",
            bg="#0078D7",
            fg="white",
            relief="flat",
            padx=12,
            pady=4,
            command=save_new_password,
        ).grid(row=3, column=0, columnspan=2, pady=12)

        new_pass_entry.focus_set()

    # ----------------- FORGOT PASSWORD FLOW -----------------
    def _show_forgot_password(self):
        """Allow student or admin to reset password if they forgot it."""
        # Hide the login window
        self.root.withdraw()

        win = tk.Toplevel(self.root)
        win.title("Forgot Password")
        center_window(win, 430, 340)
        win.configure(bg=THEME_WHITE)
        win.resizable(False, False)

        frame = tk.Frame(win, bg=THEME_WHITE)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(
            frame,
            text="Reset Password",
            font=("Segoe UI", 12, "bold"),
            bg=THEME_WHITE,
            fg=THEME_RED,
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        # Account type: Student or Admin
        tk.Label(frame, text="Account Type:", bg=THEME_WHITE).grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        account_type_var = tk.StringVar(value="Student")

        rb_student = tk.Radiobutton(
            frame,
            text="Student",
            variable=account_type_var,
            value="Student",
            bg=THEME_WHITE,
            anchor="w",
        )
        rb_student.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        rb_admin = tk.Radiobutton(
            frame,
            text="Admin",
            variable=account_type_var,
            value="Admin",
            bg=THEME_WHITE,
            anchor="w",
        )
        rb_admin.grid(row=1, column=1, padx=80, pady=5, sticky="w")

        # Username
        tk.Label(frame, text="Username:", bg=THEME_WHITE).grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        username_var = tk.StringVar()
        username_entry = tk.Entry(frame, textvariable=username_var, width=26)
        username_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Extra field: Reg. Number (for student) or Reset Key (for admin)
        extra_label = tk.Label(frame, text="Reg. Number:", bg=THEME_WHITE)
        extra_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        extra_var = tk.StringVar()
        extra_entry = tk.Entry(frame, textvariable=extra_var, width=26)
        extra_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        def on_type_change(*args):
            if account_type_var.get() == "Student":
                extra_label.config(text="Reg. Number:")
                extra_var.set("")
            else:
                extra_label.config(text="Reset Key:")
                extra_var.set("")

        account_type_var.trace_add("write", on_type_change)

        # New password
        tk.Label(frame, text="New Password:", bg=THEME_WHITE).grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        new_pass_var = tk.StringVar()
        new_pass_entry = tk.Entry(frame, textvariable=new_pass_var, show="*", width=26)
        new_pass_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Confirm password
        tk.Label(frame, text="Confirm Password:", bg=THEME_WHITE).grid(
            row=5, column=0, padx=5, pady=5, sticky="e"
        )
        confirm_var = tk.StringVar()
        confirm_entry = tk.Entry(
            frame, textvariable=confirm_var, show="*", width=26
        )
        confirm_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        def back_to_login():
            """Close reset window and show login again."""
            win.destroy()
            # Clear password entry on the login form (optional)
            if self.password_entry is not None:
                self.password_entry.delete(0, tk.END)
            self.root.deiconify()

        def do_reset():
            acc_type = account_type_var.get()
            username = username_var.get().strip()
            extra = extra_var.get().strip()
            new_pwd = new_pass_var.get().strip()
            confirm_pwd = confirm_var.get().strip()

            if not username or not extra or not new_pwd or not confirm_pwd:
                messagebox.showwarning("Input Error", "Please fill in all fields.")
                return

            if new_pwd != confirm_pwd:
                messagebox.showwarning("Mismatch", "Passwords do not match.")
                return

            if len(new_pwd) < 6:
                messagebox.showwarning(
                    "Weak Password",
                    "Password should be at least 6 characters long.",
                )
                return

            if acc_type == "Student":
                # extra = regno
                success = self.db.reset_student_password(username, extra, new_pwd)
                if not success:
                    messagebox.showerror(
                        "Not Found",
                        "No student found with that username and registration number.",
                    )
                    return
                #messagebox.showinfo("Success", "Student password reset successfully.")
                back_to_login()
            else:
                # Admin – extra must match the master reset key
                if extra != MASTER_RESET_KEY:
                    messagebox.showerror(
                        "Invalid Reset Key",
                        "The reset key is incorrect. Contact the system owner.",
                    )
                    return

                self.db.update_admin_password(username, new_pwd)
                messagebox.showinfo("Success", "Admin password reset successfully.")
                back_to_login()

        btn_frame = tk.Frame(frame, bg=THEME_WHITE)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=15)

        tk.Button(
            btn_frame,
            text="Reset Password",
            bg="#0078D7",
            fg="white",
            relief="flat",
            padx=12,
            pady=4,
            command=do_reset,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Cancel",
            bg="#CCCCCC",
            fg="black",
            relief="flat",
            padx=12,
            pady=4,
            command=back_to_login,
        ).pack(side="left", padx=5)

        # If user clicks the window X, behave like Cancel
        win.protocol("WM_DELETE_WINDOW", back_to_login)

        username_entry.focus_set()

    # ----------------- OTHER HELPERS -----------------
    def show_voting_window(self, reg_no):
        self.student_panel.show_voting_window(reg_no)

    def show_dashboard(self):
        AdminPanel().show_dashboard()

    def show_registration(self):
        # delegate to student panel's registration UI
        self.student_panel.show_registration()


if __name__ == "__main__":
    MainWindow().run()
