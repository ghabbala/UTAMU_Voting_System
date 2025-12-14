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
    def show_dashboard(self):
        self.win = tk.Tk()
        self.win.title("Admin Dashboard")
        center_window(self.win, 997, 700)
        self.win.configure(bg=THEME_WHITE)
        self.win.resizable(False, False)

        # ---------- Header ----------
        header = tk.Frame(self.win, bg=THEME_RED, height=60)
        header.pack(fill="x")
        tk.Label(header, text="UVS ADMIN DASHBOARD", font=("Helvetica", 22, "bold"),
                 bg=THEME_RED, fg=THEME_WHITE).pack(pady=10)

        # ---------- Main Frame ----------
        main_frame = tk.Frame(self.win, bg=THEME_WHITE)
        main_frame.pack(fill="both", expand=True, pady=10)

        # ---------- Sidebar ----------
        sidebar = tk.Frame(main_frame, bg=THEME_RED, width=220)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        # ---------- Right Panel (dynamic content area) ----------
        self.right_panel = tk.Frame(main_frame, bg=THEME_WHITE)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Label(self.right_panel, text="Welcome, Admin!",
                 font=("Segoe UI", 16, "bold"),
                 bg=THEME_WHITE, fg=THEME_RED).pack(pady=20)
        tk.Label(self.right_panel, text="Select an option from the sidebar to manage the system.",
                 font=("Segoe UI", 11),
                 bg=THEME_WHITE, fg="gray").pack(pady=10)

        # ---------- Sidebar Buttons ----------
        actions = [
            ("Register Candidate", self.show_candidate_registration),
            ("View Candidates", self.show_candidates),
            ("Manage Candidates", self.show_manage_candidates),
            ("Set Voting Duration", self.show_voting_duration_window),
            ("View Poll Status", self.show_poll_status),
            ("Manage Positions", self.show_manage_positions),
            ("Reset Votes", self._reset_votes),
            ("Log Out", self._go_back)
        ]

        for text, cmd in actions:
            btn_bg, btn_fg = (THEME_WHITE, THEME_RED) if text in ["Set Voting Duration", "Reset Votes", "Back"] else (THEME_RED, THEME_WHITE)
            btn = tk.Button(sidebar, text=text, bg=btn_bg, fg=btn_fg, width=20, height=2,
                            font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                            command=cmd)
            btn.pack(pady=8)

            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=THEME_WHITE if b.cget("bg") == THEME_RED else THEME_RED,
                                                          fg=THEME_RED if b.cget("fg") == THEME_WHITE else THEME_WHITE))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=btn_bg, fg=btn_fg))

        tk.Label(self.win, text="© 2025 UTAMU Voting System", font=("Segoe UI", 9),
                 bg=THEME_WHITE, fg="gray").pack(side="bottom", pady=4)

        self.win.mainloop()

    # ---------- Helper: Display content on right panel ----------
    def display_content(self, builder_func):
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        builder_func(self.right_panel)

    # ---------- Actions ----------
    def show_candidate_registration(self):
        def build(frame):
            tk.Label(
                frame,
                text="Register Candidate",
                font=("Segoe UI", 16, "bold"),
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).pack(pady=12)

            form = tk.Frame(frame, bg=THEME_WHITE)
            form.pack(pady=6)

            # === Candidate name ===
            tk.Label(
                form,
                text="Candidate Name:",
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).grid(row=0, column=0, padx=8, pady=6, sticky="e")

            name_entry = tk.Entry(form, width=28)
            name_entry.grid(row=0, column=1, padx=8, pady=6)

            # === Position selection (from positions table) ===
            tk.Label(
                form,
                text="Select Position:",
                bg=THEME_WHITE,
                fg=THEME_RED,
            ).grid(row=1, column=0, padx=8, pady=6, sticky="e")

            positions = self.db.get_all_positions()  # from positions table
            position_var = tk.StringVar()
            position_combo = ttk.Combobox(
                form,
                textvariable=position_var,
                values=positions,
                state="readonly",
                width=25,
            )
            position_combo.grid(row=1, column=1, padx=8, pady=6, sticky="w")

            if positions:
                # Set default visually; user can change it
                position_combo.current(0)
            else:
                messagebox.showwarning(
                    "No Positions Found",
                    "Please add positions first before registering candidates.",
                )

            # === File picker function (shared) ===
            def browse_file(path_var, label_widget, title):
                path = filedialog.askopenfilename(
                    title=title,
                    filetypes=[("Images", "*.jpg *.jpeg *.png *.gif *.bmp"), ("All Files", "*.*")],
                )
                if path:
                    path_var.set(path)
                    label_widget.config(text=os.path.basename(path), fg="black")

            # === Candidate Photo ===
            photo_path = tk.StringVar()
            tk.Button(
                form,
                text="Upload Photo",
                bg=THEME_RED,
                fg=THEME_WHITE,
                relief="flat",
                command=lambda: browse_file(
                    photo_path, lbl_photo, "Select Candidate Photo"
                ),
                width=15,
            ).grid(row=2, column=0, padx=6, pady=8, sticky="e")

            lbl_photo = tk.Label(
                form, text="No photo selected", bg=THEME_WHITE, fg="gray"
            )
            lbl_photo.grid(row=2, column=1, padx=6, pady=8, sticky="w")

            # === Candidate Logo ===
            logo_path = tk.StringVar()
            tk.Button(
                form,
                text="Upload Logo",
                bg=THEME_RED,
                fg=THEME_WHITE,
                relief="flat",
                command=lambda: browse_file(
                    logo_path, lbl_logo, "Select Candidate Logo"
                ),
                width=15,
            ).grid(row=3, column=0, padx=6, pady=8, sticky="e")

            lbl_logo = tk.Label(
                form, text="No logo selected", bg=THEME_WHITE, fg="gray"
            )
            lbl_logo.grid(row=3, column=1, padx=6, pady=8, sticky="w")

            # === Save candidate ===
            def save_candidate():
                name = name_entry.get().strip()
                # IMPORTANT: read directly from the combobox, not from some other list
                position = position_combo.get().strip()
                photo = photo_path.get().strip()
                logo = logo_path.get().strip()

                if not name or not position:
                    messagebox.showwarning(
                        "Input Error",
                        "Please fill all fields and select a position.",
                    )
                    return

                try:
                    self.db.add_candidate(name, position, photo, logo)
                    messagebox.showinfo(
                        "Success", f"Candidate '{name}' added successfully!"
                    )
                    # Clear fields for the next entry
                    name_entry.delete(0, tk.END)
                    photo_path.set("")
                    logo_path.set("")
                    lbl_photo.config(text="No photo selected", fg="gray")
                    lbl_logo.config(text="No logo selected", fg="gray")
                    if positions:
                        position_combo.current(0)
                except Exception as e:
                    messagebox.showerror("Database Error", str(e))

            tk.Button(
                frame,
                text="Save Candidate",
                bg=THEME_RED,
                fg=THEME_WHITE,
                font=("Segoe UI", 11, "bold"),
                width=18,
                relief="flat",
                command=save_candidate,
            ).pack(pady=15)

        self.display_content(build)


    def show_voting_duration_window(self):
        def build(frame):
            tk.Label(frame, text="Set Voting Duration", font=("Segoe UI", 16, "bold"),
                     bg=THEME_WHITE, fg=THEME_RED).pack(pady=12)

            form = tk.Frame(frame, bg=THEME_WHITE)
            form.pack(pady=6)

            tk.Label(form, text="Start (YYYY-MM-DD HH:MM):", bg=THEME_WHITE, fg=THEME_RED).grid(row=0, column=0, padx=8, pady=6, sticky="e")
            start_entry = tk.Entry(form, width=25)
            start_entry.grid(row=0, column=1, padx=8, pady=6)

            tk.Label(form, text="End (YYYY-MM-DD HH:MM):", bg=THEME_WHITE, fg=THEME_RED).grid(row=1, column=0, padx=8, pady=6, sticky="e")
            end_entry = tk.Entry(form, width=25)
            end_entry.grid(row=1, column=1, padx=8, pady=6)

            def save_duration():
                try:
                    start = datetime.fromisoformat(start_entry.get().strip())
                    end = datetime.fromisoformat(end_entry.get().strip())
                    if end <= start:
                        messagebox.showerror("Error", "End time must be after start time.")
                        return
                    self.db.set_voting_duration(start.isoformat(), end.isoformat())
                    messagebox.showinfo("Success", "Voting duration saved!")
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid format. Use YYYY-MM-DD HH:MM\n\n{e}")

            tk.Button(frame, text="Save Duration", bg=THEME_RED, fg=THEME_WHITE,
                      font=("Segoe UI", 11, "bold"), width=16, relief="flat",
                      command=save_duration).pack(pady=15)

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
                    # IMPORTANT: tie image to admin window
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
