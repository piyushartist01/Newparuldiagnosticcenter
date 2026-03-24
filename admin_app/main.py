import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from api_client import ApiClient

# Colors
BG_COLOR = "#f1f5f9"
SIDEBAR_BG = "#1e293b"
SIDEBAR_FG = "#94a3b8"
SIDEBAR_ACTIVE = "#2563eb"
ACCENT = "#2563eb"
TEXT_COLOR = "#1e293b"

class AdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Admin Panel - New Parul Diagnostic")
        self.geometry("1000x650")
        self.configure(bg=BG_COLOR)
        
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        style.configure('TFrame', background=BG_COLOR)
        style.configure('Card.TFrame', background='white', relief='solid', borderwidth=1)
        style.configure('Sidebar.TFrame', background=SIDEBAR_BG)
        style.configure('TButton', font=('Segoe UI', 10), padding=5)
        style.configure('Accent.TButton', background=ACCENT, foreground='white')
        style.configure('TLabel', background=BG_COLOR, font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'))
        style.configure('Loading.TLabel', font=('Segoe UI', 12), foreground='#64748b')

        self.api = ApiClient()
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
        lbl = ttk.Label(target, text="⏳ Loading...", style='Loading.TLabel')
        lbl.pack(pady=40)
        return lbl

    # ---- LOGIN ----
    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        frame = ttk.Frame(self, style='Card.TFrame', padding=30)
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(frame, text="🏥 New Parul Diagnostic", font=('Segoe UI', 16, 'bold'), background='white').pack(pady=(0, 20))
        
        ttk.Label(frame, text="Username", background='white').pack(anchor='w')
        self.user_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.user_var, width=30, font=('Segoe UI', 11)).pack(pady=(0, 15), ipady=5)
        
        ttk.Label(frame, text="Password", background='white').pack(anchor='w')
        self.pw_var = tk.StringVar()
        pw_entry = ttk.Entry(frame, textvariable=self.pw_var, show='*', width=30, font=('Segoe UI', 11))
        pw_entry.pack(pady=(0, 20), ipady=5)
        pw_entry.bind('<Return>', lambda e: self.do_login())
        
        self.login_btn = ttk.Button(frame, text="Sign In", style='Accent.TButton', command=self.do_login)
        self.login_btn.pack(fill='x', ipady=5)
        
        self.login_status = ttk.Label(frame, text="", background='white', foreground='#64748b')
        self.login_status.pack(pady=(10, 0))

    def do_login(self):
        username = self.user_var.get().strip()
        pwd = self.pw_var.get()
        if not username or not pwd:
            messagebox.showerror("Error", "Enter username and password.")
            return
        
        self.login_btn.configure(state='disabled')
        self.login_status.configure(text="⏳ Signing in...", foreground='#64748b')
        
        def api_call():
            return self.api.login(username, pwd)
        
        def on_result(result):
            ok, msg = result
            if ok:
                self.show_main()
            else:
                self.login_status.configure(text=f"❌ {msg}", foreground='#ef4444')
                self.login_btn.configure(state='normal')
        
        self._run_async(api_call, on_result)

    # ---- MAIN LAYOUT ----
    def show_main(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        sidebar = ttk.Frame(self, style='Sidebar.TFrame', width=200)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        ttk.Label(sidebar, text="🏥 Admin Panel", background=SIDEBAR_BG, foreground='white', font=('Segoe UI', 14, 'bold')).pack(pady=20, padx=10, anchor='w')
        
        menus = [
            ("📊 Dashboard", self.show_dashboard),
            ("📅 Appointments", self.show_appointments),
            ("🔬 Services", self.show_services),
            ("💬 Messages", self.show_messages),
        ]
        
        for text, cmd in menus:
            btn = tk.Button(sidebar, text=text, bg=SIDEBAR_BG, fg=SIDEBAR_FG, bd=0, font=('Segoe UI', 11), activebackground='#334155', activeforeground='white', cursor='hand2', anchor='w', padx=20, pady=10, command=cmd)
            btn.pack(fill='x', pady=2)
            
        tk.Frame(sidebar, bg=SIDEBAR_BG).pack(fill='both', expand=True)
        
        ttk.Label(sidebar, text=f"👤 {self.api.user.get('username', 'Admin')}", background=SIDEBAR_BG, foreground=SIDEBAR_FG).pack(pady=5, padx=20, anchor='w')
        tk.Button(sidebar, text="🚪 Sign Out", bg=SIDEBAR_BG, fg='#ef4444', bd=0, font=('Segoe UI', 11), activebackground='#fef2f2', activeforeground='#ef4444', cursor='hand2', anchor='w', padx=20, pady=10, command=self.do_logout).pack(fill='x', pady=(0, 20))

        self.content = ttk.Frame(self)
        self.content.pack(side='right', fill='both', expand=True, padx=20, pady=20)
        
        self.show_dashboard()

    def do_logout(self):
        self.api.logout()
        self.show_login()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # --- DASHBOARD ---
    def show_dashboard(self):
        self.clear_content()

        hdr_frame = ttk.Frame(self.content)
        hdr_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(hdr_frame, text="Dashboard", style='Header.TLabel').pack(side='left')
        ttk.Button(hdr_frame, text="🔄 Refresh", command=self.show_dashboard).pack(side='right')

        self._show_loading()

        def api_call():
            return self.api.get_dashboard()

        def on_result(result):
            data, err = result
            # Clear loading
            self.clear_content()
            # Re-add header
            hdr = ttk.Frame(self.content)
            hdr.pack(fill='x', pady=(0, 20))
            ttk.Label(hdr, text="Dashboard", style='Header.TLabel').pack(side='left')
            ttk.Button(hdr, text="🔄 Refresh", command=self.show_dashboard).pack(side='right')

            if err:
                ttk.Label(self.content, text=f"❌ {err}", foreground='#ef4444').pack(pady=20)
                return

            stats_frame = ttk.Frame(self.content)
            stats_frame.pack(fill='x', pady=(0, 20))
            
            stats = [
                ("Today's Appts", data.get('todays_appointments', 0)),
                ("Pending", data.get('pending', 0)),
                ("Confirmed", data.get('confirmed', 0)),
                ("Unread Msgs", data.get('unread_messages', 0)),
                ("Total Appts", data.get('total', 0)),
            ]
            
            for i, (title, val) in enumerate(stats):
                card = ttk.Frame(stats_frame, style='Card.TFrame', padding=15)
                card.grid(row=0, column=i, padx=5, sticky='nsew')
                stats_frame.grid_columnconfigure(i, weight=1)
                ttk.Label(card, text=title.upper(), font=('Segoe UI', 9, 'bold'), foreground='#64748b', background='white').pack(anchor='w')
                ttk.Label(card, text=str(val), font=('Segoe UI', 20, 'bold'), background='white').pack(anchor='w')
                
            ttk.Label(self.content, text="Recent Appointments", font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(10, 5))
            
            cols = ('Patient', 'Service', 'Date', 'Time', 'Status')
            tree = ttk.Treeview(self.content, columns=cols, show='headings', height=10)
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            tree.pack(fill='both', expand=True)
            
            for appt in data.get('recent_appointments', []):
                tree.insert('', 'end', values=(appt['patient_name'], appt['service_type'], appt['appointment_date'], appt['appointment_time'], appt['status'].title()))

        self._run_async(api_call, on_result)

    # --- APPOINTMENTS ---
    def show_appointments(self, status_filter=""):
        self.clear_content()
        
        hdr_frame = ttk.Frame(self.content)
        hdr_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(hdr_frame, text="Appointments", style='Header.TLabel').pack(side='left')
        
        ttk.Button(hdr_frame, text="📥 Export CSV", command=self.export_csv).pack(side='right')
        
        filter_var = tk.StringVar(value=status_filter.title() if status_filter else "All")
        cb = ttk.Combobox(hdr_frame, textvariable=filter_var, values=["All", "Pending", "Confirmed", "Completed", "Cancelled"], state='readonly', width=12)
        cb.pack(side='right', padx=15)
        ttk.Label(hdr_frame, text="Filter:").pack(side='right')
        cb.bind('<<ComboboxSelected>>', lambda e: self.show_appointments("" if filter_var.get() == "All" else filter_var.get().lower()))

        self._show_loading()

        def api_call():
            return self.api.get_appointments(status_filter)

        def on_result(result):
            data, err = result
            # Remove loading label (keep header)
            for w in self.content.winfo_children():
                if isinstance(w, ttk.Label) and "Loading" in str(w.cget('text')):
                    w.destroy()

            if err:
                ttk.Label(self.content, text=f"❌ {err}", foreground='#ef4444').pack(pady=20)
                return

            cols = ('ID', 'Patient', 'Email', 'Phone', 'Date', 'Time', 'Service', 'Status')
            tree = ttk.Treeview(self.content, columns=cols, show='headings', selectmode='browse')
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=80 if col != 'Email' else 150)
            tree.column('ID', width=40)
            tree.pack(fill='both', expand=True)

            for appt in data:
                tree.insert('', 'end', values=(appt['id'], appt['patient_name'], appt['email'], appt['phone'], appt['appointment_date'], appt['appointment_time'], appt['service_type'], appt['status'].title()))

            btn_frame = ttk.Frame(self.content)
            btn_frame.pack(fill='x', pady=(15, 0))
            
            def update_status(new_st):
                sel = tree.selection()
                if not sel: return messagebox.showwarning("Warning", "Select an appointment")
                appt_id = tree.item(sel[0])['values'][0]
                self._run_async(
                    lambda: self.api.update_appointment_status(appt_id, new_st),
                    lambda r: self.show_appointments(status_filter) if not r[1] else messagebox.showerror("Error", r[1])
                )
                
            def del_appt():
                sel = tree.selection()
                if not sel: return messagebox.showwarning("Warning", "Select an appointment")
                appt_id = tree.item(sel[0])['values'][0]
                if messagebox.askyesno("Confirm", f"Delete appointment #{appt_id}?"):
                    self._run_async(
                        lambda: self.api.delete_appointment(appt_id),
                        lambda r: self.show_appointments(status_filter) if not r[1] else messagebox.showerror("Error", r[1])
                    )

            ttk.Button(btn_frame, text="✅ Confirm", command=lambda: update_status('confirmed')).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="✔ Complete", command=lambda: update_status('completed')).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="✖ Cancel", command=lambda: update_status('cancelled')).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="🗑 Delete", command=del_appt).pack(side='right', padx=5)

        self._run_async(api_call, on_result)

    def export_csv(self):
        def api_call():
            return self.api.export_appointments_csv()
        def on_result(result):
            data, err = result
            if err: return messagebox.showerror("Error", err)
            fpath = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="appointments.csv", filetypes=[("CSV Files", "*.csv")])
            if fpath:
                with open(fpath, "w", encoding="utf-8") as f: f.write(data)
                messagebox.showinfo("Exported", f"Saved to {fpath}")
        self._run_async(api_call, on_result)

    # --- SERVICES ---
    def show_services(self):
        self.clear_content()
        
        hdr_frame = ttk.Frame(self.content)
        hdr_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(hdr_frame, text="Services", style='Header.TLabel').pack(side='left')
        ttk.Button(hdr_frame, text="➕ Add Service", style='Accent.TButton', command=self.add_service).pack(side='right')

        self._show_loading()

        def api_call():
            return self.api.get_services()

        def on_result(result):
            data, err = result
            for w in self.content.winfo_children():
                if isinstance(w, ttk.Label) and "Loading" in str(w.cget('text')):
                    w.destroy()

            if err:
                ttk.Label(self.content, text=f"❌ {err}", foreground='#ef4444').pack(pady=20)
                return

            cols = ('ID', 'Name', 'Description', 'Price (₹)')
            tree = ttk.Treeview(self.content, columns=cols, show='headings', selectmode='browse')
            for col in cols: tree.heading(col, text=col)
            tree.column('ID', width=40)
            tree.column('Description', width=300)
            tree.pack(fill='both', expand=True)

            for svc in data:
                tree.insert('', 'end', values=(svc['id'], svc['service_name'], svc['description'], f"₹{svc['price']:.0f}"))

            btn_frame = ttk.Frame(self.content)
            btn_frame.pack(fill='x', pady=(15, 0))
            
            def edit_svc():
                sel = tree.selection()
                if not sel: return messagebox.showwarning("Warning", "Select a service")
                vals = tree.item(sel[0])['values']
                self.edit_service(vals[0], vals[1], vals[2], str(vals[3]).replace('₹',''))
                
            def del_svc():
                sel = tree.selection()
                if not sel: return messagebox.showwarning("Warning", "Select a service")
                svc_id, name = tree.item(sel[0])['values'][0:2]
                if messagebox.askyesno("Confirm", f"Delete service '{name}'?"):
                    self._run_async(
                        lambda: self.api.delete_service(svc_id),
                        lambda r: self.show_services() if not r[1] else messagebox.showerror("Error", r[1])
                    )

            ttk.Button(btn_frame, text="✏️ Edit", command=edit_svc).pack(side='right', padx=5)
            ttk.Button(btn_frame, text="🗑 Delete", command=del_svc).pack(side='right', padx=5)

        self._run_async(api_call, on_result)

    def add_service(self):
        self._service_dialog("Add Service")
        
    def edit_service(self, sid, name, desc, price):
        self._service_dialog("Edit Service", sid, name, desc, price)
        
    def _service_dialog(self, title, sid=None, name="", desc="", price=""):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.geometry("400x300")
        dlg.transient(self)
        dlg.grab_set()
        
        f = ttk.Frame(dlg, padding=20)
        f.pack(fill='both', expand=True)
        
        ttk.Label(f, text="Name:").pack(anchor='w')
        n_var = tk.StringVar(value=name)
        ttk.Entry(f, textvariable=n_var).pack(fill='x', pady=(0, 10))
        
        ttk.Label(f, text="Description:").pack(anchor='w')
        d_var = tk.StringVar(value=desc)
        ttk.Entry(f, textvariable=d_var).pack(fill='x', pady=(0, 10))
        
        ttk.Label(f, text="Price (₹):").pack(anchor='w')
        p_var = tk.StringVar(value=price)
        ttk.Entry(f, textvariable=p_var).pack(fill='x', pady=(0, 20))
        
        def save():
            n, d, p = n_var.get().strip(), d_var.get().strip(), p_var.get().strip()
            if not n: return messagebox.showerror("Error", "Name required", parent=dlg)
            try: p_val = float(p) if p else 0.0
            except: p_val = 0.0
            
            def api_call():
                if sid:
                    return self.api.update_service(sid, n, d, p_val)
                else:
                    return self.api.add_service(n, d, p_val)
            
            def on_result(result):
                _, err = result
                if err: messagebox.showerror("Error", err, parent=dlg)
                else:
                    dlg.destroy()
                    self.show_services()
            
            self._run_async(api_call, on_result)
                
        ttk.Button(f, text="Save", style='Accent.TButton', command=save).pack(side='right', padx=5)
        ttk.Button(f, text="Cancel", command=dlg.destroy).pack(side='right')

    # --- MESSAGES ---
    def show_messages(self):
        self.clear_content()
        ttk.Label(self.content, text="Contact Messages", style='Header.TLabel').pack(anchor='w', pady=(0, 15))

        self._show_loading()

        def api_call():
            return self.api.get_messages()

        def on_result(result):
            data, err = result
            for w in self.content.winfo_children():
                if isinstance(w, ttk.Label) and "Loading" in str(w.cget('text')):
                    w.destroy()

            if err:
                ttk.Label(self.content, text=f"❌ {err}", foreground='#ef4444').pack(pady=20)
                return

            cols = ('ID', 'Name', 'Email', 'Message', 'Read')
            tree = ttk.Treeview(self.content, columns=cols, show='headings', selectmode='browse')
            for col in cols: tree.heading(col, text=col)
            tree.column('ID', width=40)
            tree.column('Message', width=300)
            tree.pack(fill='both', expand=True)

            for msg in data:
                short_msg = msg['message'][:80] + ("..." if len(msg['message']) > 80 else "")
                read_st = "✅ Yes" if msg['is_read'] else "❌ No"
                item = tree.insert('', 'end', values=(msg['id'], msg['name'], msg['email'], short_msg, read_st))
                if not msg['is_read']: tree.item(item, tags=('unread',))
                    
            tree.tag_configure('unread', background='#fef3c7')

            btn_frame = ttk.Frame(self.content)
            btn_frame.pack(fill='x', pady=(15, 0))
            
            def mark_read():
                sel = tree.selection()
                if not sel: return messagebox.showwarning("Warning", "Select a message")
                mid = tree.item(sel[0])['values'][0]
                self._run_async(
                    lambda: self.api.mark_message_read(mid),
                    lambda r: self.show_messages() if not r[1] else messagebox.showerror("Error", r[1])
                )

            ttk.Button(btn_frame, text="✅ Mark as Read", command=mark_read).pack(side='right')

        self._run_async(api_call, on_result)

if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
