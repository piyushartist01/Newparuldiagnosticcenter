import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from api_client import ApiClient

# Modern Health Theme Colors
BG_COLOR = "#f0fdf4"       # Very light green background
SIDEBAR_BG = "#064e3b"     # Very dark emerald for sidebar
SIDEBAR_FG = "#a7f3d0"     # Light emerald text
SIDEBAR_ACTIVE = "#10b981" # Bright emerald active state
ACCENT = "#059669"         # Primary Emerald button
TEXT_COLOR = "#0f172a"
CARD_BG = "#ffffff"

class AdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Admin Panel - New Parul Diagnostic")
        self.geometry("1050x700")
        self.configure(bg=BG_COLOR)
        
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        style.configure('TFrame', background=BG_COLOR)
        style.configure('Card.TFrame', background=CARD_BG, relief='flat', borderwidth=0)
        style.configure('Sidebar.TFrame', background=SIDEBAR_BG)
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=6, borderwidth=0)
        style.configure('Accent.TButton', background=ACCENT, foreground='white')
        style.map('Accent.TButton', background=[('active', SIDEBAR_ACTIVE)])
        
        style.configure('TLabel', background=BG_COLOR, font=('Segoe UI', 10), foreground=TEXT_COLOR)
        style.configure('Header.TLabel', font=('Segoe UI', 20, 'bold'), foreground=SIDEBAR_BG)
        style.configure('Loading.TLabel', font=('Segoe UI', 12), foreground=ACCENT)

        self.api = ApiClient()
        self.poll_timer = None
        
        self.show_login()

    # ---- Threading helper ----
    def _run_async(self, api_call, callback):
        """Run api_call in a background thread, then schedule callback on the main thread."""
        def worker():
            result = api_call()
            self.after(0, callback, result)
        threading.Thread(target=worker, daemon=True).start()

    def _show_loading(self, parent=None):
        """Show a loading label in the content area."""
        target = parent or self.content
        lbl = ttk.Label(target, text="⏳ Processing...", style='Loading.TLabel')
        lbl.pack(pady=40)
        return lbl

    # ---- LOGIN ----
    def show_login(self):
        self.clear_polling()
        for widget in self.winfo_children():
            widget.destroy()
            
        frame = ttk.Frame(self, style='Card.TFrame', padding=40)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(frame, text="🏥 New Parul Diagnostic", font=('Segoe UI', 18, 'bold'), background=CARD_BG, foreground=SIDEBAR_BG).pack(pady=(0, 25))
        
        ttk.Label(frame, text="Username", background=CARD_BG, font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        self.user_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.user_var, width=35, font=('Segoe UI', 11)).pack(pady=(5, 15), ipady=6)
        
        ttk.Label(frame, text="Password", background=CARD_BG, font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        self.pw_var = tk.StringVar()
        pw_entry = ttk.Entry(frame, textvariable=self.pw_var, show='*', width=35, font=('Segoe UI', 11))
        pw_entry.pack(pady=(5, 25), ipady=6)
        pw_entry.bind('<Return>', lambda e: self.do_login())
        
        self.login_btn = ttk.Button(frame, text="Secure Sign In", style='Accent.TButton', command=self.do_login)
        self.login_btn.pack(fill='x', ipady=6)
        
        self.login_status = ttk.Label(frame, text="", background=CARD_BG, foreground='#64748b')
        self.login_status.pack(pady=(15, 0))

    def do_login(self):
        username = self.user_var.get().strip()
        pwd = self.pw_var.get()
        if not username or not pwd:
            messagebox.showerror("Error", "Enter username and password.")
            return
        
        self.login_btn.configure(state='disabled')
        self.login_status.configure(text="⏳ Authenticating...", foreground=ACCENT)
        
        def on_result(result):
            ok, msg = result
            if ok:
                self.show_main()
            else:
                self.login_status.configure(text=f"❌ {msg}", foreground='#ef4444')
                self.login_btn.configure(state='normal')
        
        self._run_async(lambda: self.api.login(username, pwd), on_result)

    # ---- MAIN LAYOUT ----
    def show_main(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        sidebar = ttk.Frame(self, style='Sidebar.TFrame', width=220)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        ttk.Label(sidebar, text="🏥 Admin Control", background=SIDEBAR_BG, foreground='white', font=('Segoe UI', 15, 'bold')).pack(pady=30, padx=15, anchor='w')
        
        menus = [
            ("📊 Dashboard", self.show_dashboard),
            ("📅 Appointments", self.show_appointments),
            ("🔬 Services", self.show_services),
            ("💬 Messages", self.show_messages),
        ]
        
        for text, cmd in menus:
            btn = tk.Button(sidebar, text=text, bg=SIDEBAR_BG, fg=SIDEBAR_FG, bd=0, font=('Segoe UI', 11, 'bold'), activebackground=SIDEBAR_ACTIVE, activeforeground='white', cursor='hand2', anchor='w', padx=25, pady=12, command=cmd)
            btn.pack(fill='x', pady=2)
            
        tk.Frame(sidebar, bg=SIDEBAR_BG).pack(fill='both', expand=True)
        
        ttk.Label(sidebar, text=f"👤 {self.api.user.get('username', 'Admin')}", background=SIDEBAR_BG, foreground=SIDEBAR_FG).pack(pady=5, padx=20, anchor='w')
        tk.Button(sidebar, text="🚪 Secure Log Out", bg=SIDEBAR_BG, fg='#ef4444', bd=0, font=('Segoe UI', 10, 'bold'), activebackground='#fef2f2', activeforeground='#ef4444', cursor='hand2', anchor='w', padx=25, pady=15, command=self.do_logout).pack(fill='x', pady=(0, 20))

        self.content = ttk.Frame(self)
        self.content.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        self.show_dashboard()

    def do_logout(self):
        self.clear_polling()
        self.api.logout()
        self.show_login()

    def clear_content(self):
        self.clear_polling()
        for w in self.content.winfo_children():
            w.destroy()

    def clear_polling(self):
        if self.poll_timer:
            self.after_cancel(self.poll_timer)
            self.poll_timer = None

    # --- DASHBOARD ---
    def show_dashboard(self, is_refresh=False):
        if not is_refresh:
            self.clear_content()
            self._build_dashboard_header()
            self._show_loading()

        def on_result(result):
            data, err = result
            if not is_refresh:
                self.clear_content()
                self._build_dashboard_header()

            if err:
                if not is_refresh:
                    ttk.Label(self.content, text=f"❌ Network Error: {err}", foreground='#ef4444').pack(pady=20)
                return

            if is_refresh and hasattr(self, 'stats_frame'):
                self.stats_frame.destroy()
                self.recent_lbl.destroy()
                self.tree.destroy()

            self.stats_frame = ttk.Frame(self.content)
            self.stats_frame.pack(fill='x', pady=(0, 30))
            
            stats = [
                ("TODAY'S BOOKINGS", data.get('todays_appointments', 0), "#3b82f6"),
                ("PENDING ACTION", data.get('pending', 0), "#f59e0b"),
                ("CONFIRMED", data.get('confirmed', 0), ACCENT),
                ("UNREAD MSGS", data.get('unread_messages', 0), "#ef4444"),
                ("TOTAL ALOTMENTS", data.get('total', 0), SIDEBAR_BG),
            ]
            
            for i, (title, val, color) in enumerate(stats):
                card = tk.Frame(self.stats_frame, bg=CARD_BG, padx=20, pady=20)
                card.grid(row=0, column=i, padx=8, sticky='nsew')
                self.stats_frame.grid_columnconfigure(i, weight=1)
                tk.Label(card, text=title, font=('Segoe UI', 9, 'bold'), fg='#64748b', bg=CARD_BG).pack(anchor='w')
                tk.Label(card, text=str(val), font=('Segoe UI', 26, 'bold'), fg=color, bg=CARD_BG).pack(anchor='w', pady=(5,0))
                
            self.recent_lbl = ttk.Label(self.content, text="Latest Automated Activity", font=('Segoe UI', 13, 'bold'))
            self.recent_lbl.pack(anchor='w', pady=(10, 10))
            
            style = ttk.Style()
            style.configure("Custom.Treeview", rowheight=35, font=('Segoe UI', 10), background="white", fieldbackground="white")
            style.configure("Custom.Treeview.Heading", font=('Segoe UI', 10, 'bold'), background="#e2e8f0")
            
            cols = ('Patient', 'Service', 'Date', 'Status')
            self.tree = ttk.Treeview(self.content, columns=cols, show='headings', height=8, style="Custom.Treeview")
            for col in cols:
                self.tree.heading(col, text=col.upper())
                self.tree.column(col, width=150)
            self.tree.pack(fill='both', expand=True)
            
            for appt in data.get('recent_appointments', []):
                self.tree.insert('', 'end', values=(appt['patient_name'], appt['service_type'], appt['appointment_date'], appt['status'].upper()))

            # Automated Polling Loop (Fully Automated Dashboard)
            self.poll_timer = self.after(30000, lambda: self.show_dashboard(is_refresh=True))

        self._run_async(lambda: self.api.get_dashboard(), on_result)

    def _build_dashboard_header(self):
        hdr = ttk.Frame(self.content)
        hdr.pack(fill='x', pady=(0, 25))
        ttk.Label(hdr, text="Dashboard Overview", style='Header.TLabel').pack(side='left')
        ttk.Label(hdr, text="🟢 Live Sync Active", font=('Segoe UI', 10, 'bold'), foreground=SIDEBAR_ACTIVE).pack(side='right', pady=8)

    # --- APPOINTMENTS ---
    def show_appointments(self, status_filter=""):
        self.clear_content()
        
        hdr_frame = ttk.Frame(self.content)
        hdr_frame.pack(fill='x', pady=(0, 25))
        ttk.Label(hdr_frame, text="Manage Appointments", style='Header.TLabel').pack(side='left')
        ttk.Button(hdr_frame, text="📥 Export CSV", command=self.export_csv).pack(side='right')
        
        filter_var = tk.StringVar(value=status_filter.title() if status_filter else "All")
        cb = ttk.Combobox(hdr_frame, textvariable=filter_var, values=["All", "Pending", "Confirmed", "Completed", "Cancelled"], state='readonly', width=15)
        cb.pack(side='right', padx=20)
        ttk.Label(hdr_frame, text="Filter:", font=('Segoe UI', 10, 'bold')).pack(side='right')
        cb.bind('<<ComboboxSelected>>', lambda e: self.show_appointments("" if filter_var.get() == "All" else filter_var.get().lower()))

        self._show_loading()

        def on_result(result):
            data, err = result
            for w in self.content.winfo_children():
                if isinstance(w, ttk.Label) and "Processing" in str(w.cget('text')):
                    w.destroy()

            if err:
                ttk.Label(self.content, text=f"❌ {err}", foreground='#ef4444').pack(pady=20)
                return

            cols = ('ID', 'Patient', 'Phone', 'Date', 'Time', 'Service', 'Status')
            tree = ttk.Treeview(self.content, columns=cols, show='headings', selectmode='browse', style="Custom.Treeview")
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            tree.column('ID', width=45)
            tree.column('Patient', width=180)
            tree.pack(fill='both', expand=True)

            for appt in data:
                time_disp = appt['appointment_time'] if appt['appointment_time'] else "N/A"
                tree.insert('', 'end', values=(appt['id'], appt['patient_name'], appt['phone'], appt['appointment_date'], time_disp, appt['service_type'], appt['status'].upper()))

            btn_frame = ttk.Frame(self.content)
            btn_frame.pack(fill='x', pady=(20, 0))
            
            def update_status(new_st):
                sel = tree.selection()
                if not sel: return messagebox.showwarning("Warning", "Select an appointment")
                appt_id = tree.item(sel[0])['values'][0]
                self._run_async(
                    lambda: self.api.update_appointment_status(appt_id, new_st),
                    lambda r: self.show_appointments(status_filter) if not r[1] else messagebox.showerror("Error", r[1])
                )
                
            ttk.Button(btn_frame, text="✅ Confirm", style='Accent.TButton', command=lambda: update_status('confirmed')).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="✔ Complete", command=lambda: update_status('completed')).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="✖ Cancel", command=lambda: update_status('cancelled')).pack(side='left', padx=5)

        self._run_async(lambda: self.api.get_appointments(status_filter), on_result)

    def export_csv(self):
        def on_result(result):
            data, err = result
            if err: return messagebox.showerror("Error", err)
            fpath = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="appointments.csv", filetypes=[("CSV Files", "*.csv")])
            if fpath:
                with open(fpath, "w", encoding="utf-8") as f: f.write(data)
                messagebox.showinfo("Exported", f"Data safely exported to {fpath}")
        self._run_async(lambda: self.api.export_appointments_csv(), on_result)

    # --- SERVICES ---
    def show_services(self):
        self.clear_content()
        hdr = ttk.Frame(self.content)
        hdr.pack(fill='x', pady=(0, 25))
        ttk.Label(hdr, text="Service Protocols", style='Header.TLabel').pack(side='left')
        ttk.Button(hdr, text="➕ Build Service", style='Accent.TButton', command=self.add_service).pack(side='right')

        self._show_loading()

        def on_result(result):
            data, err = result
            for w in self.content.winfo_children():
                if "Processing" in str(w.cget('text')) if isinstance(w, ttk.Label) else False: w.destroy()

            if err: return ttk.Label(self.content, text=f"❌ {err}", foreground='#ef4444').pack(pady=20)

            cols = ('ID', 'Name', 'Description', 'Price (₹)')
            tree = ttk.Treeview(self.content, columns=cols, show='headings', selectmode='browse', style="Custom.Treeview")
            for col in cols: tree.heading(col, text=col)
            tree.column('ID', width=45)
            tree.column('Description', width=400)
            tree.pack(fill='both', expand=True)

            for svc in data:
                tree.insert('', 'end', values=(svc['id'], svc['service_name'], svc['description'][:60]+"...", f"₹{svc['price']:.0f}"))

            btn_frame = ttk.Frame(self.content)
            btn_frame.pack(fill='x', pady=(20, 0))
            
            def edit_svc():
                sel = tree.selection()
                if not sel: return messagebox.showwarning("Warning", "Select a service")
                # Get full data directly from list
                sid = tree.item(sel[0])['values'][0]
                target = next(s for s in data if s['id'] == sid)
                self.edit_service(target['id'], target['service_name'], target['description'], str(target['price']))

            ttk.Button(btn_frame, text="✏️ Manage Service", command=edit_svc).pack(side='left', padx=5)

        self._run_async(lambda: self.api.get_services(), on_result)

    def add_service(self): self._service_dialog("Build Service")
    def edit_service(self, sid, name, desc, price): self._service_dialog("Manage Service", sid, name, desc, price)
        
    def _service_dialog(self, title, sid=None, name="", desc="", price=""):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.geometry("450x330")
        dlg.configure(bg=CARD_BG)
        dlg.transient(self)
        dlg.grab_set()
        
        f = ttk.Frame(dlg, padding=25, style='Card.TFrame')
        f.pack(fill='both', expand=True)
        
        ttk.Label(f, text="Nomenclature:", font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        n_var = tk.StringVar(value=name)
        ttk.Entry(f, textvariable=n_var, font=('Segoe UI', 11)).pack(fill='x', pady=(5, 15), ipady=5)
        
        ttk.Label(f, text="Description Protocol:", font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        d_var = tk.StringVar(value=desc)
        ttk.Entry(f, textvariable=d_var, font=('Segoe UI', 11)).pack(fill='x', pady=(5, 15), ipady=5)
        
        ttk.Label(f, text="Diagnostic Fee (₹):", font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        p_var = tk.StringVar(value=price)
        ttk.Entry(f, textvariable=p_var, font=('Segoe UI', 11)).pack(fill='x', pady=(5, 25), ipady=5)
        
        def save():
            n, d, p = n_var.get().strip(), d_var.get().strip(), p_var.get().strip()
            if not n: return messagebox.showerror("System Halt", "Nomenclature required", parent=dlg)
            try: p_val = float(p) if p else 0.0
            except: p_val = 0.0
            
            call = lambda: self.api.update_service(sid, n, d, p_val) if sid else self.api.add_service(n, d, p_val)
            def on_result(result):
                _, err = result
                if err: messagebox.showerror("Error", err, parent=dlg)
                else: dlg.destroy(); self.show_services()
            
            self._run_async(call, on_result)
                 
        ttk.Button(f, text="Process Record", style='Accent.TButton', command=save).pack(side='right', padx=5)
        ttk.Button(f, text="Abort", command=dlg.destroy).pack(side='right')

    # --- MESSAGES ---
    def show_messages(self):
        self.clear_content()
        ttk.Label(self.content, text="Secure Inbox", style='Header.TLabel').pack(anchor='w', pady=(0, 25))

        self._show_loading()

        def on_result(result):
            data, err = result
            for w in self.content.winfo_children():
                if "Processing" in str(w.cget('text')) if isinstance(w, ttk.Label) else False: w.destroy()

            if err: return ttk.Label(self.content, text=f"❌ {err}", foreground='#ef4444').pack(pady=20)

            cols = ('ID', 'Name', 'Message Overview', 'Status')
            tree = ttk.Treeview(self.content, columns=cols, show='headings', selectmode='browse', style="Custom.Treeview")
            for col in cols: tree.heading(col, text=col)
            tree.column('ID', width=45)
            tree.column('Message Overview', width=350)
            tree.pack(fill='both', expand=True)

            for msg in data:
                s_msg = msg['message'][:80] + ("..." if len(msg['message']) > 80 else "")
                r_st = "READ" if msg['is_read'] else "UNREAD"
                item = tree.insert('', 'end', values=(msg['id'], msg['name'], s_msg, r_st))
                if not msg['is_read']: tree.item(item, tags=('unread',))
                    
            tree.tag_configure('unread', background='#fef3c7', foreground='#b45309')

            btn_frame = ttk.Frame(self.content)
            btn_frame.pack(fill='x', pady=(20, 0))
            
            def mark_read():
                sel = tree.selection()
                if not sel: return messagebox.showwarning("Warning", "Select a message")
                mid = tree.item(sel[0])['values'][0]
                self._run_async(lambda: self.api.mark_message_read(mid), lambda r: self.show_messages() if not r[1] else messagebox.showerror("Error", r[1]))

            ttk.Button(btn_frame, text="✅ Resolve Message", style='Accent.TButton', command=mark_read).pack(side='left')

        self._run_async(lambda: self.api.get_messages(), on_result)

if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
