import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from app import excel_db
from app import config
from app.widgets import NeuButton
import os
import time

class RecordDialog(tk.Toplevel):
    def __init__(self, parent, title="Registro", data=None):
        super().__init__(parent)
        self.title(title)
        # Permitimos redimensionar y que los campos se adapten
        self.resizable(True, True)
        self.result = None
        # Apply theme
        self.configure(bg=config.THEME_BG)

        self.entries = {}
        for i, h in enumerate(excel_db.HEADERS):
            tk.Label(self, text=h+":", bg=config.THEME_BG, fg=config.THEME_TEXT).grid(row=i, column=0, sticky=tk.W, padx=8, pady=6)
            border = tk.Frame(self, bg=config.THEME_BG, highlightthickness=1, highlightbackground=config.THEME_BORDER)
            border.grid(row=i, column=1, padx=8, pady=6, sticky='we')
            e = tk.Entry(border, bg=config.THEME_BG, fg=config.THEME_MUTED, bd=0, relief='flat', insertbackground=config.THEME_MUTED)
            e.pack(fill='x', padx=6, pady=6)
            self.entries[h] = e
        # Make columns expandable
        self.grid_columnconfigure(1, weight=1)


        if data:
            for i, h in enumerate(excel_db.HEADERS):
                self.entries[h].insert(0, str(data[i] if data[i] is not None else ""))

        btn_frame = tk.Frame(self, bg=config.THEME_BG)
        btn_frame.grid(row=len(excel_db.HEADERS), column=0, columnspan=2, pady=8)
        NeuButton(btn_frame, text="Guardar", command=self.on_ok, height=36, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0).pack(side=tk.LEFT, padx=6)
        NeuButton(btn_frame, text="Cancelar", command=self.destroy, height=36, bg='#cfcfcf', fg=config.THEME_BG, border=0).pack(side=tk.LEFT, padx=6)

    def on_ok(self):
        # Validaciones simples
        nombre = self.entries["Nombre"].get().strip()
        salario = self.entries["Salario"].get().strip()
        if not nombre:
            messagebox.showwarning("Validación", "El campo Nombre es obligatorio.")
            return
        if salario:
            try:
                float(salario)
            except ValueError:
                messagebox.showwarning("Validación", "Salario debe ser numérico.")
                return
        self.result = {h: self.entries[h].get().strip() for h in excel_db.HEADERS}
        self.destroy()

