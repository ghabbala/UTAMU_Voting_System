# admin_panel.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from database import DatabaseManager
from utils import THEME_RED, THEME_WHITE, center_window
import os
from PIL import Image, ImageTk 


class AdminPanel:
    def __init__(self):
        self.db = DatabaseManager()
        self._photo_cache = []
        self.win = None

    # ---------- ADMIN DASHBOARD ----------
        # ---------- ADMIN DASHBOARD ----------
    def show_dashboard(self):
        self.win = tk.Tk()
        self.win.title("Admin Dashboard")

        # ---------- Responsive initial sizing ----------
        # Get screen size
        screen_w = self.win.winfo_screenwidth()
        screen_h = self.win.winfo_screenheight()

        # Your original "design" size
        base_w, base_h = 997, 700

        # Use up to 90% of screen, but not more than your base design
        width = min(base_w, int(screen_w * 0.9))
        height = min(base_h, int(screen_h * 0.9))

        # Center the window with the computed size
        center_window(self.win, width, height)

        # Allow resizing + set a reasonable minimum
        self.win.resizable(True, True)
        self.win.minsize(800, 500)
        self.win.configure(bg=THEME_WHITE)

        # ---------- Header ----------
        header = tk.Frame(self.win, bg=THEME_RED, height=60)
        header.pack(fill="x")
        tk.Label(
            header,
            text="UVS ADMIN DASHBOARD",
            font=("Helvetica", 22, "bold"),
            bg=THEME_RED,
            fg=THEME_WHITE
        ).pack(pady=10)

        # ---------- Main Frame ----------
        main_frame = tk.Frame(self.win, bg=THEME_WHITE)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ Make main_frame use grid and be responsive
        main_frame.columnconfigure(0, weight=0)   # sidebar (fixed-ish)
        main_frame.columnconfigure(1, weight=1)   # right panel expands
        main_frame.rowconfigure(0, weight=1)

        # ---------- Sidebar ----------
        sidebar = tk.Frame(main_frame, bg=THEME_RED, width=220)
        sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 10), pady=0)
        # Keep its width (don't let children shrink it)
        sidebar.grid_propagate(False)

        # ---------- Right Panel (dynamic content area) ----------
        self.right_panel = tk.Frame(main_frame, bg=THEME_WHITE)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Let anything placed inside right_panel grow with it (if they use grid)
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(0, weight=1)

        # ---------- Sidebar Buttons ----------
        actions = [
            ("Dash board", self.show_stats_dashboard),
            ("Register Candidate", self.show_candidate_registration),
            ("View Candidates", self.show_candidates),
            ("Manage Candidates", self.show_manage_candidates),
            ("Set Voting Duration", self.show_voting_duration_window),
            ("View Poll Status", self.show_poll_status),
            ("Manage Positions", self.show_manage_positions),
            ("Reset Votes", self._reset_votes),
            ("Log Out", self._go_back),
        ]

        for text, cmd in actions:
            btn_bg, btn_fg = (
                (THEME_WHITE, THEME_RED)
                if text in ["Set Voting Duration", "Reset Votes", "Back"]
                else (THEME_RED, THEME_WHITE)
            )
            btn = tk.Button(
                sidebar,
                text=text,
                bg=btn_bg,
                fg=btn_fg,
                width=20,
                height=2,
                font=("Segoe UI", 11, "bold"),
                relief="flat",
                cursor="hand2",
                command=cmd,
            )
            # ✅ Make buttons stretch with sidebar width
            btn.pack(pady=8, fill="x")

            # Hover effect
            btn.bind(
                "<Enter>",
                lambda e, b=btn: b.config(
                    bg=THEME_WHITE if b.cget("bg") == THEME_RED else THEME_RED,
                    fg=THEME_RED if b.cget("fg") == THEME_WHITE else THEME_WHITE,
                ),
            )
            btn.bind(
                "<Leave>",
                lambda e, b=btn: b.config(bg=btn_bg, fg=btn_fg),
            )

        tk.Label(
            self.win,
            text="© 2025 UTAMU Voting System",
            font=("Segoe UI", 9),
            bg=THEME_WHITE,
            fg="gray",
        ).pack(side="bottom", pady=4)

        # Show dashboard charts by default on login
        self.show_stats_dashboard()

        self.win.mainloop()



    # ---------- Helper: Display content on right panel ----------
    def display_content(self, builder_func):
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        builder_func(self.right_panel)

    # ---------- Actions ----------
    def show_candidate_registration(self):
        def build(frame):
            # ===== HEADER =====
            header = tk.Frame(frame, bg=THEME_WHITE)
            header.pack(fill="x", pady=(5, 10))

            tk.Label(
                header,
                text="Register Candidate",
                font=("Segoe UI", 18, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(anchor="w", padx=10)

            tk.Label(
                header,
                text="Capture candidate details and media that will appear on the ballot.",
                font=("Segoe UI", 9),
                bg=THEME_WHITE,
                fg="#555555",
            ).pack(anchor="w", padx=10, pady=(2, 0))

            # Thin red separator
            tk.Frame(header, bg=THEME_RED, height=2).pack(fill="x", pady=(8, 0), padx=6)

            # ===== CARD CONTAINER =====
            card = tk.Frame(
                frame,
                bg=THEME_WHITE,
                highlightbackground=THEME_RED,
                highlightthickness=1,
                bd=0,
                padx=18,
                pady=16,
            )
            card.pack(padx=20, pady=16, fill="x")

            # Two columns inside card
            left = tk.Frame(card, bg=THEME_WHITE)
            right = tk.Frame(card, bg=THEME_WHITE)
            left.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
            right.grid(row=0, column=1, sticky="nsew")

            card.columnconfigure(0, weight=1)
            card.columnconfigure(1, weight=1)

            # ================= LEFT: BASIC DETAILS =================
            tk.Label(
                left,
                text="Candidate Details",
                font=("Segoe UI", 11, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

            # Full Name
            tk.Label(
                left,
                text="Full Name *",
                bg=THEME_WHITE,
                fg=THEME_RED,
                font=("Segoe UI", 10),
            ).grid(row=1, column=0, padx=4, pady=6, sticky="e")

            name_entry = tk.Entry(left, width=32, font=("Segoe UI", 10))
            name_entry.grid(row=1, column=1, padx=4, pady=6, sticky="w")

            # Position
            tk.Label(
                left,
                text="Position *",
                bg=THEME_WHITE,
                fg=THEME_RED,
                font=("Segoe UI", 10),
            ).grid(row=2, column=0, padx=4, pady=6, sticky="e")

            positions = self.db.get_all_positions()
            position_var = tk.StringVar()
            position_combo = ttk.Combobox(
                left,
                textvariable=position_var,
                values=positions,
                state="readonly",
                width=30,
            )
            position_combo.grid(row=2, column=1, padx=4, pady=6, sticky="w")

            if positions:
                position_combo.current(0)
            else:
                messagebox.showwarning(
                    "No Positions Found",
                    "Please add positions first before registering candidates.",
                )

            # Small hint under fields
            tk.Label(
                left,
                text="Fields marked * are required.",
                bg=THEME_WHITE,
                fg="#777777",
                font=("Segoe UI", 8, "italic"),
            ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(4, 0))

            # ================= RIGHT: MEDIA UPLOADS =================
            tk.Label(
                right,
                text="Media Uploads",
                font=("Segoe UI", 11, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

            # Shared file picker
            def browse_file(path_var, label_widget, title):
                path = filedialog.askopenfilename(
                    title=title,
                    filetypes=[
                        ("Images", "*.jpg *.jpeg *.png *.gif *.bmp"),
                        ("All Files", "*.*"),
                    ],
                )
                if path:
                    path_var.set(path)
                    label_widget.config(text=os.path.basename(path), fg="black")

            # Photo
            photo_path = tk.StringVar()
            tk.Label(
                right,
                text="Candidate Photo:",
                bg=THEME_WHITE,
                fg=THEME_RED,
                font=("Segoe UI", 10),
            ).grid(row=1, column=0, padx=4, pady=6, sticky="e")

            tk.Button(
                right,
                text="Upload Photo",
                bg=THEME_RED,
                fg=THEME_WHITE,
                relief="flat",
                font=("Segoe UI", 9, "bold"),
                command=lambda: browse_file(
                    photo_path, lbl_photo, "Select Candidate Photo"
                ),
                width=18,
                cursor="hand2",
            ).grid(row=1, column=1, padx=4, pady=6, sticky="w")

            lbl_photo = tk.Label(
                right,
                text="No photo selected",
                bg=THEME_WHITE,
                fg="gray",
                font=("Segoe UI", 8),
            )
            lbl_photo.grid(row=2, column=1, padx=4, pady=(0, 10), sticky="w")

            # Logo
            logo_path = tk.StringVar()
            tk.Label(
                right,
                text="Candidate Logo:",
                bg=THEME_WHITE,
                fg=THEME_RED,
                font=("Segoe UI", 10),
            ).grid(row=3, column=0, padx=4, pady=6, sticky="e")

            tk.Button(
                right,
                text="Upload Logo",
                bg=THEME_RED,
                fg=THEME_WHITE,
                relief="flat",
                font=("Segoe UI", 9, "bold"),
                command=lambda: browse_file(
                    logo_path, lbl_logo, "Select Candidate Logo"
                ),
                width=18,
                cursor="hand2",
            ).grid(row=3, column=1, padx=4, pady=6, sticky="w")

            lbl_logo = tk.Label(
                right,
                text="No logo selected",
                bg=THEME_WHITE,
                fg="gray",
                font=("Segoe UI", 8),
            )
            lbl_logo.grid(row=4, column=1, padx=4, pady=(0, 6), sticky="w")

            # Tip text
            tk.Label(
                right,
                text="Tip: Use clear, front-facing photos\nfor better recognition on the ballot.",
                bg=THEME_WHITE,
                fg="#777777",
                font=("Segoe UI", 8, "italic"),
                justify="left",
            ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(6, 0))

            # ===== SAVE CANDIDATE BUTTON =====
            def save_candidate():
                name = name_entry.get().strip()
                position = position_combo.get().strip()
                photo = photo_path.get().strip()
                logo = logo_path.get().strip()

                if not name or not position:
                    messagebox.showwarning(
                        "Input Error",
                        "Please enter the candidate name and select a position.",
                    )
                    return

                try:
                    self.db.add_candidate(name, position, photo, logo)
        
                    # Go straight to "View Candidates"
                    self.show_candidates()
                    return

                except Exception as e:
                    messagebox.showerror("Database Error", str(e))

            footer = tk.Frame(frame, bg=THEME_WHITE)
            footer.pack(fill="x", pady=(0, 10))

            tk.Button(
                footer,
                text="Save Candidate",
                bg=THEME_RED,
                fg=THEME_WHITE,
                font=("Segoe UI", 11, "bold"),
                width=20,
                relief="flat",
                cursor="hand2",
                command=save_candidate,
            ).pack(pady=5)

        self.display_content(build)



    def show_voting_duration_window(self):
        def build(frame):
            # ===== HEADER =====
            header = tk.Frame(frame, bg=THEME_WHITE)
            header.pack(fill="x", pady=(5, 10))

            tk.Label(
                header,
                text="Set Voting Duration",
                font=("Segoe UI", 18, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(anchor="w", padx=10)

            tk.Label(
                header,
                text="Define when students are allowed to cast their votes. Times use the system clock.",
                font=("Segoe UI", 9),
                bg=THEME_WHITE,
                fg="#555555",
            ).pack(anchor="w", padx=10, pady=(2, 0))

            # Thin red separator
            tk.Frame(header, bg=THEME_RED, height=2).pack(fill="x", pady=(8, 0), padx=6)

            # ===== CARD CONTAINER =====
            card = tk.Frame(
                frame,
                bg=THEME_WHITE,
                highlightbackground=THEME_RED,
                highlightthickness=1,
                bd=0,
                padx=18,
                pady=16,
            )
            card.pack(padx=20, pady=16, fill="x")

            form = tk.Frame(card, bg=THEME_WHITE)
            form.pack(fill="x")

            # ---- Start time ----
            tk.Label(
                form,
                text="Start Date & Time *",
                bg=THEME_WHITE,
                fg=THEME_RED,
                font=("Segoe UI", 10, "bold"),
            ).grid(row=0, column=0, padx=6, pady=(2, 4), sticky="w")

            start_entry = tk.Entry(form, width=28, font=("Segoe UI", 10))
            start_entry.grid(row=1, column=0, padx=6, pady=(0, 8), sticky="w")

            tk.Label(
                form,
                text="Format: YYYY-MM-DD HH:MM   e.g. 2025-03-15 09:30",
                bg=THEME_WHITE,
                fg="#777777",
                font=("Segoe UI", 8, "italic"),
            ).grid(row=2, column=0, padx=6, pady=(0, 10), sticky="w")

            # ---- End time ----
            tk.Label(
                form,
                text="End Date & Time *",
                bg=THEME_WHITE,
                fg=THEME_RED,
                font=("Segoe UI", 10, "bold"),
            ).grid(row=0, column=1, padx=6, pady=(2, 4), sticky="w")

            end_entry = tk.Entry(form, width=28, font=("Segoe UI", 10))
            end_entry.grid(row=1, column=1, padx=6, pady=(0, 8), sticky="w")

            tk.Label(
                form,
                text="Must be later than the start time.",
                bg=THEME_WHITE,
                fg="#777777",
                font=("Segoe UI", 8, "italic"),
            ).grid(row=2, column=1, padx=6, pady=(0, 10), sticky="w")

            # Stretch form columns nicely
            form.columnconfigure(0, weight=1)
            form.columnconfigure(1, weight=1)

            # Small note at bottom of card
            tk.Label(
                card,
                text="Tip: Set a clear voting window and communicate it to all students.",
                bg=THEME_WHITE,
                fg="#666666",
                font=("Segoe UI", 8),
            ).pack(anchor="w", pady=(4, 0))

            # ===== FOOTER BUTTONS =====
            footer = tk.Frame(frame, bg=THEME_WHITE)
            footer.pack(fill="x", pady=(8, 10))

            def save_duration():
                try:
                    start_str = start_entry.get().strip()
                    end_str = end_entry.get().strip()

                    if not start_str or not end_str:
                        messagebox.showerror(
                            "Missing Values",
                            "Please enter both start and end date/time.",
                        )
                        return

                    start = datetime.fromisoformat(start_str)
                    end = datetime.fromisoformat(end_str)

                    if end <= start:
                        messagebox.showerror("Error", "End time must be after start time.")
                        return

                    self.db.set_voting_duration(start.isoformat(), end.isoformat())
                    messagebox.showinfo("Success", "Voting duration saved successfully!")

                    # 👉 After saving, go back to the dashboard analytics
                    self.show_stats_dashboard()

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        "Invalid format. Use YYYY-MM-DD HH:MM\n\n"
                        f"Details: {e}",
                    )

            # Primary button: Save
            tk.Button(
                footer,
                text="Save Voting Duration",
                bg=THEME_RED,
                fg=THEME_WHITE,
                font=("Segoe UI", 11, "bold"),
                width=20,
                relief="flat",
                cursor="hand2",
                command=save_duration,
            ).pack(side="left", padx=10, pady=5)

            # Secondary button: Back to Dashboard (optional shortcut)
            tk.Button(
                footer,
                text="Back to Dashboard",
                bg=THEME_WHITE,
                fg=THEME_RED,
                font=("Segoe UI", 10, "bold"),
                relief="solid",
                bd=1,
                cursor="hand2",
                command=self.show_stats_dashboard,
            ).pack(side="left", padx=6, pady=5)

        self.display_content(build)


    def show_poll_status(self):
        def build(frame):
            tk.Label(frame, text="Current Poll Results", font=("Segoe UI", 16, "bold"),
                     bg=THEME_WHITE, fg=THEME_RED).pack(pady=10)
            tree = ttk.Treeview(frame, columns=("Position", "Name", "Votes"), show="headings", height=12)
            tree.heading("Position", text="Position")
            tree.heading("Name", text="Candidate Name")
            tree.heading("Votes", text="Votes")
            tree.pack(fill="both", expand=True, padx=10, pady=10)

            data = self.db.get_poll_status()
            for pos, name, votes in data:
                tree.insert("", "end", values=(pos, name, votes))
        self.display_content(build)
    
    def show_candidates(self):
        """Show all registered candidates with their photos and logos."""
        def build(frame):
            tk.Label(
                frame,
                text="Registered Candidates",
                font=("Segoe UI", 16, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED
            ).pack(pady=10)

            container = tk.Frame(frame, bg=THEME_WHITE)
            container.pack(fill="both", expand=True)

            # Scrollable area
            canvas = tk.Canvas(container, bg=THEME_WHITE, highlightthickness=0)
            scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scroll_frame = tk.Frame(canvas, bg=THEME_WHITE)

            scroll_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # --- Mouse wheel scrolling (no bind_all, so no TclError when closed) ---
            def _on_mousewheel(event, c=canvas):
                # Windows / MacOS (event.delta)
                if hasattr(event, "delta") and event.delta:
                    c.yview_scroll(int(-1 * (event.delta / 120)), "units")
                else:
                    # Linux (Button-4 / Button-5)
                    if event.num == 4:
                        c.yview_scroll(-1, "units")
                    elif event.num == 5:
                        c.yview_scroll(1, "units")

            canvas.bind("<MouseWheel>", _on_mousewheel)   # Windows / Mac
            canvas.bind("<Button-4>", _on_mousewheel)     # Linux scroll up
            canvas.bind("<Button-5>", _on_mousewheel)     # Linux scroll down

            # Load candidates
            try:
                candidates = self.db.get_candidates()
            except Exception as e:
                messagebox.showerror("Database Error", f"Could not load candidates:\n{e}")
                return

            if not candidates:
                tk.Label(
                    scroll_frame,
                    text="No candidates registered yet.",
                    bg=THEME_WHITE,
                    fg="gray",
                    font=("Segoe UI", 11, "italic")
                ).pack(pady=20)
                return

            # === Show last registered candidate on top ===
            # Assuming id increases with each insert -> reverse list in Python
            candidates = list(reversed(candidates))

            # Clear old images
            self._photo_cache.clear()

            for cid, name, position, votes, photo_path, logo_path in candidates:
                card = tk.Frame(
                    scroll_frame,
                    bg=THEME_WHITE,
                    bd=1,
                    relief="solid",
                    padx=10,
                    pady=10
                )
                card.pack(fill="x", padx=15, pady=8)

                # --- Candidate photo ---
                photo_label = tk.Label(card, bg=THEME_WHITE)
                photo_label.pack(side="left", padx=10)

                try:
                    if photo_path and os.path.exists(photo_path):
                        img = Image.open(photo_path)
                    else:
                        raise FileNotFoundError

                    img = img.resize((120, 120))
                    # tie image to admin window
                    photo_img = ImageTk.PhotoImage(img, master=self.win)
                except Exception:
                    placeholder = Image.new("RGB", (120, 120), color=(240, 240, 240))
                    photo_img = ImageTk.PhotoImage(placeholder, master=self.win)

                self._photo_cache.append(photo_img)
                photo_label.config(image=photo_img)
                photo_label.image = photo_img  # extra safety

                # --- Candidate logo (optional) ---
                logo_label = tk.Label(card, bg=THEME_WHITE)
                logo_label.pack(side="left", padx=10)

                if logo_path and os.path.exists(logo_path):
                    try:
                        logo_img = Image.open(logo_path).resize((120, 120))
                        logo_photo = ImageTk.PhotoImage(logo_img, master=self.win)
                        self._photo_cache.append(logo_photo)
                        logo_label.config(image=logo_photo)
                        logo_label.image = logo_photo
                    except Exception:
                        pass

                # --- Text info ---
                info = tk.Frame(card, bg=THEME_WHITE)
                info.pack(side="left", padx=15)

                tk.Label(
                    info,
                    text=name,
                    font=("Segoe UI", 13, "bold"),
                    bg=THEME_WHITE,
                    fg="#333333"
                ).pack(anchor="w")

                tk.Label(
                    info,
                    text=f"Position: {position}",
                    font=("Segoe UI", 11),
                    bg=THEME_WHITE,
                    fg="#555555"
                ).pack(anchor="w", pady=(2, 0))

                tk.Label(
                    info,
                    text=f"Votes: {votes}",
                    font=("Segoe UI", 11),
                    bg=THEME_WHITE,
                    fg="#777777"
                ).pack(anchor="w", pady=(2, 0))

        # Use your shared right-panel content loader
        self.display_content(build)




    def show_manage_positions(self):
        def build(frame):
            tk.Label(frame, text="Manage Positions", font=("Segoe UI", 16, "bold"),
                     bg=THEME_WHITE, fg=THEME_RED).pack(pady=12)

            # ----- Frame for list and controls -----
            list_frame = tk.Frame(frame, bg=THEME_WHITE)
            list_frame.pack(pady=10)

            tk.Label(list_frame, text="Available Positions", bg=THEME_WHITE, fg="gray",
                     font=("Segoe UI", 11, "italic")).pack()

            # Listbox to display positions
            self.position_list = tk.Listbox(list_frame, width=40, height=10, font=("Arial", 12))
            self.position_list.pack(pady=8)

            # Load all positions from DB
            def refresh_positions():
                self.position_list.delete(0, tk.END)
                for pos in self.db.get_all_positions():
                    self.position_list.insert(tk.END, pos)

            refresh_positions()

            # ----- Add new position -----
            add_frame = tk.Frame(frame, bg=THEME_WHITE)
            add_frame.pack(pady=10)

            tk.Label(add_frame, text="Add New Position:", bg=THEME_WHITE, fg=THEME_RED).grid(row=0, column=0, padx=6, pady=6)
            entry = tk.Entry(add_frame, width=28)
            entry.grid(row=0, column=1, padx=6, pady=6)

            def add_position():
                pos = entry.get().strip()
                if not pos:
                    messagebox.showwarning("Input Error", "Please enter position name.")
                    return
                self.db.add_position(pos)
                #messagebox.showinfo("Success", f"'{pos}' added successfully!")
                entry.delete(0, tk.END)
                refresh_positions()

            def delete_position():
                selected = self.position_list.curselection()
                if not selected:
                    messagebox.showwarning("No Selection", "Please select a position to delete.")
                    return
                pos_name = self.position_list.get(selected)
                confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{pos_name}'?")
                if confirm:
                    self.db.delete_position(pos_name)
                    refresh_positions()
                    messagebox.showinfo("Deleted", f"Position '{pos_name}' deleted successfully.")

            # ----- Buttons -----
            btn_frame = tk.Frame(frame, bg=THEME_WHITE)
            btn_frame.pack(pady=10)

            tk.Button(btn_frame, text="Add Position", bg=THEME_RED, fg=THEME_WHITE,
                      font=("Segoe UI", 11, "bold"), width=14, relief="flat",
                      command=add_position).pack(side="left", padx=10)

            tk.Button(btn_frame, text="Delete Position", bg=THEME_WHITE, fg=THEME_RED,
                      font=("Segoe UI", 11, "bold"), width=14, relief="solid",
                      command=delete_position).pack(side="left", padx=10)

        self.display_content(build)
    
    def show_manage_candidates(self):
        """Manage candidates: edit in a popup and delete."""

        def build(frame):
            tk.Label(
                frame,
                text="Manage Candidates",
                font=("Segoe UI", 16, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(pady=12)

            container = tk.Frame(frame, bg=THEME_WHITE)
            container.pack(fill="both", expand=True, padx=10, pady=5)

            # ========= LEFT: list of candidates =========
            left = tk.Frame(container, bg=THEME_WHITE)
            left.pack(side="left", fill="both", expand=True)

            columns = ("ID", "Name", "Position", "Votes")
            tree = ttk.Treeview(left, columns=columns, show="headings", height=18)

            for col in columns:
                tree.heading(col, text=col)

            tree.column("ID", width=50, anchor="center")
            tree.column("Name", width=160)
            tree.column("Position", width=140, anchor="center")
            tree.column("Votes", width=70, anchor="center")

            scroll = tk.Scrollbar(left, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scroll.set)

            tree.grid(row=0, column=0, sticky="nsew")
            scroll.grid(row=0, column=1, sticky="ns")

            left.rowconfigure(0, weight=1)
            left.columnconfigure(0, weight=1)

            # helper: load candidates from DB into tree
            def load_candidates(select_id=None):
                tree.delete(*tree.get_children())
                try:
                    rows = self.db.get_candidates()
                except Exception as e:
                    messagebox.showerror("Database Error", f"Could not load candidates:\n{e}")
                    return

                for cid, name, position, votes, photo_path, logo_path in rows:
                    tree.insert("", "end", iid=str(cid), values=(cid, name, position, votes))

                children = tree.get_children()
                if not children:
                    return

                # optional reselect
                if select_id is not None and str(select_id) in children:
                    iid = str(select_id)
                else:
                    iid = children[0]

                tree.selection_set(iid)
                tree.focus(iid)

            load_candidates()

            # ========= RIGHT: action buttons =========
            right = tk.Frame(container, bg=THEME_WHITE)
            right.pack(side="left", fill="y", padx=20)

            tk.Label(
                right,
                text="Actions",
                font=("Segoe UI", 12, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(anchor="w", pady=(0, 10))

            # helper: get selected candidate id
            def get_selected_id():
                sel = tree.selection()
                if not sel:
                    return None
                try:
                    return int(sel[0])
                except Exception:
                    return None

            # ---- EDIT POPUP ----
            def edit_selected():
                cid = get_selected_id()
                if cid is None:
                    messagebox.showwarning("No selection", "Please select a candidate to edit.")
                    return

                row = self.db.get_candidate_by_id(cid)
                if not row:
                    messagebox.showerror("Error", "Candidate not found in database.")
                    return

                _cid, name, position, votes, photo_path, logo_path = row

                # === Popup window ===
                win = tk.Toplevel(self.win)
                win.title(f"Edit Candidate #{cid}")
                center_window(win, 500, 350)
                win.configure(bg=THEME_WHITE)
                win.resizable(False, False)

                form = tk.Frame(win, bg=THEME_WHITE)
                form.pack(padx=15, pady=15, fill="both", expand=True)

                # --- Candidate name (same as register) ---
                tk.Label(form, text="Candidate Name:", bg=THEME_WHITE, fg=THEME_RED).grid(
                    row=0, column=0, padx=8, pady=6, sticky="e"
                )
                name_var = tk.StringVar(value=name or "")
                name_entry = tk.Entry(form, textvariable=name_var, width=30)
                name_entry.grid(row=0, column=1, padx=8, pady=6, sticky="w")

                # --- Position selection (from positions table) ---
                tk.Label(form, text="Select Position:", bg=THEME_WHITE, fg=THEME_RED).grid(
                    row=1, column=0, padx=8, pady=6, sticky="e"
                )
                positions = self.db.get_all_positions()
                position_var = tk.StringVar()
                position_combo = ttk.Combobox(
                    form,
                    textvariable=position_var,
                    values=positions,
                    state="readonly",
                    width=27,
                )
                position_combo.grid(row=1, column=1, padx=8, pady=6, sticky="w")

                # set current position if it exists in list, else blank
                if position and position in positions:
                    position_var.set(position)
                elif positions:
                    position_var.set(positions[0])

                # --- Photo and Logo path display + browser ---
                def browse_file(path_var, label_widget, title):
                    path = filedialog.askopenfilename(
                        title=title,
                        filetypes=[
                            ("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
                            ("All Files", "*.*"),
                        ],
                    )
                    if path:
                        path_var.set(path)
                        label_widget.config(text=os.path.basename(path), fg="black")

                # photo
                tk.Label(form, text="Photo:", bg=THEME_WHITE, fg=THEME_RED).grid(
                    row=2, column=0, padx=8, pady=6, sticky="e"
                )
                photo_path_var = tk.StringVar(value=photo_path or "")
                lbl_photo = tk.Label(
                    form,
                    text=os.path.basename(photo_path) if photo_path else "No photo selected",
                    bg=THEME_WHITE,
                    fg="black" if photo_path else "gray",
                )
                lbl_photo.grid(row=2, column=1, padx=6, pady=6, sticky="w")
                tk.Button(
                    form,
                    text="Change Photo",
                    bg=THEME_RED,
                    fg=THEME_WHITE,
                    relief="flat",
                    width=14,
                    command=lambda: browse_file(
                        photo_path_var, lbl_photo, "Select Candidate Photo"
                    ),
                ).grid(row=2, column=2, padx=6, pady=6)

                # logo
                tk.Label(form, text="Logo:", bg=THEME_WHITE, fg=THEME_RED).grid(
                    row=3, column=0, padx=8, pady=6, sticky="e"
                )
                logo_path_var = tk.StringVar(value=logo_path or "")
                lbl_logo = tk.Label(
                    form,
                    text=os.path.basename(logo_path) if logo_path else "No logo selected",
                    bg=THEME_WHITE,
                    fg="black" if logo_path else "gray",
                )
                lbl_logo.grid(row=3, column=1, padx=6, pady=6, sticky="w")
                tk.Button(
                    form,
                    text="Change Logo",
                    bg=THEME_RED,
                    fg=THEME_WHITE,
                    relief="flat",
                    width=14,
                    command=lambda: browse_file(
                        logo_path_var, lbl_logo, "Select Candidate Logo"
                    ),
                ).grid(row=3, column=2, padx=6, pady=6)

                # votes (read only)
                tk.Label(form, text="Votes:", bg=THEME_WHITE, fg=THEME_RED).grid(
                    row=4, column=0, padx=8, pady=6, sticky="e"
                )
                tk.Label(
                    form,
                    text=str(votes),
                    bg=THEME_WHITE,
                    fg="#555555",
                ).grid(row=4, column=1, padx=6, pady=6, sticky="w")

                # --- Save changes ---
                def save_changes():
                    new_name = name_var.get().strip()
                    new_pos = position_combo.get().strip()
                    new_photo = photo_path_var.get().strip()
                    new_logo = logo_path_var.get().strip()

                    if not new_name or not new_pos:
                        messagebox.showwarning(
                            "Input Error",
                            "Please fill all fields and select a position.",
                        )
                        return

                    try:
                        self.db.update_candidate(cid, new_name, new_pos, new_photo, new_logo)
                        messagebox.showinfo("Success", "Candidate updated successfully.")
                        win.destroy()
                        # reload main list and reselect this candidate
                        load_candidates(select_id=cid)
                    except Exception as e:
                        messagebox.showerror("Database Error", str(e))

                btn_frame = tk.Frame(form, bg=THEME_WHITE)
                btn_frame.grid(row=5, column=0, columnspan=3, pady=12, sticky="w")

                tk.Button(
                    btn_frame,
                    text="Save Changes",
                    bg="#0078D7",
                    fg="white",
                    relief="flat",
                    padx=12,
                    pady=3,
                    command=save_changes,
                ).pack(side="left", padx=(0, 8))

                tk.Button(
                    btn_frame,
                    text="Cancel",
                    bg="#CCCCCC",
                    fg="black",
                    relief="flat",
                    padx=12,
                    pady=3,
                    command=win.destroy,
                ).pack(side="left")

            # ---- DELETE SELECTED ----
            def delete_selected():
                cid = get_selected_id()
                if cid is None:
                    messagebox.showwarning("No selection", "Please select a candidate to delete.")
                    return

                if not messagebox.askyesno(
                    "Confirm Delete",
                    "Are you sure you want to delete this candidate?",
                ):
                    return

                try:
                    self.db.delete_candidate(cid)
                    messagebox.showinfo("Deleted", "Candidate deleted successfully.")
                    load_candidates()
                except Exception as e:
                    messagebox.showerror("Database Error", str(e))

            # Buttons on the right
            tk.Button(
                right,
                text="Edit Selected",
                bg=THEME_RED,
                fg=THEME_WHITE,
                relief="flat",
                width=16,
                padx=8,
                pady=4,
                command=edit_selected,
            ).pack(anchor="w", pady=(0, 8))

            tk.Button(
                right,
                text="Delete Selected",
                bg="#D83B01",
                fg=THEME_WHITE,
                relief="flat",
                width=16,
                padx=8,
                pady=4,
                command=delete_selected,
            ).pack(anchor="w")

        self.display_content(build)

    def show_stats_dashboard(self):
        """Visual dashboard: leaders per position + pie chart + bar graph of current poll status."""
        def build(frame):
            # ---------- HEADER ----------
            header = tk.Frame(frame, bg=THEME_WHITE)
            header.pack(fill="x", pady=(5, 5))

            tk.Label(
                header,
                text="Poll Analytics Dashboard",
                font=("Segoe UI", 18, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(anchor="w", padx=10)

            tk.Label(
                header,
                text="Leaders per position and visual summary of current votes.",
                font=("Segoe UI", 9),
                bg=THEME_WHITE,
                fg="#555555",
            ).pack(anchor="w", padx=10, pady=(0, 4))

            # ---------- LOAD DATA ----------
            # rows: (position, name, votes)
            rows = self.db.get_poll_status()

            if not rows:
                tk.Label(
                    frame,
                    text="No poll data available yet.",
                    font=("Segoe UI", 11, "italic"),
                    bg=THEME_WHITE,
                    fg="gray",
                ).pack(pady=40)
                return

            candidates = [(pos, name, votes) for (pos, name, votes) in rows]
            total_votes = sum(v for _, _, v in candidates)

            if total_votes == 0:
                tk.Label(
                    frame,
                    text="No votes have been cast yet.\nCharts will appear once voting starts.",
                    font=("Segoe UI", 11),
                    bg=THEME_WHITE,
                    fg="gray",
                    justify="center",
                ).pack(pady=40)
                return

            # sort by votes desc and limit to top 8 for charts
            candidates_sorted = sorted(candidates, key=lambda r: r[2], reverse=True)
            top_candidates = candidates_sorted[:8]

            # ---------- LEADERS PER POSITION ----------
            # NOTE: your SQL already orders by position, votes DESC
            # so the first row for each position is the leader.
            leaders = {}
            for pos, name, votes in rows:
                if pos not in leaders:      # first one we see for that pos is the leader
                    leaders[pos] = (name, votes)

            leader_items = sorted(leaders.items(), key=lambda kv: kv[0])  # sort by position name

            leaders_frame = tk.Frame(frame, bg=THEME_WHITE)
            leaders_frame.pack(fill="x", padx=10, pady=(6, 4))

            tk.Label(
                leaders_frame,
                text="Position Leaders",
                font=("Segoe UI", 11, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(anchor="w", pady=(0, 4))

            tree = ttk.Treeview(
                leaders_frame,
                columns=("Position", "Leader", "Votes"),
                show="headings",
                height=min(len(leader_items), 7),
            )
            tree.heading("Position", text="Position")
            tree.heading("Leader", text="Leading Candidate")
            tree.heading("Votes", text="Votes")

            tree.column("Position", width=160, anchor="w")
            tree.column("Leader", width=220, anchor="w")
            tree.column("Votes", width=80, anchor="center")

            tree.pack(fill="x", expand=False)

            for pos, (name, votes) in leader_items:
                tree.insert("", "end", values=(pos, name, votes))

            # ---------- MAIN CHARTS CONTAINER ----------
            charts_container = tk.Frame(frame, bg=THEME_WHITE)
            charts_container.pack(fill="both", expand=True, padx=10, pady=10)

            # Left: Pie chart
            pie_frame = tk.Frame(charts_container, bg=THEME_WHITE)
            pie_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

            # Right: Bar chart + legend
            bar_frame = tk.Frame(charts_container, bg=THEME_WHITE)
            bar_frame.pack(side="right", fill="both", expand=True, padx=(8, 0))

            # ---------------- PIE CHART ----------------
            tk.Label(
                pie_frame,
                text="Vote Share (Top Candidates)",
                font=("Segoe UI", 11, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(anchor="w", pady=(0, 4), padx=4)

            pie_canvas = tk.Canvas(
                pie_frame,
                width=320,
                height=260,
                bg=THEME_WHITE,
                highlightthickness=0,
            )
            pie_canvas.pack(pady=4, fill="both", expand=True)

            slice_colors = [
                "#e53935", "#8e24aa", "#3949ab", "#00897b",
                "#fbc02d", "#fb8c00", "#6d4c41", "#5e35b1",
            ]

            x0, y0, x1, y1 = 30, 20, 290, 240
            start_angle = 0

            for idx, (_, name, votes) in enumerate(top_candidates):
                if votes <= 0:
                    continue
                extent = (votes / total_votes) * 360
                color = slice_colors[idx % len(slice_colors)]
                pie_canvas.create_arc(
                    x0, y0, x1, y1,
                    start=start_angle,
                    extent=extent,
                    fill=color,
                    outline=THEME_WHITE,
                )
                start_angle += extent

            # Legend under pie
            legend_frame = tk.Frame(pie_frame, bg=THEME_WHITE)
            legend_frame.pack(pady=(6, 0), anchor="w", padx=4)

            for idx, (pos, name, votes) in enumerate(top_candidates):
                color = slice_colors[idx % len(slice_colors)]
                row = tk.Frame(legend_frame, bg=THEME_WHITE)
                row.pack(anchor="w", pady=1)

                tk.Canvas(
                    row, width=12, height=12, bg=color, highlightthickness=0
                ).pack(side="left", padx=(0, 4))

                percent = (votes / total_votes) * 100 if total_votes > 0 else 0
                tk.Label(
                    row,
                    text=f"{name} ({pos}) – {votes} votes ({percent:.1f}%)",
                    bg=THEME_WHITE,
                    fg="#333333",
                    font=("Segoe UI", 8),
                ).pack(side="left")

            # ---------------- BAR CHART ----------------
            tk.Label(
                bar_frame,
                text="Votes per Candidate (Top 8)",
                font=("Segoe UI", 11, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(anchor="w", pady=(0, 4), padx=4)

            bar_canvas_width = 420
            bar_canvas_height = 260

            bar_canvas = tk.Canvas(
                bar_frame,
                width=bar_canvas_width,
                height=bar_canvas_height,
                bg=THEME_WHITE,
                highlightthickness=0,
            )
            bar_canvas.pack(pady=4, fill="both", expand=True)

            max_votes = max(v for _, _, v in top_candidates) or 1

            # dynamic left margin based on longest candidate name
            max_name_len = max(len(name) for _, name, _ in top_candidates)
            label_col_width = min(180, 7 * max_name_len)  # ~7px per char, capped

            chart_left = 20 + label_col_width
            chart_right = bar_canvas_width - 20
            chart_top = 20
            chart_bottom = bar_canvas_height - 30

            bar_height = 18
            bar_gap = 8

            # Axis lines
            bar_canvas.create_line(
                chart_left, chart_top,
                chart_left, chart_bottom,
                fill="#cccccc"
            )
            bar_canvas.create_line(
                chart_left, chart_bottom,
                chart_right, chart_bottom,
                fill="#cccccc"
            )

            # Optional x-axis ticks (0.5 and 1.0 of max_votes)
            for frac in (0.5, 1.0):
                x = chart_left + frac * (chart_right - chart_left)
                bar_canvas.create_line(
                    x, chart_bottom,
                    x, chart_bottom + 4,
                    fill="#aaaaaa"
                )
                bar_canvas.create_text(
                    x,
                    chart_bottom + 12,
                    text=str(int(frac * max_votes)),
                    font=("Segoe UI", 7),
                    fill="#777777",
                )

            # Bars + labels
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

                # Candidate label – clear left column, fully visible
                bar_canvas.create_text(
                    chart_left - 10,
                    y + bar_height / 2,
                    text=name,
                    anchor="e",
                    font=("Segoe UI", 9),
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

            # ---------- FOOTER SUMMARY ----------
            tk.Label(
                frame,
                text=f"Total votes counted: {total_votes}",
                bg=THEME_WHITE,
                fg="#555555",
                font=("Segoe UI", 9, "italic"),
            ).pack(pady=(4, 2))

            # overall (all positions combined) leader
            leader_pos, leader_name, leader_votes = top_candidates[0]
            tk.Label(
                frame,
                text=f"Overall leader (all positions): {leader_name} ({leader_pos}) with {leader_votes} votes.",
                bg=THEME_WHITE,
                fg=THEME_RED,
                font=("Segoe UI", 9, "bold"),
            ).pack(pady=(0, 8))

        self.display_content(build)



    def _reset_votes(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to reset all votes?"):
            self.db.reset_votes()
            messagebox.showinfo("Success", "All votes have been reset.")
            self.show_poll_status()

    def _go_back(self):
        try:
            self.win.destroy()
        except Exception:
            pass
        from main import MainWindow
        app = MainWindow()
        app.run()
