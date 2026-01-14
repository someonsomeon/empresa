import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import font as tkfont
from app import auth
from app.gui_recovery import RecoveryWindow
from app.gui_main import MainApp
from app.widgets import NeuButton
from app.gui_register import RegisterWindow

class LoginWindow(tk.Tk):
    """Ventana de login mínima y nativa (Tkinter por defecto)."""
    def __init__(self):
        super().__init__()
        self.title("Login")
        # Tamaño solicitado por el usuario: ancho x alto (px)
        self.geometry("300x500")
        self.minsize(280, 420)
        self.resizable(False, False)
        # Dark theme
        self.configure(bg='#2b2b33')
        try:
            self.eval('tk::PlaceWindow . center')
        except Exception:
            pass

        frame = tk.Frame(self, padx=20, pady=20, bg='#2b2b33')
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="Inicio de sesión", font=("Arial", 18, "bold"), bg='#2b2b33', fg='#f5f5f5').grid(row=0, column=0, columnspan=3, pady=(0,20))

        tk.Label(frame, text="Usuario:", bg='#2b2b33', fg='#dcdcdc', font=("Arial", 12)).grid(row=1, column=1, pady=(0,6))
        # Thin gray border by default (same thickness as error border)
        self.user_border = tk.Frame(frame, bg='#2b2b33', highlightthickness=1, highlightbackground='#3a3a43')
        self.user_border.grid(row=2, column=0, columnspan=3, sticky='we', pady=(0,10))
        # Entry with left email icon (no circle)
        self.user_icon = tk.Label(self.user_border, text='✉', bg=self.user_border.cget('bg'), fg='#F8E3A9', font=("Arial", 16))
        self.user_icon.pack(side='left', padx=(8,6), pady=8)
        self.user_entry = tk.Entry(self.user_border, width=30, fg='#dcdcdc', bg=self.user_border.cget('bg'), bd=0, relief='flat', highlightthickness=0, insertbackground='#dcdcdc')
        self.user_entry.pack(side='left', fill='x', expand=True, padx=(0,6), pady=8) 

        tk.Label(frame, text="Contraseña:", bg='#2b2b33', fg='#dcdcdc', font=("Arial", 12)).grid(row=3, column=1, pady=(0,6))
        # Thin gray border by default (same thickness as error border)
        self.pw_border = tk.Frame(frame, bg='#2b2b33', highlightthickness=1, highlightbackground='#3a3a43')
        self.pw_border.grid(row=4, column=0, columnspan=3, sticky='we')
        # Lock icon + transparent entry + eye canvas
        # Eye icon on the left (no circle) and transparent-looking entry
        self.eye_canvas = tk.Canvas(self.pw_border, width=40, height=40, bg=self.pw_border.cget('bg'), highlightthickness=0, cursor='hand2')
        self.eye_canvas.pack(side='left', padx=(8,8), pady=6)
        self.eye_canvas.bind('<Button-1>', lambda e: self.toggle_show())
        self.pw_entry = tk.Entry(self.pw_border, show='*', width=30, fg='#dcdcdc', bg=self.pw_border.cget('bg'), bd=0, relief='flat', highlightthickness=0, insertbackground='#dcdcdc')
        self.pw_entry.pack(side='left', fill='x', expand=True, padx=(0,6), pady=8)
        # Initial eye draw (hidden)
        try:
            # ensure eye canvas exists and draw without circular background
            self._draw_eye(False)
        except Exception:
            pass

        # Clear error visuals when user focuses the entries
        self.user_entry.bind('<FocusIn>', lambda e: self._clear_error('user'))
        self.pw_entry.bind('<FocusIn>', lambda e: self._clear_error('pw'))

        # Make columns 0 and 2 flexible so column 1 stays centered
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=1)

        # Botones centrados (columna 1)
        login_btn = NeuButton(frame, text="Iniciar sesión", command=self.on_login, height=48, bg='#F8E3A9', fg=self.cget('bg'), border=0)
        login_btn.grid(row=6, column=1, pady=(18,14))

        register_btn = NeuButton(frame, text="Regístrate", command=self.on_signup, height=44, bg='#F8E3A9', fg=self.cget('bg'), border=0)
        register_btn.grid(row=7, column=1, pady=(6,10))

        # Etiqueta clicable para recuperar contraseña (centrada al final) — estilo link claro
        self.recovery_label = tk.Label(frame, text="¿Olvidaste tu correo? Recuperar aquí", fg='#bcd1ff', bg='#2b2b33', cursor='hand2', font=("Arial", 11, 'underline'))
        self.recovery_label.grid(row=9, column=1, pady=(18,8))
        self.recovery_label.bind('<Button-1>', lambda e: self._open_recovery_with_email())

        # Espacio flexible debajo
        frame.grid_rowconfigure(10, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        self.bind('<Return>', lambda e: self.on_login())

    def on_signup(self):
        # Abrir la ventana de registro completa
        try:
            RegisterWindow(self)
        except Exception as exc:
            messagebox.showerror("Registro", f"No se pudo abrir la ventana de registro: {exc}")

    def _open_recovery_with_email(self):
        # Obtener el texto actual del campo de usuario y pasarlo como email a RecoveryWindow
        candidate = self.user_entry.get().strip()
        # Si el texto parece un email (contiene '@'), lo usamos; si no, lo pasamos tal cual (pueden querer escribir el correo)
        RecoveryWindow(self, email=candidate)

    def toggle_show(self):
        # Toggle visibility and update eye canvas
        try:
            if self.pw_entry.cget('show') == '':
                self.pw_entry.config(show='*')
                self._draw_eye(False)
            else:
                self.pw_entry.config(show='')
                self._draw_eye(True)
        except Exception:
            pass

    def _draw_eye(self, visible):
        try:
            if not hasattr(self, 'eye_canvas'):
                return
            c = self.eye_canvas
            w = int(c['width'])
            c.delete('all')
            txt = '🙈' if visible else '👁'
            # Draw only the eye glyph colored like the button (no circular background)
            font_size = max(14, int(w * 0.45))
            c.create_text(w//2, w//2, text=txt, fill='#F8E3A9', font=("Arial", font_size, 'bold'))
        except Exception:
            pass

    def on_login(self):
        u = self.user_entry.get().strip()
        p = self.pw_entry.get()
        if not u or not p:
            messagebox.showwarning('Campos vacíos', 'Ingrese usuario y contraseña')
            # indicate error on both fields
            self._indicate_error(['user','pw'])
            return
        if auth.authenticate(u, p):
            messagebox.showinfo('Bienvenido', f'Bienvenido {u}')
            self.destroy()
            app = MainApp(u)
            app.mainloop()
        else:
            # visual feedback: red borders and shake
            self._indicate_error(['user','pw'])
            messagebox.showerror('Error', 'Usuario o contraseña incorrectos')

    def _clear_error(self, which):
        # Reset border for the given field to thin gray appropriate for dark theme
        if which == 'user' and hasattr(self, 'user_border'):
            self.user_border.config(highlightthickness=1, highlightbackground='#3a3a43')
        if which == 'pw' and hasattr(self, 'pw_border'):
            self.pw_border.config(highlightthickness=1, highlightbackground='#3a3a43')

    def _indicate_error(self, fields):
        # Set thin highlight border to red
        if 'user' in fields and hasattr(self, 'user_border'):
            self.user_border.config(highlightthickness=1, highlightbackground='#ff6b6b')
        if 'pw' in fields and hasattr(self, 'pw_border'):
            self.pw_border.config(highlightthickness=1, highlightbackground='#ff6b6b')
        # shake the entry widgets (not the whole window)
        self._shake_fields(fields)
        # after 1.2s restore borders
        self.after(1200, lambda: [self._clear_error(f) for f in fields])

    def _shake_fields(self, fields, magnitude=6, cycles=8, delay=30):
        try:
            # Adjust grid padding to simulate shake
            orig_user_padx = None
            orig_pw_padx = None
            if hasattr(self, 'user_border'):
                info = self.user_border.grid_info()
                orig_user_padx = info.get('padx', 0)
            if hasattr(self, 'pw_border'):
                info = self.pw_border.grid_info()
                orig_pw_padx = info.get('padx', 0)
            for i in range(cycles):
                offset = magnitude if i % 2 == 0 else -magnitude
                if 'user' in fields and hasattr(self, 'user_border'):
                    self.user_border.grid_configure(padx=offset)
                if 'pw' in fields and hasattr(self, 'pw_border'):
                    self.pw_border.grid_configure(padx=offset)
                self.update()
                self.after(delay)
            # restore
            if hasattr(self, 'user_border'):
                self.user_border.grid_configure(padx=orig_user_padx or 0)
            if hasattr(self, 'pw_border'):
                self.pw_border.grid_configure(padx=orig_pw_padx or 0)
            self.update()
        except Exception:
            pass

    def on_lost(self):
        RecoveryWindow(self)
