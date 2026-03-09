import tkinter as tk
from tkinter import ttk
import re

LIMIT = 4000

def split_into_cards(text, limit=LIMIT):
    lines = text.splitlines(keepends=True)
    cards = []
    current = ""
    for line in lines:
        if len(current) + len(line) <= limit:
            current += line
        else:
            if current:
                cards.append(current)
                current = ""
            if len(line) <= limit:
                current += line
            else:
                i = 0
                while i < len(line):
                    remaining = limit - len(current)
                    if remaining == 0:
                        cards.append(current)
                        current = ""
                        remaining = limit
                    take = min(remaining, len(line) - i)
                    current += line[i:i+take]
                    i += take
                    if len(current) == limit:
                        cards.append(current)
                        current = ""
    if current:
        cards.append(current)
    return cards

def detect_language(text):
    head = text.lstrip()[:200].lower()
    if head.startswith('#!') and ('python' in head or 'python3' in head):
        return 'python'
    if re.search(r'\b(import|def|class|print|from)\b', head):
        return 'python'
    if '<html' in head or head.strip().startswith('<!doctype'):
        return 'html'
    if re.search(r'\b(function|console\.log|var|let|const)\b', head):
        return 'javascript'
    return 'plain'

class CardSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PiPaste 4000")
        self.cards = []
        self.index = 0
        self._after_id = None
        self.bg = "#121212"
        self.panel = "#1e1e1e"
        self.input_bg = "#151515"
        self.text_fg = "#e6e6e6"
        self.btn_bg = "#2a2a2a"
        self.btn_active = "#3a7bd5"
        self.font_mono = ("Consolas", 11)
        self.placeholder_text = "Paste your code here"
        self.input_placeholder = False
        self.setup_style()
        self.setup_ui()
        self.root.after(0, self.center_window)

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background=self.bg)
        style.configure("TLabel", background=self.bg, foreground=self.text_fg)
        style.configure("Card.TLabel", background=self.panel, foreground=self.text_fg, font=("Segoe UI", 10, "bold"))
        style.configure("Count.TLabel", background=self.bg, foreground="#bfbfbf", font=("Segoe UI", 9))
        style.configure("Nav.TButton", background=self.btn_bg, foreground=self.text_fg, font=("Segoe UI", 12), padding=6)
        style.map("Nav.TButton", background=[("active", self.btn_active)])
        style.configure("Dark.Vertical.TScrollbar", troughcolor=self.panel, background=self.btn_bg, arrowcolor=self.text_fg)
        style.configure("Dark.Horizontal.TScrollbar", troughcolor=self.panel, background=self.btn_bg, arrowcolor=self.text_fg)
        self.root.configure(bg=self.bg)

    def make_text_with_scrolls(self, parent, bg, fg, font, wrap="none", height=20):
        container = ttk.Frame(parent, style="TFrame")
        txt = tk.Text(container, bg=bg, fg=fg, insertbackground=fg, wrap=wrap, font=font, relief="flat", bd=0, padx=6, pady=6)
        vcmd = ttk.Scrollbar(container, orient="vertical", command=txt.yview, style="Dark.Vertical.TScrollbar")
        hcmd = ttk.Scrollbar(container, orient="horizontal", command=txt.xview, style="Dark.Horizontal.TScrollbar")
        txt.configure(yscrollcommand=vcmd.set, xscrollcommand=hcmd.set)
        txt.grid(row=0, column=0, sticky="nsew")
        vcmd.grid(row=0, column=1, sticky="ns")
        hcmd.grid(row=1, column=0, sticky="ew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        return container, txt, vcmd, hcmd

    def setup_ui(self):
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill="both", expand=True, padx=12, pady=12)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        ui_frame = ttk.Frame(main, style="TFrame")
        ui_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        card_frame = ttk.Frame(main, style="TFrame")
        card_frame.grid(row=0, column=1, sticky="nsew")
        ui_frame.rowconfigure(1, weight=1)
        top_label = ttk.Label(ui_frame, text="Input code / text", style="Card.TLabel")
        top_label.grid(row=0, column=0, sticky="ew", pady=(0,8))
        input_container, self.input_text, iv, ih = self.make_text_with_scrolls(ui_frame, bg=self.input_bg, fg=self.text_fg, font=self.font_mono, height=25)
        input_container.grid(row=1, column=0, sticky="nsew")
        self.input_text.tag_configure("ph", foreground="#6f6f6f")
        self.input_text.insert("1.0", self.placeholder_text)
        self.input_text.tag_add("ph", "1.0", "end")
        self.input_placeholder = True
        self.input_text.bind("<FocusIn>", self._input_focus_in)
        self.input_text.bind("<FocusOut>", self._input_focus_out)
        self.input_text.bind("<KeyRelease>", self._on_input_change)
        self.input_text.bind("<<Paste>>", self._on_input_change)
        self.input_text.bind("<Control-v>", self._on_input_change)
        self.input_text.bind("<Button-2>", self._on_input_change)
        self.input_text.bind("<Button-3>", self._on_input_change)
        btns_frame = ttk.Frame(ui_frame, style="TFrame")
        btns_frame.grid(row=2, column=0, sticky="ew", pady=(10,0))
        btns_frame.columnconfigure(0, weight=1)
        btns_frame.columnconfigure(1, weight=0)
        left_col = ttk.Frame(btns_frame, style="TFrame")
        left_col.grid(row=0, column=0, sticky="w")
        clear_btn = ttk.Button(left_col, text="Clear Input", command=self.clear_input, style="Nav.TButton")
        clear_btn.grid(row=0, column=0, sticky="w", padx=(0,6))
        paste_btn = ttk.Button(left_col, text="Paste", command=self.paste_input, style="Nav.TButton")
        paste_btn.grid(row=0, column=1, sticky="w")
        nav_col = ttk.Frame(btns_frame, style="TFrame")
        nav_col.grid(row=0, column=1, sticky="e", padx=(6,0))
        nav_col.columnconfigure(0, weight=0)
        nav_col.columnconfigure(1, weight=0)
        first_btn = ttk.Button(nav_col, text="1st Card 📍", command=self.first_card, width=12, style="Nav.TButton")
        first_btn.grid(row=0, column=0, padx=(0,6))
        next_btn = ttk.Button(nav_col, text="Next Card ➤", command=self.next_card, width=12, style="Nav.TButton")
        next_btn.grid(row=0, column=1)
        info_frame = ttk.Frame(ui_frame, style="TFrame")
        info_frame.grid(row=3, column=0, sticky="ew", pady=(10,0))
        self.input_count_label = ttk.Label(info_frame, text="Input chars: 0", style="Count.TLabel")
        self.input_count_label.grid(row=0, column=0, sticky="w")
        self.cards_count_label = ttk.Label(info_frame, text="Cards: 0", style="Count.TLabel")
        self.cards_count_label.grid(row=1, column=0, sticky="w")
        self.card_lengths_label = ttk.Label(info_frame, text="Card lengths: []", style="Count.TLabel")
        self.card_lengths_label.grid(row=2, column=0, sticky="w")
        self.alert_label = ttk.Label(info_frame, text="", style="Count.TLabel")
        self.alert_label.grid(row=3, column=0, sticky="w", pady=(6,0))
        card_frame.rowconfigure(1, weight=1)
        self.card_label = ttk.Label(card_frame, text="Card 0 / 0", style="Card.TLabel")
        self.card_label.grid(row=0, column=0, sticky="w")
        card_container, self.card_text, cv, ch = self.make_text_with_scrolls(card_frame, bg=self.panel, fg=self.text_fg, font=self.font_mono, height=25)
        card_container.grid(row=1, column=0, sticky="nsew")
        self.card_text.configure(state="normal")
        self.card_text.delete("1.0", "end")
        self.card_text.insert("1.0", "No code provided")
        self.card_text.tag_configure("nocode", foreground="#6f6f6f")
        self.card_text.tag_add("nocode", "1.0", "end")
        self.card_text.configure(state="disabled")
        self.configure_syntax_tags()
        self.root.bind("<Up>", lambda e: self.prev_card())
        self.root.bind("<Down>", lambda e: self.next_card())

    def _input_focus_in(self, event=None):
        if self.input_placeholder:
            try:
                self.input_text.delete("1.0", "end")
            except Exception:
                pass
            self.input_text.tag_remove("ph", "1.0", "end")
            self.input_placeholder = False

    def _input_focus_out(self, event=None):
        content = self.input_text.get("1.0", "end-1c")
        if not content:
            self.input_text.insert("1.0", self.placeholder_text)
            self.input_text.tag_add("ph", "1.0", "end")
            self.input_placeholder = True

    def configure_syntax_tags(self):
        self.card_text.tag_configure("keyword", foreground="#61afef")
        self.card_text.tag_configure("string", foreground="#98c379")
        self.card_text.tag_configure("comment", foreground="#5c6370")
        self.card_text.tag_configure("number", foreground="#d19a66")
        self.card_text.tag_configure("builtin", foreground="#c678dd")
        self.card_text.tag_configure("tag", foreground="#e06c75")
        self.card_text.tag_configure("attr", foreground="#e5c07b")

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        if w <= 1 or h <= 1:
            w = max(900, self.root.winfo_reqwidth())
            h = max(600, self.root.winfo_reqheight())
            self.root.geometry(f"{w}x{h}")
            self.root.update_idletasks()
            w = self.root.winfo_width()
            h = self.root.winfo_height()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def clear_input(self):
        if self._after_id:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        try:
            self.root.clipboard_clear()
            self.root.update()
        except Exception:
            pass
        try:
            self.input_text.delete("1.0", "end")
        except Exception:
            pass
        try:
            self.input_text.insert("1.0", self.placeholder_text)
            self.input_text.tag_add("ph", "1.0", "end")
            self.input_placeholder = True
        except Exception:
            self.input_placeholder = True
        self.cards = []
        self.index = 0
        self.update_display()
        self.update_counts()
        self.show_alert("Cleared input and clipboard", "#bfbfbf")

    def paste_input(self):
        try:
            txt = self.root.clipboard_get()
        except Exception:
            txt = ""
        if txt:
            if self.input_placeholder:
                try:
                    self.input_text.delete("1.0", "end")
                except Exception:
                    pass
                try:
                    self.input_text.tag_remove("ph", "1.0", "end")
                except Exception:
                    pass
                self.input_placeholder = False
            try:
                self.input_text.insert("insert", txt)
            except Exception:
                try:
                    self.input_text.insert("1.0", txt)
                except Exception:
                    pass
            self._on_input_change()
            self.show_alert("Pasted from clipboard", "#bfbfbf")
        else:
            self.show_alert("Clipboard empty", "#f0a070")

    def _on_input_change(self, event=None):
        if self.input_placeholder:
            return
        if self._after_id:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = self.root.after(350, self._auto_process)

    def _auto_process(self):
        self._after_id = None
        text = self.input_text.get("1.0", "end-1c")
        if self.input_placeholder:
            self.input_count_label.config(text="Input chars: 0")
            self.cards = []
            self.index = 0
            self.update_display()
            self.update_counts()
            return
        self.input_count_label.config(text=f"Input chars: {len(text)}")
        self.on_process(auto=True)

    def on_process(self, auto=False):
        text = self.input_text.get("1.0", "end-1c")
        if self.input_placeholder:
            self.cards = []
            self.index = 0
            self.update_display()
            self.update_counts()
            self.show_alert("No content to split", "#f0a070")
            return
        self.cards = split_into_cards(text)
        self.index = 0
        self.update_display()
        self.update_counts()
        if self.cards:
            self.copy_to_clipboard(self.cards[0])
            self.show_alert("Successfully load with auto copy on card 1", "#7fe08a")
        else:
            self.show_alert("No content to split", "#f0a070")

    def update_counts(self):
        total = len(self.cards)
        self.cards_count_label.config(text=f"Cards: {total}")
        lengths = [len(c) for c in self.cards]
        self.card_lengths_label.config(text=f"Card lengths: {lengths}")

    def update_display(self):
        total = len(self.cards)
        if total == 0:
            self.card_label.config(text="Card 0 / 0")
            self.card_text.configure(state="normal")
            self.card_text.delete("1.0", "end")
            self.card_text.insert("1.0", "No code provided")
            self.card_text.tag_add("nocode", "1.0", "end")
            self.card_text.configure(state="disabled")
            return
        current = self.cards[self.index]
        self.card_label.config(text=f"Card {self.index+1} / {total}    chars: {len(current)}")
        self.card_text.configure(state="normal")
        self.card_text.delete("1.0", "end")
        self.card_text.insert("1.0", current)
        try:
            self.card_text.tag_remove("nocode", "1.0", "end")
        except Exception:
            pass
        self.apply_syntax_highlight(current)
        self.card_text.configure(state="disabled")

    def apply_syntax_highlight(self, text):
        self.card_text.configure(state="normal")
        tags = ("keyword", "string", "comment", "number", "builtin", "tag", "attr")
        for tag in tags:
            try:
                self.card_text.tag_remove(tag, "1.0", "end")
            except Exception:
                pass
        lang = detect_language(text)
        if lang == "python":
            kw = r'\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b'
            for m in re.finditer(kw, text):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("keyword", start, end)
            for m in re.finditer(r'#[^\n]*', text):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("comment", start, end)
            for m in re.finditer(r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'|\".*?\"|\'.*?\')', text, re.DOTALL):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("string", start, end)
            for m in re.finditer(r'\b\d+(\.\d+)?\b', text):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("number", start, end)
            for m in re.finditer(r'\b(print|len|range|open|int|str|list|dict|set|tuple|super)\b', text):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("builtin", start, end)
        elif lang == "javascript":
            kw = r'\b(break|case|catch|class|const|continue|debugger|default|delete|do|else|export|extends|finally|for|function|if|import|in|instanceof|let|new|return|super|switch|this|throw|try|typeof|var|void|while|with|yield)\b'
            for m in re.finditer(kw, text):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("keyword", start, end)
            for m in re.finditer(r'//[^\n]*', text):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("comment", start, end)
            for m in re.finditer(r'/\*.*?\*/', text, re.DOTALL):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("comment", start, end)
            for m in re.finditer(r'(\".*?\"|\'.*?\'|`.*?`)', text, re.DOTALL):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("string", start, end)
            for m in re.finditer(r'\b\d+(\.\d+)?\b', text):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("number", start, end)
            for m in re.finditer(r'\b(console|Math|JSON|Date|Array|String|Object)\b', text):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("builtin", start, end)
        elif lang == "html":
            for m in re.finditer(r'</?[\w:-]+', text):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("tag", start, end)
            for m in re.finditer(r'[\w-]+(?=\=)', text):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("attr", start, end)
            for m in re.finditer(r'(\".*?\"|\'.*?\')', text):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("string", start, end)
            for m in re.finditer(r'<!--.*?-->', text, re.DOTALL):
                start = "1.0 + %d chars" % m.start()
                end = "1.0 + %d chars" % m.end()
                self.card_text.tag_add("comment", start, end)

    def copy_to_clipboard(self, text):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
        except Exception:
            pass

    def prev_card(self):
        if not self.cards:
            self.show_alert("No cards loaded", "#f0a070")
            return
        if self.index > 0:
            self.index -= 1
            self.update_display()
            self.copy_to_clipboard(self.cards[self.index])
            self.show_alert(f"Auto copy on card {self.index+1}", "#7fe08a")
        else:
            self.show_alert("Already at first card", "#f0a070")

    def next_card(self):
        if not self.cards:
            self.show_alert("No cards loaded", "#f0a070")
            return
        if self.index < len(self.cards) - 1:
            self.index += 1
            self.update_display()
            self.copy_to_clipboard(self.cards[self.index])
            self.show_alert(f"Auto copy on card {self.index+1}", "#7fe08a")
        else:
            self.show_alert("Already at last card", "#f0a070")

    def first_card(self):
        if not self.cards:
            self.show_alert("No cards loaded", "#f0a070")
            return
        if self.index != 0:
            self.index = 0
            self.update_display()
            self.copy_to_clipboard(self.cards[self.index])
            self.show_alert("Auto copy on card 1", "#7fe08a")
        else:
            self.show_alert("Already at first card", "#f0a070")

    def show_alert(self, msg, color=None):
        self.alert_label.config(text=msg)
        if color:
            try:
                self.alert_label.configure(foreground=color)
            except Exception:
                pass
        else:
            self.alert_label.configure(foreground="#bfbfbf")
        self.root.after(3500, lambda: self.alert_label.config(text=""))

if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap("favicon.ico")
    except Exception:
        pass
    app = CardSplitterApp(root)
    root.mainloop()