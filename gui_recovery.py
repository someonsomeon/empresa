import tkinter as tk
from tkinter import messagebox, simpledialog
from app import email_utils, auth, config
from app.widgets import NeuButton


class ThemedInputDialog(tk.Toplevel):
    """Modal input dialog styled with app theme."""
    def __init__(self, parent, title, prompt, show=None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.resizable(False, False)
        self.configure(bg=config.THEME_BG)
        self.result = None

        # container
        frm = tk.Frame(self, bg=config.THEME_BG, padx=12, pady=12)
        frm.pack(fill='both', expand=True)

        tk.Label(frm, text=prompt, bg=config.THEME_BG, fg=config.THEME_TEXT, font=("Arial", 12)).pack(pady=(0,8))
        # entry with themed border
        self._input_border = tk.Frame(frm, bg=config.THEME_BG, highlightthickness=1, highlightbackground=config.THEME_BORDER)
        self._input_border.pack(fill='x', pady=(0,8))
        self._entry = tk.Entry(self._input_border, show=show or '', bg=config.THEME_BG, fg=config.THEME_MUTED, bd=0, relief='flat', insertbackground=config.THEME_MUTED)
        self._entry.pack(fill='x', padx=6, pady=8)
        self._entry.focus_set()

        btn_frame = tk.Frame(frm, bg=config.THEME_BG)
        btn_frame.pack(fill='x')
        ok = NeuButton(btn_frame, text='Aceptar', command=self._on_ok, height=38, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0)
        ok.pack(side='right', padx=6)
        # Cancel button styled flat to match theme
        cancel = NeuButton(btn_frame, text='Cancelar', command=self._on_cancel, height=38, bg='#cfcfcf', fg=config.THEME_BG, border=0)
        cancel.pack(side='right')

        # center over parent
        try:
            self.update_idletasks()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = px + max(0, (pw - w)//2)
            y = py + max(0, (ph - h)//2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        # Make modal
        self.grab_set()

    def _on_ok(self):
        self.result = self._entry.get()
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def _on_cancel(self):
        self.result = None
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

class RecoveryWindow(tk.Toplevel):
    def __init__(self, parent, email=None):
        super().__init__(parent)
        self.title("Recuperar contraseña")
        # No permitir cambiar tamaño
        self.resizable(False, False)
        self.minsize(320, 140)

        # Apply dark theme
        self.configure(bg=config.THEME_BG)
        container = tk.Frame(self, bg=config.THEME_BG)
        container.pack(fill='both', expand=True, padx=12, pady=12)

        tk.Label(container, text="Correo electrónico:", bg=config.THEME_BG, fg=config.THEME_TEXT, font=("Arial", 12)).pack(padx=10, pady=(10,0))
        # email input frame
        email_frame = tk.Frame(container, bg=config.THEME_BG)
        email_frame.pack(fill='x', padx=10, pady=4)

        # Border frame to match LoginWindow fields
        self.email_border = tk.Frame(email_frame, bg=config.THEME_BG, highlightthickness=1, highlightbackground=config.THEME_BORDER)
        self.email_border.pack(fill='x', expand=True)

        self.email_entry = tk.Entry(self.email_border, font=("Arial", 12), fg=config.THEME_MUTED, bg=config.THEME_BG, bd=0, relief='flat', insertbackground=config.THEME_MUTED)
        self.email_entry.pack(fill='x', padx=6, pady=8, ipady=4)

        # Domain suffix shown inside the entry (as grey overlay text, not a separate box)
        self._domain_text = '@gmail.com'
        self.domain_label = tk.Label(self.email_border, text=self._domain_text, bg=config.THEME_BG, fg=config.THEME_PLACEHOLDER, font=("Arial", 12))
        # Place the domain label overlayed inside the entry area, aligned to the right (inside border)
        self.domain_label.place(relx=1.0, rely=0.5, anchor='e', x=-8)
        # Clicking the suffix focuses the entry
        self.domain_label.bind('<Button-1>', lambda e: self.email_entry.focus_set())
        # Helper to show/hide the domain label depending on entry content
        def _update_domain_label(e=None):
            try:
                txt = self.email_entry.get()
                if getattr(self, '_ph_active', False) or not txt.strip() or '@' in txt:
                    self.domain_label.place_forget()
                else:
                    self.domain_label.config(text=self._domain_text)
                    self.domain_label.place(relx=1.0, rely=0.5, anchor='e', x=-8)
            except Exception:
                pass

        # Placeholder behavior
        self._placeholder = 'email'
        def _show_ph(e=None):
            if not self.email_entry.get():
                try:
                    self.email_entry.insert(0, self._placeholder)
                    self.email_entry.config(fg=config.THEME_PLACEHOLDER)
                    self._ph_active = True
                except Exception:
                    pass
        def _clear_ph(e=None):
            # If placeholder mode was active, clear or normalize it. Don't delete user-typed text.
            if getattr(self, '_ph_active', False):
                if self.email_entry.get() == self._placeholder:
                    try:
                        self.email_entry.delete(0, 'end')
                    except Exception:
                        pass
                self.email_entry.config(fg=config.THEME_MUTED)
                self._ph_active = False
        self.email_entry.bind('<FocusIn>', lambda e: (_clear_ph(e), _update_domain_label(e)))
        self.email_entry.bind('<FocusOut>', lambda e: (_show_ph(e), _update_domain_label(e)))
        # On typing: clear placeholder (if any) and update suffix visibility
        def _on_key(e=None):
            try:
                _clear_ph(e)
            except Exception:
                pass
            try:
                _update_domain_label(e)
            except Exception:
                pass
        self.email_entry.bind('<KeyRelease>', _on_key)
        self._ph_active = False
        _show_ph()
        # Initialize domain label visibility
        _update_domain_label()

        # If initialization provided an email, prefill parts
        if email:
            try:
                if '@' in email:
                    # Full email provided — show full email and hide suffix
                    self.email_entry.delete(0, 'end')
                    self.email_entry.insert(0, email)
                    self.email_entry.config(fg='#333333')
                    self._ph_active = False
                    try:
                        self.domain_label.place_forget()
                    except Exception:
                        pass
                else:
                    # Only local part provided — insert and show suffix
                    self.email_entry.delete(0, 'end')
                    self.email_entry.insert(0, email)
                    self.email_entry.config(fg='#333333')
                    self._ph_active = False
                    _update_domain_label()
            except Exception:
                pass

        # Send button centered and con texto un poco más grande
        self.send_btn = NeuButton(container, text="Enviar código", command=self.on_send, height=44, width=240, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0)
        self.send_btn.pack(padx=10, pady=10)
        self.status = tk.Label(container, text="", bg=config.THEME_BG, fg=config.THEME_MUTED, font=("Arial", 11))
        self.status.pack(padx=10, pady=(2,0))
        self.resend_btn = None
        self.resend_btn = None

        # Center the toplevel over its parent if possible
        try:
            self.update_idletasks()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = px + max(0, (pw - w)//2)
            y = py + max(0, (ph - h)//2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _get_effective_email(self):
        # Return full email string considering placeholder and domain pill
        e = self.email_entry.get().strip()
        if getattr(self, '_ph_active', False) and e == self._placeholder:
            return ''
        if '@' in e:
            return e
        # Combine local part and domain pill
        dom = getattr(self, '_domain_text', '')
        if not dom:
            return e
        # Ensure domain has leading @
        if not dom.startswith('@'):
            dom = '@' + dom
        return e + dom

    def on_send(self):
        # Compute the effective email from local part + domain pill or full entry
        effective_email = self._get_effective_email()
        if not effective_email:
            messagebox.showwarning("Email vacío", "Ingrese un correo electrónico")
            return
        username = auth.get_username_by_email(effective_email)
        if not username:
            messagebox.showerror("No encontrado", "No existe usuario con ese correo")
            return
        # Disable button and show sending status
        self.send_btn.config(state='disabled')
        if not self.status:
            self.status = tk.Label(self, text="Enviando código...")
            self.status.pack(padx=10, pady=6)
        else:
            self.status.config(text="Enviando código...")
        import threading
        def worker():
            try:
                code, sent = email_utils.send_code(effective_email)
                self.after(0, lambda: self._send_done(effective_email, code, sent))
            except Exception as e:
                self.after(0, lambda: self._send_error(e))
        threading.Thread(target=worker, daemon=True).start()

    def _send_done(self, email, code, sent):
        # Re-enable button and show result
        self.send_btn.config(state='normal')
        sent_msg = "(enviado por correo)" if sent else "(impreso en consola - modo desarrollo)"
        if self.status:
            self.status.config(text=f"Código enviado: {code} {sent_msg}")
        if not self.resend_btn:
            self.resend_btn = NeuButton(self, text="Reenviar código", command=lambda: self._resend(email), height=40, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0)
            self.resend_btn.pack(padx=10, pady=4, fill='x')
        messagebox.showinfo(
            "Enviado",
            f"Se ha enviado un código de 5 dígitos desde {email_utils.config.FROM_ADDRESS} con asunto 'Restaurar contraseña' al correo {email}. {sent_msg}",
        )
        # Prompt for code after sending
        # Themed dialog for code entry
        code_dlg = ThemedInputDialog(self, "Código", "Ingrese el código enviado al correo:")
        self.wait_window(code_dlg)
        entered = code_dlg.result
        if not entered:
            return
        if not email_utils.verify_code(email, entered.strip()):
            messagebox.showerror("Código inválido", "El código ingresado no coincide o está caducado")
            return
        # Preguntar si se desea usar el código como contraseña temporal
        use_code = messagebox.askyesno("Usar código", "¿Desea usar el código de 5 dígitos como contraseña temporal?")
        if use_code:
            username = auth.get_username_by_email(email)
            auth.set_password_for_username(username, entered.strip())
            messagebox.showinfo("Listo", "Se ha establecido la contraseña temporal (el código). Por favor inicie sesión y cámbiela.")
            self.destroy()
            return
        # Themed dialog for new password
        pwd_dlg = ThemedInputDialog(self, "Nueva contraseña", "Ingrese nueva contraseña:", show='*')
        self.wait_window(pwd_dlg)
        new_pwd = pwd_dlg.result
        if not new_pwd:
            return
        auth.set_password_for_username(auth.get_username_by_email(email), new_pwd)
        messagebox.showinfo("Listo", "Contraseña cambiada correctamente")
        self.destroy()

    def _send_error(self, exc):
        self.send_btn.config(state='normal')
        if self.status:
            self.status.config(text=f"Error enviando: {exc}", fg='#ffb3b3')
        messagebox.showerror("Error", f"No se pudo enviar el código: {exc}")

    def _resend(self, email):
        # Reuse on_send worker logic for re-send
        if hasattr(self, 'send_btn'):
            self.send_btn.config(state='disabled')
        if not self.status:
            self.status = tk.Label(self, text="Reenviando código...")
            self.status.pack(padx=10, pady=6)
        else:
            self.status.config(text="Reenviando código...")
        import threading
        def worker():
            try:
                code, sent = email_utils.send_code(email)
                self.after(0, lambda: self._send_done(email, code, sent))
            except Exception as e:
                self.after(0, lambda: self._send_error(e))
        threading.Thread(target=worker, daemon=True).start()
