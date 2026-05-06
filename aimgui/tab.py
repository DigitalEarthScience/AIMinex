import customtkinter as ctk
import tkinter as tk

class SharedContainer:
    def __init__(self, parent):
        # Initialize the tab container and content container
        self.tab_container = ctk.CTkFrame(parent)
        self.tab_container.pack(fill='x')
        self.content_container = ctk.CTkFrame(parent)
        self.content_container.pack(fill='both', expand=True)
        self.tabs = []
        self.current_tab = None
        self.tab_count = 0

        # Add a plus button for creating new tabs
        self.plus_button = ctk.CTkButton(self.tab_container, text="+", width=25, height=25, border_width=0, hover_color="darkgrey", text_color="black", fg_color="transparent", command=self.create_tab_button)
        #self.plus_button.pack(side=tk.RIGHT, padx=3, pady=3)

    def create_tab(self, title="New Tab"):
        # Create a new tab with a title
        self.tab_count += 1
        title = f"Layout {self.tab_count}"
        tab_frame = tk.Frame(
            self.tab_container,
            bd=1,
            relief=tk.RAISED,
            height=40
        )
        #tab_frame.pack_propagate(False)

        tab_label = ctk.CTkLabel(
            tab_frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold")
)
        tab_label.bind("<Double-1>", lambda event: self.edit_tab_label(tab_label))
        custom_font = ctk.CTkFont(size=12)
        close_button = ctk.CTkButton(tab_frame, text="x", width=28, height=32, border_width=0, font=custom_font, hover_color="darkgrey", text_color="black", command=lambda: self.close_tab(tab_frame, content_frame))
        
        close_button.pack(side=tk.RIGHT, padx=3, pady=3) #, fill=tk.Y)
        tab_label.pack(side=tk.LEFT, padx=3, pady=3) #, fill=tk.Y)

        self.plus_button.pack_forget()
        tab_frame.pack(side=tk.LEFT, padx=2, pady=2)
        self.plus_button.pack(side=tk.LEFT, padx=3, pady=3)

        content_frame = ctk.CTkFrame(self.content_container)
        content_frame.pack(fill='both', expand=True)

        tab_frame.bind("<Button-1>", lambda event: self.select_tab(tab_frame, content_frame))
        tab_label.bind("<Button-1>", lambda event: self.select_tab(tab_frame, content_frame))
        close_button.bind("<Button-1>", lambda event: self.select_tab(tab_frame, content_frame))

        self.tabs.append((tab_frame, content_frame))
        self.select_tab(tab_frame, content_frame)
        self.adjust_tab_widths()
    
    def adjust_tab_widths(self):
        self.max_tab_width = 150
        
        # Adjust the width of each tab icon
        total_width = self.tab_container.winfo_width() - self.plus_button.winfo_width() - 10
        tab_width = min(self.max_tab_width, total_width // len(self.tabs) - 4 if self.tabs else total_width)
    
        for tab_frame, _ in self.tabs:
            tab_frame.config(width=tab_width)
            #tab_frame.pack_propagate(False)


    def create_tab_button(self):
        # Create a new tab with default title "Layout #"
        self.create_tab()

    def select_tab(self, tab_frame, content_frame):
        # Highlight the selected tab and show its content
        if self.current_tab:
            self.current_tab[0].config(bg='lightgrey')
            for widget in self.current_tab[0].winfo_children():
                widget.configure(fg_color='lightgrey')

        tab_frame.config(bg='gray95')
        for widget in tab_frame.winfo_children():
            widget.configure(fg_color='gray95')

        for frame in self.content_container.winfo_children():
            frame.pack_forget()

        content_frame.pack(fill='both', expand=True)
        self.current_tab = (tab_frame, content_frame)
        content_frame.update_idletasks()

    def close_tab(self, tab_frame, content_frame):
        # Close the selected tab and select the previous tab if available
        if self.current_tab == (tab_frame, content_frame):
            self.current_tab = None
        tab_frame.destroy()
        content_frame.destroy()
        self.tabs.remove((tab_frame, content_frame))
        if self.tabs:
            self.select_tab(*self.tabs[-1])
        self.adjust_tab_widths()

    def edit_tab_label(self, tab_label):
        # Enable editing of the tab label
        current_text = tab_label.cget("text")
        tab_frame = tab_label.master

        entry = tk.Entry(tab_frame, width=10)
        entry.insert(0, current_text)
        entry.pack(side=tk.LEFT, padx=3, pady=3)
        entry.bind("<Return>", lambda event: self.update_tab_label(tab_label, entry))
        entry.bind("<FocusOut>", lambda event: self.update_tab_label(tab_label, entry))
        entry.focus()

        tab_label.pack_forget()

    def update_tab_label(self, tab_label, entry):
        # Update the tab label with new text
        new_text = entry.get()
        tab_label.configure(text=new_text)
        entry.destroy()
        tab_label.pack(side=tk.LEFT, padx=3, pady=3)
        self.tab_container.update_idletasks()
