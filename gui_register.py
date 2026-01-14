import tkinter as tk
from tkinter import messagebox
from app.widgets import NeuButton
from app import auth, config

class RegisterWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Registro")
        self.geometry("320x340")
        self.resizable(False, False)
        # Theme
        self.configure(bg=config.THEME_BG)
        try:
            self.eval('tk::PlaceWindow . center')
        except Exception:
            pass

        frame = tk.Frame(self, bg=config.THEME_BG, padx=16, pady=16)
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="Registro", font=("Arial", 14, "bold"), bg=config.THEME_BG, fg=config.THEME_TEXT).grid(row=0, column=0, columnspan=3, pady=(0,12))

        # Campos: Usuario / Correo / Contraseña (vertical, centrados)
        tk.Label(frame, text="Usuario:", bg=config.THEME_BG, fg=config.THEME_TEXT, font=("Arial", 12)).grid(row=1, column=0, sticky='w', pady=(0,6))
        self.username_border = tk.Frame(frame, bg=config.THEME_BG, highlightthickness=1, highlightbackground=config.THEME_BORDER)
        self.username_border.grid(row=2, column=0, sticky='we', pady=(0,10))
        self.username_entry = tk.Entry(self.username_border, width=30, fg=config.THEME_MUTED, bg=config.THEME_BG, bd=0, relief='flat', insertbackground=config.THEME_MUTED)
        self.username_entry.pack(fill='x', padx=6, pady=8)

        tk.Label(frame, text="Correo:", bg=config.THEME_BG, fg=config.THEME_TEXT, font=("Arial", 12)).grid(row=3, column=0, sticky='w', pady=(0,6))
        self.email_border = tk.Frame(frame, bg=config.THEME_BG, highlightthickness=1, highlightbackground=config.THEME_BORDER)
        self.email_border.grid(row=4, column=0, sticky='we', pady=(0,10))
        self.email_entry = tk.Entry(self.email_border, width=30, fg=config.THEME_MUTED, bg=config.THEME_BG, bd=0, relief='flat', insertbackground=config.THEME_MUTED)
        self.email_entry.pack(fill='x', padx=6, pady=8)

        tk.Label(frame, text="Contraseña:", bg=config.THEME_BG, fg=config.THEME_TEXT, font=("Arial", 12)).grid(row=5, column=0, sticky='w', pady=(0,6))
        self.pwd_border = tk.Frame(frame, bg=config.THEME_BG, highlightthickness=1, highlightbackground=config.THEME_BORDER)
        self.pwd_border.grid(row=6, column=0, sticky='we')
        self.pwd_entry = tk.Entry(self.pwd_border, show='*', width=30, fg=config.THEME_MUTED, bg=config.THEME_BG, bd=0, relief='flat', insertbackground=config.THEME_MUTED)
        self.pwd_entry.pack(fill='x', padx=6, pady=8)

        # Aceptar button centered
        save_btn = NeuButton(frame, text="Aceptar", command=self.on_save, height=44, width=220, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0)
        save_btn.grid(row=7, column=0, pady=(14,6))

        # Make flexible space below
        frame.grid_rowconfigure(8, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def on_save(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        pwd = self.pwd_entry.get()
        if not username or not email or not pwd:
            messagebox.showwarning('Campos vacíos', 'Complete todos los campos')
            return
        try:
            auth.add_user(username, pwd, email)
            messagebox.showinfo('Registro', 'Usuario registrado correctamente')
            self.destroy()
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo registrar: {e}')
