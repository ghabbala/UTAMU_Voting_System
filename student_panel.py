# student_panel.py
import tkinter as tk
from tkinter import messagebox
from database import DatabaseManager
from utils import THEME_RED, THEME_WHITE, center_window
from PIL import Image, ImageTk
import os


class StudentPanel:
    def __init__(self, root=None):
        self.db = DatabaseManager()
        self._photo_cache = []  # prevent garbage collection of PhotoImage
        self.root = root
        self.content_frame = None

    # ---------- REGISTRATION ----------
    def show_registration(self):
        win = tk.Toplevel()
        win.title("Student Registration")
        center_window(win, 480, 460)
        win.configure(bg=THEME_WHITE)

        tk.Label(
            win,
            text="Create Your Account",
            font=("Segoe UI", 16, "bold"),
            bg=THEME_WHITE,
            fg=THEME_RED,
        ).pack(pady=12)

        form = tk.Frame(win, bg=THEME_WHITE)
        form.pack(pady=6)

        labels = [
            ("Full Name", "name"),
            ("Username", "username"),
            ("Reg. Number", "regno"),
            ("Password", "password"),
            ("Confirm Password", "confirm"),
        ]
        self._reg_entries = {}

        for i, (lab, key) in enumerate(labels):
            tk.Label(
                form,
                text=f"{lab}:",
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).grid(row=i, column=0, sticky="e", padx=6, pady=8)

            show = "*" if "password" in key else ""
            e = tk.Entry(form, show=show, width=28)
            e.grid(row=i, column=1, padx=6, pady=8)
            self._reg_entries[key] = e

        tk.Button(
            win,
            text="Create Account",
            bg=THEME_RED,
            fg=THEME_WHITE,
            command=lambda: self._register_student(win),
        ).pack(pady=12)

    def _register_student(self, win):
        name = self._reg_entries["name"].get().strip()
        username = self._reg_entries["username"].get().strip()
        regno = self._reg_entries["regno"].get().strip()
        password = self._reg_entries["password"].get().strip()
        confirm = self._reg_entries["confirm"].get().strip()

        if not all([name, username, regno, password, confirm]):
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        try:
            self.db.register_student(name, username, regno, password)
            messagebox.showinfo("Success", "Account created successfully!")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ---------- VOTING WINDOW ----------
    def show_voting_window(self, reg_no):
        # master = self.root (if provided) or default root
        win = tk.Toplevel(self.root)
        win.title("Vote Dashboard")
        center_window(win, 890, 650)
        win.configure(bg=THEME_WHITE)
        self.current_window = win

        # === Layout ===
        sidebar = tk.Frame(win, bg=THEME_RED, width=200)
        sidebar.pack(side="left", fill="y")

        self.content_frame = tk.Frame(win, bg=THEME_WHITE)
        self.content_frame.pack(side="right", fill="both", expand=True)

        # === Sidebar ===
        tk.Label(
            sidebar,
            text="UVS",
            fg=THEME_WHITE,
            bg=THEME_RED,
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=25)

        actions = [
            ("Vote", lambda: self._display_vote_screen(reg_no)),
            ("Poll Status", self._display_poll_status_screen),
            ("Log Out", lambda: self._go_back(win)),
        ]

        for text, cmd in actions:
            tk.Button(
                sidebar,
                text=text,
                bg=THEME_WHITE,
                fg=THEME_RED,
                font=("Arial", 11, "bold"),
                width=14,
                relief="flat",
                command=cmd,
            ).pack(pady=8)

        # Show Vote screen by default
        self._display_vote_screen(reg_no)

    # ---------- INTERNAL: refresh content ----------
    def display_content(self, builder_func):
        if self.content_frame is None:
            return
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        builder_func(self.content_frame)

    # ---------- VOTE SCREEN ----------
    def _display_vote_screen(self, reg_no):
        is_open, msg = self.db.is_voting_open()
        if not is_open:
            messagebox.showwarning("Voting Unavailable", msg)
            return

        def build(frame):
            tk.Label(
                frame,
                text="CAST YOUR VOTE",
                font=("Segoe UI", 18, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(pady=15)

            # === Countdown timer section ===
            from datetime import datetime

            duration = self.db.get_voting_duration()
            if not duration:
                tk.Label(
                    frame,
                    text="Voting period not set.",
                    bg=THEME_WHITE,
                    fg="red",
                ).pack(pady=5)
                return

            start_str, end_str = duration
            end_time = datetime.fromisoformat(end_str)

            countdown_label = tk.Label(
                frame,
                text="Calculating remaining time...",
                bg=THEME_WHITE,
                fg="#333",
                font=("Arial", 11, "bold"),
            )
            countdown_label.pack(pady=5)

            def update_countdown():
                now = datetime.now()
                remaining = end_time - now

                if remaining.total_seconds() <= 0:
                    countdown_label.config(
                        text="Voting period has ended.", fg="red"
                    )
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Button):
                            widget.config(state="disabled", text="Voting Closed")
                    return

                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                countdown_label.config(
                    text=f"Voting ends in: {hours:02d}h {minutes:02d}m {seconds:02d}s",
                    fg="#008000" if hours > 0 or minutes > 5 else "orange",
                )
                countdown_label.after(1000, update_countdown)

            update_countdown()

            # Already voted?
            if self.db.student_has_voted(reg_no):
                tk.Label(
                    frame,
                    text="You have already voted.",
                    bg=THEME_WHITE,
                    fg=THEME_RED,
                    font=("Arial", 12, "bold"),
                ).pack(pady=10)
                return

            positions = self.db.get_all_positions()
            self._photo_cache.clear()
            selections = {}  # position -> IntVar(candidate_id or 0)

            # === Scrollable area ===
            canvas = tk.Canvas(frame, bg=THEME_WHITE, highlightthickness=0)
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scroll_frame = tk.Frame(canvas, bg=THEME_WHITE)

            scroll_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
            )
            canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

                        # --- mouse wheel scrolling (bound only to this canvas) ---
            def _on_mousewheel(event, c=canvas):
                # If canvas has already been destroyed, just ignore the event
                if not c.winfo_exists():
                    return

                # Windows / MacOS: event.delta is non-zero
                if getattr(event, "delta", 0):
                    c.yview_scroll(int(-1 * (event.delta / 120)), "units")
                else:
                    # Linux: use Button-4 / Button-5
                    if event.num == 4:
                        c.yview_scroll(-1, "units")
                    elif event.num == 5:
                        c.yview_scroll(1, "units")

            # Bind only to this canvas, not globally
            canvas.bind("<MouseWheel>", _on_mousewheel)   # Windows/Mac
            canvas.bind("<Button-4>", _on_mousewheel)     # Linux up
            canvas.bind("<Button-5>", _on_mousewheel)     # Linux down


            # === Build position sections ===
            for position in positions:
                tk.Label(
                    scroll_frame,
                    text=position.upper(),
                    font=("Segoe UI", 13, "bold"),
                    bg=THEME_WHITE,
                    fg=THEME_RED,
                ).pack(anchor="w", padx=15, pady=(12, 4))

                group_box = tk.LabelFrame(
                    scroll_frame,
                    bg=THEME_WHITE,
                    padx=10,
                    pady=5,
                    highlightbackground=THEME_RED,
                    highlightthickness=1,
                )
                group_box.pack(fill="x", padx=20, pady=5)

                candidates = self.db.get_candidates(position=position)

                # IntVar to store selected candidate id for this position (0 = none)
                selections[position] = tk.IntVar(value=0)

                # cid -> (label_widget, name)
                labels_map = {}

                for cid, name, pos, votes, photo_path, logo_path in candidates:
                    row = tk.Frame(group_box, bg=THEME_WHITE)
                    row.pack(fill="x", pady=3)

                    # normalize paths
                    safe_photo = os.path.normpath((photo_path or "").strip()) if photo_path else ""
                    safe_logo = os.path.normpath((logo_path or "").strip()) if logo_path else ""

                    # Candidate photo
                    try:
                        if safe_photo and os.path.exists(safe_photo):
                            img = Image.open(safe_photo)
                        else:
                            raise FileNotFoundError
                        img = img.resize((120, 120))
                        photo = ImageTk.PhotoImage(img)
                    except Exception:
                        from PIL import Image as PILImage

                        placeholder = PILImage.new("RGB", (120, 120), color=(240, 240, 240))
                        photo = ImageTk.PhotoImage(placeholder)

                    self._photo_cache.append(photo)
                    tk.Label(row, image=photo, bg=THEME_WHITE).pack(
                        side="left", padx=20, pady=20
                    )

                    # Candidate logo
                    if safe_logo and os.path.exists(safe_logo):
                        try:
                            logo_img = Image.open(safe_logo).resize((120, 120))
                            logo_photo = ImageTk.PhotoImage(logo_img)
                            self._photo_cache.append(logo_photo)
                            tk.Label(row, image=logo_photo, bg=THEME_WHITE).pack(
                                side="left", padx=20, pady=20
                            )
                        except Exception:
                            pass

                    # Big "checkbox" label
                    display_text = f"☐ {name}"
                    lbl_choice = tk.Label(
                        row,
                        text=display_text,
                        bg=THEME_WHITE,
                        fg="#333333",
                        font=("Arial", 15, "bold"),
                        padx=10,
                        pady=8,
                        anchor="w",
                    )
                    lbl_choice.pack(side="left", padx=10)

                    labels_map[cid] = (lbl_choice, name)

                    def on_click(event, cid=cid, position=position, labels_map=labels_map):
                        current = selections[position].get()
                        # click same candidate again -> unselect
                        if current == cid:
                            selections[position].set(0)
                        else:
                            selections[position].set(cid)

                        selected_id = selections[position].get()
                        for other_cid, (other_lbl, other_name) in labels_map.items():
                            if other_cid == selected_id:
                                other_lbl.config(text=f"☑ {other_name}")
                            else:
                                other_lbl.config(text=f"☐ {other_name}")

                    lbl_choice.bind("<Button-1>", on_click)

            # === Submit votes ===
            def submit_votes():
                chosen_votes = {}
                for position, var in selections.items():
                    cid = var.get()
                    if cid != 0:
                        chosen_votes[position] = cid

                if not chosen_votes:
                    messagebox.showwarning(
                        "No Selection", "Please select at least one candidate."
                    )
                    return

                confirm = messagebox.askyesno(
                    "Confirm Vote", "Are you sure you want to submit your votes?"
                )
                if not confirm:
                    return

                try:
                    for position, cid in chosen_votes.items():
                        self.db.record_vote(reg_no, cid)
                    # After voting, show poll status screen
                    self._display_poll_status_screen()
                except Exception as e:
                    messagebox.showerror(
                        "Database Error",
                        f"An error occurred while submitting votes: {e}",
                    )

            tk.Button(
                frame,
                text="Submit Votes",
                bg=THEME_RED,
                fg=THEME_WHITE,
                font=("Segoe UI", 12, "bold"),
                width=20,
                relief="flat",
                command=submit_votes,
            ).pack(pady=20)

            tk.Label(
                frame,
                text=f"Voting open from {start_str} to {end_str}",
                bg=THEME_WHITE,
                fg="#555",
                font=("Arial", 10, "italic"),
            ).pack(pady=2)

        self.display_content(build)

    # ---------- POLL STATUS ----------
    def _display_poll_status_screen(self):
        def build(frame):
            tk.Label(
                frame, text="CURRENT POLL RESULTS",
                font=("Segoe UI", 18, "bold"),
                bg=THEME_WHITE, fg=THEME_RED
            ).pack(pady=12)

            from datetime import datetime
            duration = self.db.get_voting_duration()
            if not duration:
                tk.Label(
                    frame, text="Voting period not set.",
                    bg=THEME_WHITE, fg="red"
                ).pack(pady=5)
                return

            start_str, end_str = duration
            end_time = datetime.fromisoformat(end_str)

            countdown_label = tk.Label(
                frame,
                text="Calculating remaining time...",
                bg=THEME_WHITE,
                fg="#333",
                font=("Arial", 11, "bold")
            )
            countdown_label.pack(pady=5)

            def update_countdown():
                now = datetime.now()
                remaining = end_time - now

                if remaining.total_seconds() <= 0:
                    countdown_label.config(text="Voting period has ended.", fg="red")
                    # disable all buttons if time expires
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Button):
                            widget.config(state="disabled", text="Voting Closed")
                    return

                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                countdown_label.config(
                    text=f"Voting ends in: {hours:02d}h {minutes:02d}m {seconds:02d}s",
                    fg="#008000" if hours > 0 or minutes > 5 else "orange"
                )

                countdown_label.after(1000, update_countdown)

            update_countdown()

            # ==== scrollable area ====
            canvas = tk.Canvas(frame, bg=THEME_WHITE, highlightthickness=0)
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            inner = tk.Frame(canvas, bg=THEME_WHITE)

            inner.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=inner, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # mouse-wheel scrolling (safe even after window is closed)
            def _on_mousewheel(event):
                if not canvas.winfo_exists():
                    return
                if hasattr(event, "delta") and event.delta:
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                else:  # Linux
                    if event.num == 4:
                        canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        canvas.yview_scroll(1, "units")

            canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
            canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

            self._photo_cache.clear()

            positions = self.db.get_all_positions()
            for pos in positions:
                tk.Label(
                    inner, text=pos.upper(),
                    font=("Segoe UI", 14, "bold"),
                    bg=THEME_WHITE, fg=THEME_RED
                ).pack(anchor="w", padx=15, pady=(14, 6))

                candidates = self.db.get_candidates(position=pos)
                for cid, name, position, votes, photo_path, logo_path in candidates:
                    cf = tk.Frame(
                        inner,
                        bg="#f9f9f9",
                        highlightbackground="#ffcccc",
                        highlightthickness=1
                    )
                    cf.pack(fill="x", padx=25, pady=5)

                    # --- normalise paths (THIS FIXES YOUR MISSING PHOTO) ---
                    safe_photo = (photo_path or "").strip()
                    safe_logo = (logo_path or "").strip()
                    if safe_photo:
                        safe_photo = os.path.normpath(safe_photo)
                    if safe_logo:
                        safe_logo = os.path.normpath(safe_logo)

                    # === Candidate photo ===
                    try:
                        if safe_photo and os.path.exists(safe_photo):
                            img = Image.open(safe_photo)
                        else:
                            raise FileNotFoundError
                        img = img.resize((120, 120))
                        photo = ImageTk.PhotoImage(img)
                    except Exception:
                        from PIL import Image
                        photo = ImageTk.PhotoImage(
                            Image.new("RGB", (120, 120), color=(240, 200, 200))
                        )

                    tk.Label(cf, image=photo, bg="#f9f9f9").pack(
                        side="left", padx=20, pady=20
                    )
                    self._photo_cache.append(photo)

                    # === Candidate logo ===
                    if safe_logo and os.path.exists(safe_logo):
                        try:
                            logo_img = Image.open(safe_logo).resize((120, 120))
                            logo_photo = ImageTk.PhotoImage(logo_img)
                            self._photo_cache.append(logo_photo)
                            tk.Label(cf, image=logo_photo, bg="#f9f9f9").pack(
                                side="left", padx=20, pady=20
                            )
                        except Exception:
                            pass

                    # === Text info ===
                    tk.Label(
                        cf, text=f"{name}\nVotes: {votes}",
                        bg="#f9f9f9", fg="#333333",
                        justify="left", font=("Arial", 11, "bold")
                    ).pack(side="left", padx=10, pady=8)

        self.display_content(build)



    # ---------- GO BACK / LOG OUT ----------
    def _go_back(self, win=None):
        try:
            if win:
                win.destroy()
            elif hasattr(self, "root") and self.root is not None:
                self.root.destroy()
        except Exception:
            pass

        from main import MainWindow

        app = MainWindow()
        app.run()
