import customtkinter as ctk
import sqlite3
from datetime import datetime
from tkinter import messagebox
import tkinter as tk
import winsound
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NU_BLUE = "#0033A0"
NU_YELLOW = "#FFD100"
DARK_BG = "#1a1a1a"


class NQSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NQ Sync - Unified Queue System")
        self.root.geometry("700x500")

        self.root.resizable(True, True)
        self.root.minsize(700, 500)

        try:
            self.root.iconbitmap("NU Logo.ico")
        except Exception:
            try:
                self.app_icon = tk.PhotoImage(file="NU Logo.png")
                self.root.iconphoto(False, self.app_icon)
            except Exception as e:
                print(f"Hindi ma-load ang window icon: {e}")

        try:
            self.logo_image = ctk.CTkImage(
                light_image=Image.open("NU Logo.png"),
                dark_image=Image.open("NU Logo.png"),
                size=(120, 120)
            )
        except:
            self.logo_image = None

        self.init_db()
        self.current_frame = None
        self.show_main_menu()

    def center_target_window(self, target, width=700, height=500):
        target.update_idletasks()
        screen_width = target.winfo_screenwidth()
        screen_height = target.winfo_screenheight()
        x = int((screen_width // 2) - (width // 2)) - 100
        y = int((screen_height // 2) - (height // 2)) - 100
        target.geometry(f"{width}x{height}+{x}+{y}")

    def init_db(self):
        conn = sqlite3.connect("nq_sync.db")
        cursor = conn.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS tickets
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           ticket_no TEXT,
                           student_name TEXT,
                           service TEXT,
                           status TEXT,
                           counter TEXT,
                           timestamp TEXT
                       )
                       """)
        conn.commit()
        conn.close()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def limit_input_length(self, current_text, proposed_insert, limit=25):
        if len(current_text) + len(proposed_insert) > int(limit):
            return False
        return True

    def show_main_menu(self):
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self.root, fg_color="#0A0A0A")
        self.current_frame.pack(fill="both", expand=True)

        content_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        content_frame.pack(expand=True)

        if self.logo_image:
            ctk.CTkLabel(content_frame, image=self.logo_image, text="").pack(pady=(20, 5))

        ctk.CTkLabel(
            content_frame,
            text="NQ SYNC SYSTEM",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=NU_YELLOW
        ).pack()

        ctk.CTkLabel(
            content_frame,
            text="Education that works.",
            font=ctk.CTkFont(size=14, slant="italic"),
            text_color="#AAAAAA"
        ).pack(pady=(0, 25))

        glow_btn_style = {
            "width": 280,
            "height": 50,
            "font": ctk.CTkFont(size=14, weight="bold"),
            "border_width": 2,
            "border_color": NU_YELLOW,
            "hover_color": "#333333"
        }

        ctk.CTkButton(content_frame, text="STUDENT PORTAL", fg_color="#001F60", **glow_btn_style,
                      command=self.show_student_portal).pack(pady=10)
        ctk.CTkButton(content_frame, text="ADMIN DASHBOARD", fg_color="#1A1A1A", **glow_btn_style,
                      command=self.show_admin_dashboard).pack(pady=10)
        ctk.CTkButton(content_frame, text="TV DISPLAY SCREEN", fg_color="#004D26", **glow_btn_style,
                      command=self.show_display_screen).pack(pady=10)

        self.center_target_window(self.root, 700, 500)

    def show_student_portal(self):
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self.root)
        self.current_frame.pack(fill="both", expand=True)

        ctk.CTkButton(self.current_frame, text="← BACK", width=80, fg_color=NU_YELLOW, text_color="black",
                      command=self.show_main_menu).pack(anchor="w", padx=20, pady=10)

        content_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        content_frame.pack(expand=True)

        ctk.CTkLabel(content_frame, text="REGISTER TICKET", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=NU_YELLOW).pack(pady=5)

        ctk.CTkLabel(content_frame, text="Enter Full Name (Max 25 Characters):").pack(pady=(10, 0))

        vcmd = (self.root.register(self.limit_input_length), '%S', '%P')

        self.ent_name = ctk.CTkEntry(
            content_frame,
            width=350,
            height=40,
            border_color=NU_BLUE,
            validate="key",
            validatecommand=vcmd
        )
        self.ent_name.pack(pady=10)

        ctk.CTkLabel(content_frame, text="Select Service:").pack(pady=(10, 0))
        self.service_var = ctk.StringVar(value="Registrar")
        ctk.CTkComboBox(content_frame, values=["Registrar", "Accounting", "Clinic", "Library"],
                        variable=self.service_var, width=350, height=40).pack(pady=10)

        ctk.CTkButton(content_frame, text="GENERATE TICKET", fg_color=NU_BLUE, height=50, width=350,
                      command=self.generate_ticket).pack(pady=20)

        self.center_target_window(self.root, 700, 500)

    def generate_ticket(self):
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showwarning("Required", "Please enter your name.")
            return

        conn = sqlite3.connect("nq_sync.db")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM tickets WHERE status='Waiting'")
        people_ahead = cursor.fetchone()[0]

        avg_time_per_person = 5
        estimated_wait = people_ahead * avg_time_per_person

        cursor.execute("SELECT COUNT(*) FROM tickets")
        count = cursor.fetchone()[0] + 1
        ticket_no = f"{self.service_var.get()[0]}-{count:03d}"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute(
            "INSERT INTO tickets (ticket_no, student_name, service, status, timestamp) VALUES (?, ?, ?, 'Waiting', ?)",
            (ticket_no, name, self.service_var.get(), now))
        conn.commit()
        conn.close()

        message_body = (
            f"Registration Successful!\n\n"
            f"Ticket Number: {ticket_no}\n"
            f"Position in Queue: {people_ahead} person(s) ahead\n"
            f"Estimated Wait Time: ~{estimated_wait} minutes\n\n"
            "You may utilize this time for other activities. "
            "Please ensure you return to the area before your designated time."
        )

        messagebox.showinfo("Ticket Issued", message_body)
        self.show_main_menu()

    def show_admin_dashboard(self):
        self.password_win = ctk.CTkToplevel(self.root)
        self.password_win.title("Authentication")

        self.password_win.resizable(False, False)
        self.password_win.grab_set()
        self.password_win.attributes("-topmost", True)
        self.center_target_window(self.password_win, 320, 240)

        try:
            self.password_win.iconbitmap("NU Logo.ico")
        except:
            try:
                self.password_win.iconphoto(False, self.app_icon)
            except:
                pass

        ctk.CTkLabel(self.password_win, text="Enter Admin Password:", font=ctk.CTkFont(size=14, weight="bold")).pack(
            pady=(20, 5))

        self.pass_var = ctk.StringVar()

        def on_type(*args):
            if self.pass_var.get() == "admin123":
                self.password_win.destroy()
                self.open_admin_panel()
            else:
                self.lbl_error.configure(text="")

        self.pass_var.trace_add("write", on_type)

        pass_frame = ctk.CTkFrame(self.password_win, fg_color="transparent")
        pass_frame.pack(pady=5)

        self.pass_entry = ctk.CTkEntry(pass_frame, textvariable=self.pass_var, show="*", width=160)
        self.pass_entry.pack(side="left", padx=(20, 5))
        self.pass_entry.focus_set()

        self.is_shady = True

        def toggle_password():
            if self.is_shady:
                self.pass_entry.configure(show="")
                btn_eye.configure(text="🔒")
                self.is_shady = False
            else:
                self.pass_entry.configure(show="*")
                btn_eye.configure(text="👁️")
                self.is_shady = True

        btn_eye = ctk.CTkButton(pass_frame, text="👁️", width=35, fg_color="#333333", command=toggle_password)
        btn_eye.pack(side="left", padx=(0, 20))

        self.lbl_error = ctk.CTkLabel(self.password_win, text="", text_color="#FF3333", font=ctk.CTkFont(size=12))
        self.lbl_error.pack(pady=0)

        def manual_check():
            if self.pass_var.get() == "admin123":
                self.password_win.destroy()
                self.open_admin_panel()
            else:
                self.lbl_error.configure(text="❌ Incorrect Password")

        ctk.CTkButton(self.password_win, text="Login", width=120, fg_color=NU_BLUE, command=manual_check).pack(pady=15)

    def open_admin_panel(self):
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self.root, fg_color="#0A0A0A")
        self.current_frame.pack(fill="both", expand=True)

        ctk.CTkButton(self.current_frame, text="← BACK", width=80, fg_color="#1A1A1A",
                      border_width=1, border_color=NU_YELLOW, command=self.show_main_menu).pack(anchor="w", padx=20,
                                                                                                pady=10)

        content_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=40)

        top_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        top_row.pack(pady=5)

        ctk.CTkLabel(top_row, text="Counter: ", font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left")
        self.counter_var = ctk.StringVar(value="1")
        ctk.CTkComboBox(top_row, values=["1", "2", "3"], variable=self.counter_var, width=100).pack(side="left")

        self.queue_box = ctk.CTkTextbox(
            content_frame,
            width=550, height=230,
            scrollbar_button_color="#0A0A0A",
            scrollbar_button_hover_color="#0A0A0A",
            border_color=NU_YELLOW, border_width=2,
            text_color="white",
            fg_color="#121212",
            font=("Consolas", 14)
        )
        self.queue_box.pack(pady=10, fill="both", expand=True)

        ctk.CTkButton(content_frame, text="CALL NEXT STUDENT", fg_color=NU_BLUE,
                      border_width=2, border_color=NU_YELLOW, height=50, width=300, command=self.call_next).pack(
            pady=10)

        self.refresh_admin_list()

        self.center_target_window(self.root, 700, 500)

    def refresh_admin_list(self):
        try:
            if not hasattr(self, 'queue_box') or not self.queue_box.winfo_exists():
                return

            self.queue_box.delete("1.0", "end")
            conn = sqlite3.connect("nq_sync.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ticket_no, student_name, timestamp FROM tickets WHERE status='Waiting' ORDER BY timestamp ASC")

            now = datetime.now()
            for t, n, ts in cursor.fetchall():
                t_issued = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
                diff = now - t_issued
                mins_ago = int(diff.total_seconds() // 60)
                self.queue_box.insert("end", f" [ ] {t} - {n.upper()} ({mins_ago} mins ago)\n")

            conn.close()
            self.root.after(5000, self.refresh_admin_list)
        except Exception:
            pass

    def call_next(self):
        counter = self.counter_var.get()
        conn = sqlite3.connect("nq_sync.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, ticket_no, student_name, timestamp FROM tickets WHERE status='Waiting' ORDER BY timestamp ASC LIMIT 1")
        row = cursor.fetchone()

        if row:
            ticket_id, t_no, name, t_stamp = row

            start_time = datetime.strptime(t_stamp, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.now()
            duration = end_time - start_time

            seconds = int(duration.total_seconds())
            mins, secs = divmod(seconds, 60)
            wait_text = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

            cursor.execute("UPDATE tickets SET status='Completed' WHERE counter=? AND status='Serving'", (counter,))
            cursor.execute("UPDATE tickets SET status='Serving', counter=? WHERE id=?", (counter, ticket_id))
            conn.commit()

            try:
                winsound.PlaySound("notify.wav", winsound.SND_ASYNC)
            except:
                pass

            messagebox.showinfo("Calling",
                                f"Now Serving: {name}\n"
                                f"Ticket: {t_no}\n"
                                f"Counter: {counter}\n\n"
                                f"⏱ Total Wait Time: {wait_text}")
        else:
            messagebox.showwarning("Empty", "No students in queue.")
        conn.close()

    def show_display_screen(self):
        self.clear_frame()
        self.current_frame = ctk.CTkFrame(self.root, fg_color="#0a0a0a")
        self.current_frame.pack(fill="both", expand=True)

        ctk.CTkButton(self.current_frame, text="EXIT", width=60, fg_color="#333333", command=self.show_main_menu).place(
            x=10, y=10)

        self.header_label = ctk.CTkLabel(self.current_frame, text="NOW SERVING",
                                         font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        self.header_label.place(relx=0.5, rely=0.15, anchor="center")

        self.lbl_ticket = ctk.CTkLabel(self.current_frame, text="---", font=ctk.CTkFont(size=90, weight="bold"),
                                       text_color=NU_YELLOW)
        self.lbl_ticket.place(relx=0.5, rely=0.35, anchor="center")

        self.lbl_name = ctk.CTkLabel(
            self.current_frame,
            text="Please wait...",
            font=ctk.CTkFont(size=28),
            text_color="white",
            wraplength=600,
            justify="center"
        )
        self.lbl_name.place(relx=0.5, rely=0.55, anchor="center")

        self.lbl_counter = ctk.CTkLabel(
            self.current_frame,
            text="COUNTER -",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=NU_BLUE,
            fg_color=NU_YELLOW,
            corner_radius=10,
            width=350,
            height=60
        )
        self.lbl_counter.place(relx=0.5, rely=0.75, anchor="center")

        self.footer_frame = ctk.CTkFrame(self.current_frame, fg_color="#1a1a1a", height=80)
        self.footer_frame.pack(side="bottom", fill="x")

        self.lbl_waiting = ctk.CTkLabel(self.footer_frame, text="PREPARING: ---", font=ctk.CTkFont(size=16),
                                        text_color="#aaaaaa")
        self.lbl_waiting.pack(side="left", padx=20, pady=15)

        self.lbl_est_time = ctk.CTkLabel(self.footer_frame, text="EST. WAIT: 0 MINS",
                                         font=ctk.CTkFont(size=14, weight="bold"), text_color=NU_YELLOW)
        self.lbl_est_time.pack(side="right", padx=20, pady=15)

        self.update_tv_display()

        self.center_target_window(self.root, 700, 500)

    def update_tv_display(self):
        try:
            if not hasattr(self, 'lbl_ticket') or not self.lbl_ticket.winfo_exists():
                return

            conn = sqlite3.connect("nq_sync.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT ticket_no, student_name, counter FROM tickets WHERE status='Serving' ORDER BY timestamp DESC LIMIT 1")
            serving = cursor.fetchone()

            if serving:
                self.lbl_ticket.configure(text=serving[0])
                self.lbl_name.configure(text=serving[1].upper())
                self.lbl_counter.configure(text=f"PROCEED TO COUNTER {serving[2]}")
            else:
                self.lbl_ticket.configure(text="---")
                self.lbl_name.configure(text="READY TO SERVE")
                self.lbl_counter.configure(text="WAITING FOR NEXT")

            cursor.execute("SELECT ticket_no FROM tickets WHERE status='Waiting' ORDER BY timestamp ASC LIMIT 5")
            waiting_list = cursor.fetchall()
            waiting_text = "  •  ".join([w[0] for w in waiting_list])
            self.lbl_waiting.configure(text=f"ON DECK: {waiting_text}" if waiting_text else "NO PENDING TICKETS")

            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status='Waiting'")
            count_waiting = cursor.fetchone()[0]
            avg_time = 5
            total_est = count_waiting * avg_time

            if hasattr(self, 'lbl_est_time'):
                self.lbl_est_time.configure(text=f"EST. WAIT: ~{total_est} MINS ({count_waiting} in queue)")

            conn.close()
            self.root.after(3000, self.update_tv_display)
        except Exception:
            pass


if __name__ == "__main__":
    root = ctk.CTk()
    app = NQSyncApp(root)
    app.center_target_window(root, 700, 500)
    root.mainloop()