class MainApp(tk.Tk):
    POLL_INTERVAL = 2000  # ms

    def __init__(self, username):
        super().__init__()
        self.title(f"Panel - Usuario: {username}")
        self.geometry("900x500")
        self.minsize(640, 400)
        self.resizable(True, True)
        # Apply theme
        self.configure(bg=config.THEME_BG)

        top_frame = tk.Frame(self, bg=config.THEME_BG)
        top_frame.pack(padx=10, pady=10, fill=tk.X)

        NeuButton(top_frame, text="Agregar", command=self.on_add, height=40, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0).pack(side=tk.LEFT, padx=4)
        NeuButton(top_frame, text="Editar", command=self.on_edit, height=40, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0).pack(side=tk.LEFT, padx=4)
        NeuButton(top_frame, text="Refrescar", command=self.refresh, height=40, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0).pack(side=tk.LEFT, padx=8)
        NeuButton(top_frame, text="Exportar CSV", command=self.export_csv, height=40, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0).pack(side=tk.LEFT, padx=8)

        self._search_var = tk.StringVar()
        self._filter_query = ''
        NeuButton(top_frame, text="Salir", command=self.quit, height=40, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0).pack(side=tk.RIGHT, padx=4)

        # Search row: placed under the top buttons, full width above the cards
        search_row = tk.Frame(self, bg=config.THEME_BG)
        search_row.pack(fill=tk.X, padx=10, pady=(0,8))
        # Larger search entry font and padding for readability
        search_entry = tk.Entry(search_row, textvariable=self._search_var, bg=config.THEME_PANEL, fg=config.THEME_TEXT, bd=0, relief='flat', insertbackground=config.THEME_MUTED, font=("Arial", 12))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6), ipady=8)
        search_entry.bind('<KeyRelease>', self._on_search_change)
        # Larger magnifier icon button in accent color
        NeuButton(search_row, text='🔍', width=48, height=40, font=("Arial", 14), command=self._on_search_change, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0).pack(side=tk.RIGHT)

        # Records area: scrollable list of cards
        self._cards_container = tk.Frame(self, bg=config.THEME_BG)
        self._cards_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,6))

        # Canvas + scrollbar for cards
        self._cards_canvas = tk.Canvas(self._cards_container, bg=config.THEME_BG, highlightthickness=0)
        self._cards_scroll = tk.Scrollbar(self._cards_container, orient='vertical', command=self._cards_canvas.yview)
        self._cards_frame = tk.Frame(self._cards_canvas, bg=config.THEME_BG)
        self._cards_frame.bind('<Configure>', lambda e: self._cards_canvas.configure(scrollregion=self._cards_canvas.bbox('all')))
        # Create window and keep reference so we can keep inner frame width synced with canvas.
        self._cards_frame_id = self._cards_canvas.create_window((0,0), window=self._cards_frame, anchor='nw')
        # Make inner frame width follow canvas width so cards expand vertically and wrap text instead of compressing horizontally.
        self._cards_canvas.bind('<Configure>', self._on_canvas_config)
        self._cards_canvas.configure(yscrollcommand=self._cards_scroll.set)
        self._cards_canvas.pack(side='left', fill='both', expand=True)
        self._cards_scroll.pack(side='right', fill='y')
        # Keep track of value labels for wrap updates
        self._card_value_labels = []

        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("")
        tk.Label(self, textvariable=self.status_var, anchor=tk.W, bg=config.THEME_BG, fg=config.THEME_MUTED).pack(fill=tk.X, padx=10, pady=(0,8))

        # Build initial cards
        self._build_cards()

        # Estado de archivo
        self._last_mtime = None
        self.refresh()
        self.after(self.POLL_INTERVAL, self._poll_file)

        # Bottom frame with Logout button centered below the table
        bottom_frame = tk.Frame(self, bg=config.THEME_BG)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        NeuButton(bottom_frame, text="Cerrar sesión", command=self.on_logout, height=40, bg=config.THEME_ACCENT, fg=config.THEME_BG, border=0).pack(pady=6)


    def export_csv(self):
        import csv
        rows = excel_db.read_all()
        try:
            csv_path = os.path.splitext(config.DATA_EXCEL)[0] + ".csv"
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(excel_db.HEADERS)
                for row in rows:
                    w.writerow([("" if v is None else v) for v in row])
            messagebox.showinfo("Exportar CSV", f"Exportado a {csv_path}")
            self.status_var.set(f"Exportado: {csv_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar CSV: {e}")

    def refresh(self):
        # Rebuild cards from Excel
        self._build_cards()
        # actualizar estado
        try:
            self._last_mtime = os.path.getmtime(config.DATA_EXCEL)
            self.status_var.set(f"Última sincronización: {time.ctime(self._last_mtime)}")
        except Exception:
            self.status_var.set("Archivo de datos no disponible")

    def _build_cards(self):
        # Reset value label registry and clear existing
        self._card_value_labels = []
        for w in self._cards_frame.winfo_children():
            w.destroy()
        rows_all = excel_db.read_all()
        if not rows_all:
            tk.Label(self._cards_frame, text="No hay registros.", bg=config.THEME_BG, fg=config.THEME_MUTED).pack(padx=8, pady=8)
            return
        # Enumerate with original indices so delete operations map to correct rows
        rows_enum = list(enumerate(rows_all))
        q = getattr(self, '_filter_query', '').lower()
        if q:
            rows_enum = [ (i,row) for i,row in rows_enum if any(q in ('' if v is None else str(v)).lower() for v in row) ]
        if not rows_enum:
            # Mostrar mensaje centrado cuando no hay coincidencias de búsqueda
            lbl = tk.Label(self._cards_frame, text="No se encontraron resultados", bg=config.THEME_BG, fg=config.THEME_MUTED, font=("Arial", 12), anchor='center', justify='center')
            lbl.pack(fill='both', expand=True, padx=8, pady=8)
            return
        for orig_i, row in rows_enum:
            self._make_card(orig_i, row)

    def _make_card(self, index, row_data):
        # Create a card frame for a record
        # Make card a squarish box with a stronger border and more vertical padding
        card = tk.Frame(self._cards_frame, bg=config.THEME_PANEL, bd=0, relief='flat', highlightthickness=1, highlightbackground=config.THEME_BORDER)
        card.pack(fill='x', pady=10, padx=6, ipady=12)
        # Right: Delete button (red)
        # Square delete button: use a compact symbol and make width == height
        _del_size = 48
        del_btn = NeuButton(card, text='✖', width=_del_size, height=_del_size, font=("Arial", 14), command=lambda i=index: self.on_delete_card(i), bg='#ff6b6b', fg=config.THEME_BG, border=0)
        del_btn.pack(side='right', padx=8, pady=6, anchor='n')
        # Center: info grid (four columns: Nombre | Cédula | Cargo | Salario)
        info = tk.Frame(card, bg=config.THEME_PANEL)
        info.pack(fill='both', expand=True, padx=6, pady=6)
        # Four equal-width columns for horizontal layout
        info.grid_columnconfigure(0, weight=1)
        info.grid_columnconfigure(1, weight=1)
        info.grid_columnconfigure(2, weight=1)
        info.grid_columnconfigure(3, weight=1)
        # Place each field as a column: title above the value
        # Fonts for titles and values (larger values for readability)
        title_font = ("Arial", 10, "bold")
        value_font = ("Arial", 13)
        for idx, (h, v) in enumerate(zip(excel_db.HEADERS, row_data)):
            col = idx  # 0..3
            title = tk.Label(info, text=f"{h}", bg=config.THEME_PANEL, fg=config.THEME_MUTED, anchor='w', font=title_font)
            title.grid(row=0, column=col, sticky='w', padx=6, pady=(0,6))
            wrap = max(100, int((self._cards_canvas.winfo_width() - 240) / 4))
            value = tk.Label(info, text=f"{'' if v is None else v}", bg=config.THEME_PANEL, fg=config.THEME_TEXT, anchor='w', justify='left', wraplength=wrap, font=value_font)
            value.grid(row=1, column=col, sticky='w', padx=6)
            # Keep track of value labels for wrap updates
            self._card_value_labels.append(value)

    def on_delete_card(self, index):
        if not messagebox.askyesno('Eliminar', '¿Desea eliminar el registro seleccionado?'):
            return
        excel_db.delete_record(index)
        self.refresh()

    def on_edit_card(self, index):
        rows = excel_db.read_all()
        if index < 0 or index >= len(rows):
            messagebox.showwarning('Editar', 'Registro no encontrado')
            return
        data = rows[index]
        dlg = RecordDialog(self, title='Editar empleado', data=data)
        self.wait_window(dlg)
        if dlg.result:
            excel_db.update_record(index, dlg.result)
            self.refresh()

    def on_add(self):
        dlg = RecordDialog(self, title="Agregar empleado")
        self.wait_window(dlg)
        if dlg.result:
            excel_db.add_record(dlg.result)
            self.refresh()

    def on_edit(self):
        messagebox.showinfo("Editar", "La edición por tarjeta fue removida; use las opciones de la barra superior para gestionar registros.")

    def on_delete(self):
        messagebox.showinfo("Eliminar", "Use el botón 'Eliminar' dentro de la tarjeta correspondiente para borrar un registro.")

    def _poll_file(self):
        try:
            m = os.path.getmtime(config.DATA_EXCEL)
            if self._last_mtime is None or m != self._last_mtime:
                # archivo cambiado externamente
                self.refresh()
        except Exception:
            pass
        self.after(self.POLL_INTERVAL, self._poll_file)

    def _on_canvas_config(self, e):
        # Keep inner frame width synced with canvas and update wraplengths of value labels
        try:
            self._cards_canvas.itemconfig(self._cards_frame_id, width=e.width)
        except Exception:
            pass
        for lbl in getattr(self, '_card_value_labels', []):
            try:
                # Now cards have 4 columns, compute wrap per column
                lbl.config(wraplength=max(100, int((e.width - 260) / 4)))
            except Exception:
                pass

    def _on_search_change(self, event=None):
        # Update filter query and refresh cards
        try:
            q = self._search_var.get().strip().lower()
            self._filter_query = q
        except Exception:
            self._filter_query = ''
        self.refresh()

    def on_logout(self):
        # Confirm logout
        if not messagebox.askyesno("Cerrar sesión", "¿Desea cerrar sesión?"):
            return
        # Destroy current main window
        try:
            self.destroy()
        except Exception:
            pass
        # Open a fresh LoginWindow (fields will be empty)
        try:
            # Import here to avoid circular imports at module load
            from app.gui_login import LoginWindow
            win = LoginWindow()
            win.mainloop()
        except Exception as e:
            print("Error al abrir la ventana de login después de cerrar sesión:", e)
