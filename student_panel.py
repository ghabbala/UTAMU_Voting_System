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
        parent = self.root if self.root is not None else None
        win = tk.Toplevel(parent)
        win.title("Student Registration")
        center_window(win, 480, 460)
        win.configure(bg=THEME_WHITE)

        # allow resizing
        win.resizable(True, True)

        # Main container (responsive)
        main = tk.Frame(win, bg=THEME_WHITE)
        main.pack(fill="both", expand=True, padx=16, pady=16)

        # Header
        tk.Label(
            main,
            text="Create Your Account",
            font=("Segoe UI", 16, "bold"),
            bg=THEME_WHITE,
            fg=THEME_RED,
        ).pack(anchor="w", pady=(0, 12))

        # Form container
        form = tk.Frame(main, bg=THEME_WHITE)
        form.pack(pady=6, fill="x", expand=False)

        # Let the entry column expand when window widens
        form.columnconfigure(0, weight=0)  # labels
        form.columnconfigure(1, weight=1)  # entries

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
            e.grid(row=i, column=1, padx=6, pady=8, sticky="we")
            self._reg_entries[key] = e

        # Button row
        btn_frame = tk.Frame(main, bg=THEME_WHITE)
        btn_frame.pack(fill="x", pady=12)

        tk.Button(
            btn_frame,
            text="Create Account",
            bg=THEME_RED,
            fg=THEME_WHITE,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            command=lambda: self._register_student(win),
        ).pack(pady=4, ipadx=10, ipady=4)

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
        parent = self.root if self.root is not None else None
        win = tk.Toplevel(parent)
        win.title("Vote Dashboard")
        center_window(win, 890, 650)
        win.configure(bg=THEME_WHITE)

        # allow resizing
        win.resizable(True, True)
        self.current_window = win

        # Main layout container (grid, responsive)
        main = tk.Frame(win, bg=THEME_WHITE)
        main.pack(fill="both", expand=True)

        # Configure grid so right side grows
        main.columnconfigure(0, weight=0)  # sidebar fixed width
        main.columnconfigure(1, weight=1)  # content grows
        main.rowconfigure(0, weight=1)

        # Sidebar
        sidebar = tk.Frame(main, bg=THEME_RED, width=200)
        sidebar.grid(row=0, column=0, sticky="nsw")

        # Make sidebar fill vertically
        sidebar.grid_propagate(False)
        sidebar.rowconfigure(0, weight=0)
        sidebar.rowconfigure(1, weight=1)

        tk.Label(
            sidebar,
            text="UVS",
            fg=THEME_WHITE,
            bg=THEME_RED,
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, pady=(25, 10), padx=10, sticky="n")

        # Buttons container inside sidebar
        btn_container = tk.Frame(sidebar, bg=THEME_RED)
        btn_container.grid(row=1, column=0, sticky="n", padx=10, pady=10)

        actions = [
            ("Vote", lambda: self._display_vote_screen(reg_no)),
            ("Poll Status", self._display_poll_status_screen),
            ("Log Out", lambda: self._go_back(win)),
        ]

        for text, cmd in actions:
            tk.Button(
                btn_container,
                text=text,
                bg=THEME_WHITE,
                fg=THEME_RED,
                font=("Arial", 11, "bold"),
                width=14,
                relief="flat",
                command=cmd,
            ).pack(pady=8, fill="x")

        # Content frame (responsive)
        self.content_frame = tk.Frame(main, bg=THEME_WHITE)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)

        # Show Vote screen by default
        self._display_vote_screen(reg_no)

    # ---------- INTERNAL: refresh content ----------
    def display_content(self, builder_func):
        if self.content_frame is None:
            return
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Wrap builder in a root frame that expands
        root_inner = tk.Frame(self.content_frame, bg=THEME_WHITE)
        root_inner.grid(row=0, column=0, sticky="nsew")
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)

        builder_func(root_inner)

    # ---------- VOTE SCREEN ----------
    def _display_vote_screen(self, reg_no):
        is_open, msg = self.db.is_voting_open()
        if not is_open:
            messagebox.showwarning("Voting Unavailable", msg)
            return

        def build(frame):
            frame.rowconfigure(2, weight=1)
            frame.columnconfigure(0, weight=1)

            tk.Label(
                frame,
                text="CAST YOUR VOTE",
                font=("Segoe UI", 18, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).grid(row=0, column=0, pady=10, sticky="n")

            # Countdown timer section
            from datetime import datetime

            duration = self.db.get_voting_duration()
            if not duration:
                tk.Label(
                    frame,
                    text="Voting period not set.",
                    bg=THEME_WHITE,
                    fg="red",
                ).grid(row=1, column=0, pady=5)
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
            countdown_label.grid(row=1, column=0, pady=5)

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
                ).grid(row=2, column=0, pady=10)
                return

            positions = self.db.get_all_positions()
            self._photo_cache.clear()
            selections = {}  # position -> IntVar(candidate_id or 0)

            # Scrollable area
            list_container = tk.Frame(frame, bg=THEME_WHITE)
            list_container.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
            frame.rowconfigure(3, weight=1)

            canvas = tk.Canvas(list_container, bg=THEME_WHITE, highlightthickness=0)
            scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
            scroll_frame = tk.Frame(canvas, bg=THEME_WHITE)

            scroll_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
            )
            canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            def _on_mousewheel(event, c=canvas):
                if not c.winfo_exists():
                    return
                if getattr(event, "delta", 0):
                    c.yview_scroll(int(-1 * (event.delta / 120)), "units")
                else:
                    if event.num == 4:
                        c.yview_scroll(-1, "units")
                    elif event.num == 5:
                        c.yview_scroll(1, "units")

            canvas.bind("<MouseWheel>", _on_mousewheel)
            canvas.bind("<Button-4>", _on_mousewheel)
            canvas.bind("<Button-5>", _on_mousewheel)

            # Build position sections
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
                selections[position] = tk.IntVar(value=0)
                labels_map = {}

                for cid, name, pos, votes, photo_path, logo_path in candidates:
                    row = tk.Frame(group_box, bg=THEME_WHITE)
                    row.pack(fill="x", pady=3)

                    safe_photo = os.path.normpath((photo_path or "").strip()) if photo_path else ""
                    safe_logo = os.path.normpath((logo_path or "").strip()) if logo_path else ""

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

            footer = tk.Frame(frame, bg=THEME_WHITE)
            footer.grid(row=4, column=0, pady=10)

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
                    # After voting show poll status
                    self._display_poll_status_screen()
                except Exception as e:
                    messagebox.showerror(
                        "Database Error",
                        f"An error occurred while submitting votes: {e}",
                    )

            tk.Button(
                footer,
                text="Submit Votes",
                bg=THEME_RED,
                fg=THEME_WHITE,
                font=("Segoe UI", 12, "bold"),
                width=20,
                relief="flat",
                command=submit_votes,
            ).pack(pady=5)

            tk.Label(
                footer,
                text=f"Voting open from {start_str} to {end_str}",
                bg=THEME_WHITE,
                fg="#555",
                font=("Arial", 10, "italic"),
            ).pack(pady=2)

        self.display_content(build)

    # ---------- POLL STATUS ----------
       # ---------- POLL STATUS ----------
       # ---------- POLL STATUS ----------
        # ---------- POLL STATUS ----------
    def _display_poll_status_screen(self):
        def build(frame):
            from datetime import datetime

            # Make main grid responsive
            frame.rowconfigure(1, weight=1)
            frame.columnconfigure(0, weight=3)  # left: list with photos
            frame.columnconfigure(1, weight=2)  # right: analytics

            # ===== HEADER + COUNTDOWN (top, spans both columns) =====
            header = tk.Frame(frame, bg=THEME_WHITE)
            header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(8, 4))
            header.columnconfigure(0, weight=1)

            tk.Label(
                header,
                text="CURRENT POLL RESULTS",
                font=("Segoe UI", 18, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).grid(row=0, column=0, pady=(0, 4), sticky="n")

            duration = self.db.get_voting_duration()
            if not duration:
                tk.Label(
                    header,
                    text="Voting period not set.",
                    bg=THEME_WHITE,
                    fg="red",
                ).grid(row=1, column=0, pady=5)
                return

            start_str, end_str = duration
            end_time = datetime.fromisoformat(end_str)

            countdown_label = tk.Label(
                header,
                text="Calculating remaining time...",
                bg=THEME_WHITE,
                fg="#333",
                font=("Arial", 11, "bold"),
            )
            countdown_label.grid(row=1, column=0, pady=4)

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
                    fg="#008000" if hours > 0 or minutes > 5 else "orange",
                )
                countdown_label.after(1000, update_countdown)

            update_countdown()

            # ===== MAIN AREA: LEFT (CARDS) + RIGHT (ANALYTICS) =====
            main = tk.Frame(frame, bg=THEME_WHITE)
            main.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
            main.columnconfigure(0, weight=3)
            main.columnconfigure(1, weight=2)
            main.rowconfigure(0, weight=1)

            # ---------------- LEFT: SCROLLABLE CARDS WITH PICS/LOGOS ----------------
            list_container = tk.Frame(main, bg=THEME_WHITE)
            list_container.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
            list_container.rowconfigure(0, weight=1)
            list_container.columnconfigure(0, weight=1)

            canvas = tk.Canvas(list_container, bg=THEME_WHITE, highlightthickness=0)
            scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
            inner = tk.Frame(canvas, bg=THEME_WHITE)

            inner.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
            )
            canvas.create_window((0, 0), window=inner, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.grid(row=0, column=0, sticky="nsew")
            scrollbar.grid(row=0, column=1, sticky="ns")

            # --- Mouse wheel scrolling only affects this canvas/inner ---
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

            # Bind to both canvas and inner so scrolling works over the cards
            for widget in (canvas, inner):
                widget.bind("<MouseWheel>", _on_mousewheel)   # Windows / Mac
                widget.bind("<Button-4>", _on_mousewheel)     # Linux up
                widget.bind("<Button-5>", _on_mousewheel)     # Linux down)

            # Keep photos/logos EXACTLY as before
            self._photo_cache.clear()
            positions = self.db.get_all_positions()

            for pos in positions:
                tk.Label(
                    inner,
                    text=pos.upper(),
                    font=("Segoe UI", 14, "bold"),
                    bg=THEME_WHITE,
                    fg=THEME_RED,
                ).pack(anchor="w", padx=15, pady=(14, 6))

                candidates = self.db.get_candidates(position=pos)
                for cid, name, position, votes, photo_path, logo_path in candidates:
                    cf = tk.Frame(
                        inner,
                        bg="#f9f9f9",
                        highlightbackground="#ffcccc",
                        highlightthickness=1,
                    )
                    cf.pack(fill="x", padx=25, pady=5)

                    safe_photo = (photo_path or "").strip()
                    safe_logo = (logo_path or "").strip()
                    if safe_photo:
                        safe_photo = os.path.normpath(safe_photo)
                    if safe_logo:
                        safe_logo = os.path.normpath(safe_logo)

                    # Photo
                    try:
                        if safe_photo and os.path.exists(safe_photo):
                            img = Image.open(safe_photo)
                        else:
                            raise FileNotFoundError
                        img = img.resize((120, 120))
                        photo = ImageTk.PhotoImage(img)
                    except Exception:
                        from PIL import Image as PILImage

                        photo = ImageTk.PhotoImage(
                            PILImage.new("RGB", (120, 120), color=(240, 200, 200))
                        )

                    tk.Label(cf, image=photo, bg="#f9f9f9").pack(
                        side="left", padx=20, pady=20
                    )
                    self._photo_cache.append(photo)

                    # Logo
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

                    # Text info
                    tk.Label(
                        cf,
                        text=f"{name}\nVotes: {votes}",
                        bg="#f9f9f9",
                        fg="#333333",
                        justify="left",
                        font=("Arial", 11, "bold"),
                    ).pack(side="left", padx=10, pady=8)

            # ---------------- RIGHT: ANALYTICS PANEL (UNCHANGED) ----------------
            analytics = tk.LabelFrame(
                main,
                text="Poll Analytics",
                bg=THEME_WHITE,
                fg=THEME_RED,
                padx=8,
                pady=8,
                font=("Segoe UI", 10, "bold"),
            )
            analytics.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
            analytics.rowconfigure(0, weight=1)
            analytics.columnconfigure(0, weight=1)
            analytics.columnconfigure(1, weight=1)

            # Get poll data for charts
            rows = self.db.get_poll_status()  # (position, name, votes)
            if not rows:
                tk.Label(
                    analytics,
                    text="No poll data available yet.",
                    bg=THEME_WHITE,
                    fg="gray",
                    font=("Segoe UI", 9, "italic"),
                ).grid(row=0, column=0, columnspan=2, pady=10)
                return

            candidates_flat = [(pos, name, votes) for (pos, name, votes) in rows]
            total_votes = sum(v for _, _, v in candidates_flat)

            if total_votes == 0:
                tk.Label(
                    analytics,
                    text="No votes have been cast yet.\nCharts will appear once voting starts.",
                    bg=THEME_WHITE,
                    fg="gray",
                    font=("Segoe UI", 9),
                    justify="center",
                ).grid(row=0, column=0, columnspan=2, pady=10)
                return

            # Sort & top 8
            candidates_sorted = sorted(candidates_flat, key=lambda r: r[2], reverse=True)
            top_candidates = candidates_sorted[:8]

            charts_container = tk.Frame(analytics, bg=THEME_WHITE)
            charts_container.grid(row=0, column=0, columnspan=2, sticky="nsew")
            charts_container.columnconfigure(0, weight=1)
            charts_container.columnconfigure(1, weight=1)
            charts_container.rowconfigure(0, weight=1)

            # ===== PIE CHART =====
            pie_frame = tk.Frame(charts_container, bg=THEME_WHITE)
            pie_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

            tk.Label(
                pie_frame,
                text="Vote Share (Top Candidates)",
                font=("Segoe UI", 11, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(anchor="w", pady=(0, 4), padx=4)

            pie_canvas = tk.Canvas(
                pie_frame,
                width=240,
                height=190,
                bg=THEME_WHITE,
                highlightthickness=0,
            )
            pie_canvas.pack(pady=4, fill="both", expand=True)

            slice_colors = [
                "#e53935",
                "#8e24aa",
                "#3949ab",
                "#00897b",
                "#fbc02d",
                "#fb8c00",
                "#6d4c41",
                "#5e35b1",
            ]

            x0, y0, x1, y1 = 20, 10, 210, 180
            start_angle = 0

            for idx, (_, name, votes) in enumerate(top_candidates):
                if votes <= 0:
                    continue
                extent = (votes / total_votes) * 360
                color = slice_colors[idx % len(slice_colors)]
                pie_canvas.create_arc(
                    x0,
                    y0,
                    x1,
                    y1,
                    start=start_angle,
                    extent=extent,
                    fill=color,
                    outline=THEME_WHITE,
                )
                start_angle += extent

            legend = tk.Frame(pie_frame, bg=THEME_WHITE)
            legend.pack(anchor="w", padx=4, pady=(2, 0))

            for idx, (pos, name, votes) in enumerate(top_candidates):
                color = slice_colors[idx % len(slice_colors)]
                row_f = tk.Frame(legend, bg=THEME_WHITE)
                row_f.pack(anchor="w", pady=1)

                tk.Canvas(
                    row_f,
                    width=10,
                    height=10,
                    bg=color,
                    highlightthickness=0,
                ).pack(side="left", padx=(0, 4))

                percent = (votes / total_votes) * 100
                tk.Label(
                    row_f,
                    text=f"{name} ({pos}) – {votes} ({percent:.1f}%)",
                    bg=THEME_WHITE,
                    fg="#333333",
                    font=("Segoe UI", 8),
                ).pack(side="left")

            # ===== BAR CHART =====
            bar_frame = tk.Frame(charts_container, bg=THEME_WHITE)
            bar_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

                        # ---------------- BAR CHART ----------------
            tk.Label(
                bar_frame,
                text="Votes per Candidate (Top 8)",
                font=("Segoe UI", 11, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(anchor="w", pady=(0, 4), padx=4)

            # Wider canvas so we have space for labels + bars
            bar_canvas = tk.Canvas(
                bar_frame,
                width=320,
                height=200,
                bg=THEME_WHITE,
                highlightthickness=0,
            )
            bar_canvas.pack(pady=4, fill="both", expand=True)

            max_votes = max(v for _, _, v in top_candidates) or 1

            # Leave a big left margin for full names
            label_x = 10
            chart_left = 130      # y-axis (start of bars)
            chart_top = 10
            chart_right = 300
            chart_bottom = 190
            bar_height = 14
            bar_gap = 6

            # Axes
            bar_canvas.create_line(
                chart_left,
                chart_top,
                chart_left,
                chart_bottom,
                fill="#cccccc",
            )
            bar_canvas.create_line(
                chart_left,
                chart_bottom,
                chart_right,
                chart_bottom,
                fill="#cccccc",
            )

            for idx, (pos, name, votes) in enumerate(top_candidates):
                y = chart_top + idx * (bar_height + bar_gap)
                if y + bar_height > chart_bottom:
                    break

                bar_length = (votes / max_votes) * (chart_right - chart_left - 10)
                color = slice_colors[idx % len(slice_colors)]

                # Bar
                bar_canvas.create_rectangle(
                    chart_left,
                    y,
                    chart_left + bar_length,
                    y + bar_height,
                    fill=color,
                    outline="",
                )

                # ✅ Candidate label INSIDE canvas, fully visible
                bar_canvas.create_text(
                    label_x,
                    y + bar_height / 2,
                    text=name,
                    anchor="w",         # start from label_x and grow to the right
                    font=("Segoe UI", 8),
                    fill="#333333",
                )

                # Vote count at end of bar
                bar_canvas.create_text(
                    chart_left + bar_length + 4,
                    y + bar_height / 2,
                    text=str(votes),
                    anchor="w",
                    font=("Segoe UI", 8, "bold"),
                    fill="#555555",
                )

            # ===== LEADING PER POSITION =====
            leaders_frame = tk.Frame(analytics, bg=THEME_WHITE)
            leaders_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))

            tk.Label(
                leaders_frame,
                text="Leading per Position:",
                bg=THEME_WHITE,
                fg=THEME_RED,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w", padx=2, pady=(0, 2))

            leaders = {}
            for pos, name, votes in candidates_flat:
                if pos not in leaders or votes > leaders[pos][1]:
                    leaders[pos] = (name, votes)

            for pos, (name, votes) in leaders.items():
                tk.Label(
                    leaders_frame,
                    text=f"{pos}: {name} ({votes} votes)",
                    bg=THEME_WHITE,
                    fg="#333333",
                    font=("Segoe UI", 9),
                ).pack(anchor="w", padx=10)

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
