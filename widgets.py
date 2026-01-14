import tkinter as tk

class NeuButton(tk.Canvas):
    """A simple rounded-corner button implemented on a Canvas.

    This version is intentionally minimal: flat background, rounded corners,
    visible border, hover/pressed feedback, and larger font (approx. 18px).
    """

    def __init__(self, master, text="Button", command=None, width=None, height=56,
                 bg="#d0d0d0", fg="#4d4d4d", radius=10, font=None, padding_x=40,
                 border=2, **kwargs):
        self.text = text
        self.command = command
        self.bg = bg
        self.fg = fg
        self.radius = radius
        self.border = border
        # larger font to match requested CSS (font-size:18px)
        self.font = font or ("Arial", 18)
        if width is None:
            width = max(120, len(text) * 12 + padding_x)
        super().__init__(master, width=width, height=height, bg=master.cget('bg'), highlightthickness=0, bd=0, **kwargs)
        self._pressed = False
        self._hover = False
        self.configure(cursor='hand2')
        self.bind("<Enter>", lambda e: self._on_enter())
        self.bind("<Leave>", lambda e: self._on_leave())
        self.bind("<ButtonPress-1>", lambda e: self._on_press())
        self.bind("<ButtonRelease-1>", lambda e: self._on_release())
        # keyboard
        self.bind('<space>', lambda e: self._on_press(keyboard=True))
        self.bind('<KeyRelease-space>', lambda e: self._on_release(keyboard=True))
        self.bind('<Return>', lambda e: self._on_release(keyboard=True))
        # focus visuals
        self.bind('<FocusIn>', lambda e: self._on_enter())
        self.bind('<FocusOut>', lambda e: self._on_leave())
        self._draw()

    def _draw(self):
        self.delete('all')
        w = int(self['width'])
        h = int(self['height'])
        r = self.radius
        fill_color = self.bg
        outline_color = None
        outline_width = self.border
        if self._pressed:
            # slightly darker fill when pressed
            fill_color = '#d9d9d9'
        elif self._hover and self.border > 0:
            # subtle highlight on hover
            outline_color = '#bdbdbd'
        # No outline if border is 0 (flat button)
        if self.border == 0:
            outline_color = ''
            outline_width = 0
        # draw rounded rectangle (fill + border)
        self.create_round_rect(0, 0, w, h, r, fill=fill_color, outline=outline_color, width=outline_width)
        # draw text
        self.create_text(w//2, h//2, text=self.text, fill=self.fg, font=self.font, tags='label')

    def create_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        # Draw using arcs and rectangles to ensure crisp rounded corners
        # corners: use create_arc for each corner then rectangles
        items = []
        # center rectangle
        items.append(self.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs))
        items.append(self.create_rectangle(x1, y1 + r, x2, y2 - r, **kwargs))
        # corners (arcs)
        items.append(self.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90, extent=90, style='pieslice', **kwargs))
        items.append(self.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=0, extent=90, style='pieslice', **kwargs))
        items.append(self.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=270, extent=90, style='pieslice', **kwargs))
        items.append(self.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=180, extent=90, style='pieslice', **kwargs))
        return items

    def _on_enter(self):
        self._hover = True
        self._draw()

    def _on_leave(self):
        self._hover = False
        self._pressed = False
        self._draw()

    def _on_press(self, keyboard=False):
        self._pressed = True
        self._draw()

    def _on_release(self, keyboard=False):
        if self._pressed:
            self._pressed = False
            self._draw()
            if self.command:
                try:
                    self.command()
                except Exception:
                    raise

    def config(self, **kwargs):
        if 'text' in kwargs:
            self.text = kwargs.pop('text')
        if 'command' in kwargs:
            self.command = kwargs.pop('command')
        super().config(**kwargs)

    def set_state(self, state):
        if state == 'disabled':
            self.unbind("<ButtonPress-1>")
            self.configure(cursor='arrow')
        else:
            # no-op
            pass
