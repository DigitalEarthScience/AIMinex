import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, scrolledtext, Menu, font as tkfont
from tkinter import filedialog as fd
from customtkinter import CTkImage
from tkinter import PanedWindow
from tkinter import messagebox
import darkdetect

import pandas as pd
import numpy as np

from sklearn.decomposition import PCA, KernelPCA

from PIL import Image
import webbrowser
import os
import platform

from aimgui.terminal import MATerminal
from aimgui.pca import PCA_class
from aimgui.supervised import supervised_learning
from aimgui.tab import SharedContainer
from aimgui.loadings import loading_class
from aimgui.loading_cluster import loading_cluster
from aimgui.sample import sample_class
from aimgui.sample_cluster import sample_cluster
from aimgui.drill import drill_class
from aimgui.biplot2d import class2d
from aimgui.biplot3d import class3d
from aimgui.cluster2d import Cluster2DPlotClass
from aimgui.cluster3d import Cluster3DPlotClass
from aimgui.about import show_about
from aimgui import color_change


class MainApp(ctk.CTk):        
    def __init__(self):
        super().__init__()
        # ---------------------------------------------------------
        # Cross-platform UI scaling and fonts
        # ---------------------------------------------------------
        system_name = platform.system()
        if system_name == "Windows":
            scale = 1.25
            self.default_font_family = "Segoe UI"
            self.mono_font_family = "Consolas"

        elif system_name == "Darwin":   # macOS
            scale = 1.15
            self.default_font_family = "SF Pro Display"
            self.mono_font_family = "Menlo"

        else:   # Linux
            scale = 1.20
            self.default_font_family = "DejaVu Sans"
            self.mono_font_family = "DejaVu Sans Mono"

        # CustomTkinter scaling
        ctk.set_widget_scaling(scale)
        ctk.set_window_scaling(1.0)

        # DPI-aware reusable font sizes
        self.tk_scaling = float(self.tk.call('tk', 'scaling'))

        self.font_size_small = int(10 * self.tk_scaling)
        self.font_size_normal = int(12 * self.tk_scaling)
        self.font_size_large = int(14 * self.tk_scaling)

        # For tab title size
        self.tab_font_size = 11

        # Global Tk fonts
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(
            family=self.default_font_family,
            size=self.font_size_normal
        )

        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(
            family=self.default_font_family,
            size=self.font_size_normal
        )

        fixed_font = tkfont.nametofont("TkFixedFont")
        fixed_font.configure(
            family=self.mono_font_family,
            size=self.font_size_normal
        )
        
        # ttk styling
        style = ttk.Style()

        style.theme_use("clam")

        # Tabs are entirely taken care of in tab.py
        # style.configure(
        #     "TNotebook",
        #     tabmargins=(2, 6, 2, 0)
        # )

        # style.configure(
        #     "TNotebook.Tab",
        #     font=(self.default_font_family,  self.tab_font_size),
        #     padding=(16, 8)
        # )

        # style.map(
        #     "TNotebook.Tab",
        #     expand=[("selected", [1, 1, 1, 0])]
        # )

        style.configure(
            "Treeview",
            font=(self.default_font_family, 11),
            rowheight=40
        )

        style.configure(
            "Treeview.Heading",
            font=(self.default_font_family, 12, "bold")
        )

        style.configure(
            "TCombobox",
            font=(self.default_font_family, 12)
        )
        #------------------------------------------------------------

        self.title("AIMinex")
        #setting icon        
        if platform.system() == 'Windows':            
            icon_path = 'images/favicons/favicon.ico'
            self.iconbitmap(icon_path)
        else:            
            icon_path = 'images/favicons/favicon.png'
            icon = tk.PhotoImage(file=icon_path)
            self.iconphoto(False, icon)

        ctk.set_appearance_mode("System")
        style = ttk.Style()
        style.theme_use("default")
        # Setting application window
        # screen_width = self.winfo_screenwidth()
        # screen_height = self.winfo_screenheight()
        
        # self.geometry(f"{screen_width}x{screen_height}")   

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

        # if platform.system() == "Windows":
        #     self.after(100, lambda: self.state("zoomed"))
        # else:
        #     self.geometry(f"{screen_width}x{int(screen_height * 0.92)}+0+0") 
        #------------------------------------------------------------   

        self.filtered_df = pd.DataFrame()
        self.box_frame_sub_visible = True
        self.create_widgets()
        self.data_columns = None
        self.group_column = None

    def toggle_box_frame_sub(self):
        if self.box_frame_sub_visible:
            self.box_frame_sub.grid_remove()
            self.box_frame_sub_visible = False
            self.toggle_button.configure(text='>')
        else:
            self.box_frame_sub.grid()
            self.box_frame_sub_visible = True
            self.toggle_button.configure(text='<')

    def update_toggle_button_position(self, event=None):
        # update button position
        self.update_idletasks()

        if self.box_frame_sub_visible:
            x = self.box_frame_sub.winfo_x() + self.box_frame_sub.winfo_width() - (self.toggle_button.winfo_width() // 2.5)
        else:
            x = self.selection_frame.winfo_x() + self.selection_frame.winfo_width()

        y = self.winfo_height() // 2 - self.toggle_button.winfo_height() // 2

        self.toggle_button.place(x=x, y=y)        
    
    
    def create_widgets(self):
        # Create a PanedWindow
        self.paned_window = PanedWindow(self, orient='horizontal')
        self.paned_window.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self.paned_window)
        self.paned_window.add(self.left_frame, stretch="always")

        self.right_frame = ctk.CTkFrame(self.paned_window, width=300)
        self.paned_window.add(self.right_frame, stretch="never")
    
        # Left Frame contents
        self.selection_frame = ctk.CTkFrame(self.left_frame, height=250)
        self.selection_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", pady=(5,0), padx=5)
        
        self.box_frame = ctk.CTkFrame(self.left_frame, width=150)
        self.box_frame.grid(row=2, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)
        
        self.box_frame_sub = ctk.CTkFrame(self.left_frame, width=200)
        self.box_frame_sub.pack_propagate(False)
        self.box_frame_sub.grid(row=0, column=1, rowspan=4, sticky="ns", pady=5)
        
        self.bargraph_frame = ctk.CTkFrame(self.left_frame, width=600)
        self.bargraph_frame.grid(row=0, column=2, rowspan=4, sticky="nsew", pady=5, padx=5)
        
        self.left_frame.grid_columnconfigure(2, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=1)

        # Right Frame contents
        self.legend_frame = ctk.CTkScrollableFrame(self.right_frame, width=300)
        self.legend_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=(5, 0))
        
        self.output_frame = ctk.CTkFrame(self.right_frame, width=300, height=500)
        self.output_frame.pack_propagate(False)
        self.output_frame.grid(row=2, column=0, rowspan=3, sticky="nsew", padx=5, pady=5)

        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Create the toggle button
        self.toggle_button = ctk.CTkButton(
            self,
            text="<",
            width=20,
            fg_color='transparent',
            hover=False,
            text_color="black",
            command=self.toggle_box_frame_sub
        )
        self.toggle_button.place(x=0, y=0)

        self.bind('<Configure>', self.update_toggle_button_position)

        self.output_text = scrolledtext.ScrolledText(
            self.output_frame, 
            wrap="word", 
            bd=0,
            highlightthickness=0,
            font=(self.mono_font_family, self.font_size_normal)
        )
        self.output_text.pack(fill="both", expand=True)

        menubar = Menu(self)
        menu_font = (self.default_font_family, self.font_size_normal)
        self.filemenu = Menu(menubar, tearoff=0, font=menu_font)

        # Create file menu options
        self.filemenu.add_command(label="Open File", command=self.load_data)
        self.filemenu.add_command(label="New Tab", command=lambda: self.shared_container.create_tab())
        self.filemenu.entryconfig("New Tab", state=tk.DISABLED)
        
        self.save_pc_menu = tk.Menu(self.filemenu, tearoff=0, font=menu_font)
        
        # Create save PC options
        self.save_pc_menu.add_command(label="Save PC by sample excel", command=self.export_pc_by_sample)
        self.save_pc_menu.add_command(label="Save PC by element excel", command=self.export_pc_by_element)
        
        self.save_pc_menu.entryconfig("Save PC by sample excel", state=tk.DISABLED)
        self.save_pc_menu.entryconfig("Save PC by element excel", state=tk.DISABLED)
        
        self.filemenu.add_cascade(label="Save PC", menu=self.save_pc_menu)
        
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=self.filemenu)
        
        #edit menu
        self.editmenu = Menu(menubar, tearoff=0, font=menu_font)
        self.editmenu.add_command(label="Edit Data Point Color/Shape", command=lambda: color_change.open_color_window(self), state="disabled")

        menubar.add_cascade(label="Edit", menu=self.editmenu)      
        
        # Add "Settings" option under the "Edit" menu, which opens the settings popup
        # Initialize default appearance mode and color theme
        self.current_appearance_mode = "system"  # Default is system
        self.current_color_theme = "blue"  # Default theme is blue

        # Set the appearance mode and color theme initially
        ctk.set_appearance_mode(self.current_appearance_mode)
        ctk.set_default_color_theme(self.current_color_theme)
        
        self.editmenu.add_command(label="Settings", command=self.open_settings)

        # Create help menu options
        helpmenu = Menu(menubar, tearoff=0, font=menu_font)
        helpmenu.add_command(label="User Manual", command=self.open_help_html)
        helpmenu.add_separator()
        helpmenu.add_command(label="Shortcuts:", command=None)
        helpmenu.add_command(label="Select_all", command=None, accelerator="Ctrl+a / Cmd+a")
        helpmenu.add_command(label="Deselect_all", command=None, accelerator="Ctrl+d / Cmd+d")
        helpmenu.add_separator()
        helpmenu.add_command(label="About...", command=show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.config(menu=menubar)
        
        #initialize terminal
        self.terminal = MATerminal(self.output_text, self)

        #make sure color matches during night
        # style = ttk.Style()
        # style.map('TCombobox', 
        # fieldbackground=[('readonly', 'white')],
        # background=[('readonly', 'lightgrey')])            
    
    # Function to change appearance mode.
    def change_appearance_mode(self, mode):
        self.current_appearance_mode = mode
        ctk.set_appearance_mode(mode)

        # set default highlight color
        system_select_bg = self.option_get('selectBackground', '')

        if not system_select_bg:
            system_select_bg = 'LightSkyBlue1'  

        if self.current_appearance_mode == "system":
            if darkdetect.isDark():
                self.tk_setPalette(background='#2E2E2E', foreground='white', selectBackground='#476288', activeForeground='white')    

            else:
                self.tk_setPalette(background='white', foreground='black', selectBackground=system_select_bg, activeForeground='black')    


        elif self.current_appearance_mode == "light":
            self.tk_setPalette(background='white', foreground='black', selectBackground=system_select_bg, activeForeground='black')    

        else:
            self.tk_setPalette(background='#2E2E2E', foreground='white', selectBackground='#476288', activeForeground='white')    


    # Function to change color theme (default CustomTkinter themes)
    def change_color_theme(self, theme):
        self.current_color_theme = theme
        ctk.set_default_color_theme(theme) 

    # Function to open the Settings popup
    def open_settings(self):
        # Create a new settings popup (top-level window)
        settings_popup = ctk.CTkToplevel(self)
        settings_popup.title("Settings")

        # Set the size of the settings popup window
        settings_popup.geometry("250x350")
        settings_popup.attributes("-topmost", True)  # Ensure it stays on top

        # Add Appearance Mode options
        appearance_mode_label = ctk.CTkLabel(settings_popup, text="Appearance Mode:")
        appearance_mode_label.pack(pady=10)

        appearance_mode_var = tk.StringVar(value=self.current_appearance_mode)  # Set initial value

        # Create Radio Buttons with the correct checked state
        appearance_mode_system = ctk.CTkRadioButton(settings_popup, text="System", variable=appearance_mode_var, value="system", command=lambda: self.change_appearance_mode("system"))
        appearance_mode_system.pack(pady=5)

        appearance_mode_light = ctk.CTkRadioButton(settings_popup, text="Light", variable=appearance_mode_var, value="light", command=lambda: self.change_appearance_mode("light"))
        appearance_mode_light.pack(pady=5)

        appearance_mode_dark = ctk.CTkRadioButton(settings_popup, text="Dark", variable=appearance_mode_var, value="dark", command=lambda: self.change_appearance_mode("dark"))
        appearance_mode_dark.pack(pady=5)

        # Add Color Theme options
        color_theme_label = ctk.CTkLabel(settings_popup, text="Color Theme:")
        color_theme_label.pack(pady=10)

        color_theme_var = tk.StringVar(value=self.current_color_theme)  # Set initial value

        # Create Radio Buttons with the correct checked state
        color_theme_blue = ctk.CTkRadioButton(settings_popup, text="Blue", variable=color_theme_var, value="blue", command=lambda: self.change_color_theme("blue"))
        color_theme_blue.pack(pady=5)

        color_theme_dark_blue = ctk.CTkRadioButton(settings_popup, text="Dark Blue", variable=color_theme_var, value="dark-blue", command=lambda: self.change_color_theme("dark-blue"))
        color_theme_dark_blue.pack(pady=5)

        color_theme_green = ctk.CTkRadioButton(settings_popup, text="Green", variable=color_theme_var, value="green", command=lambda: self.change_color_theme("green"))
        color_theme_green.pack(pady=5)

        # Close Button
        close_button = ctk.CTkButton(settings_popup, text="Close", command=settings_popup.destroy)
        close_button.pack(pady=20)

        settings_popup.mainloop()               
    
    def open_help_html(self):
        import urllib.parse
        # Open HTML help file
        html_path = 'doc/_build/html/index.html'
        absolute_path = os.path.abspath(html_path)
        file_url = urllib.parse.urljoin('file:', urllib.request.pathname2url(absolute_path))
        print(f"Opening HTML file at: {file_url}")
        
        try:
            if os.path.exists(absolute_path):
                webbrowser.open_new_tab(file_url)
                print("HTML file opened successfully.")
            else:
                print(f"File does not exist: {absolute_path}")
        except Exception as e:
            print(f"Error opening HTML file: {e}")

    def load_data(self):
        # Load data from selected file
        try:
            self.file_path = fd.askopenfilename()
            if not self.file_path:
                self.output_text.insert("end", "No file selected\n")
                return

            self.clear_all()
            
            self.button_0()
            self.sheet_names = pd.ExcelFile(self.file_path).sheet_names
            self.sheet_combobox.configure(values=self.sheet_names)
            self.output_text.insert("end", "File loaded successfully. Please select a sheet.\n")

        except:
            self.output_text.insert("end", "Error loading file: \n")

    def load_selected_sheet(self):
        #initialize tab function
        self.filemenu.entryconfig("New Tab", state=tk.NORMAL)
        self.shared_container = SharedContainer(self.bargraph_frame)
        
        # Load selected sheet from the file
        try:
            selected_sheet = self.sheet_combobox.get()
            if selected_sheet not in self.sheet_names:
                self.output_text.insert("end", "Invalid sheet name\n")
                return
            self.sheet_name=selected_sheet
            self.df_0 = pd.read_excel(self.file_path, self.sheet_name)
            # if 'Zn_ppm' in self.df_0.columns:
            #     before_count = len(self.df_0)
            #     self.df_0 = self.df_0[self.df_0['Zn_ppm'] >= 1000]
            #     after_count = len(self.df_0)
            #     self.output_text.insert(
            #         "end",
            #         f"Filtered zn_ppm < 1000: {before_count - after_count} rows removed, {after_count} remain.\n"
            #    )
            
            for widget in self.selection_frame.winfo_children():
                widget.destroy()
            
        except Exception as e:
            self.output_text.insert("end", f"Error loading sheet: {str(e)}\n")
        
        self.open_column_selector()
        
    def open_column_selector(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Select Data Columns")
        popup.geometry("950x450")
        popup.attributes("-topmost", True)
        popup.rowconfigure(2, weight=1)
        popup.columnconfigure(0, weight=1)

        #scrollbar
        xscroll = tk.Scrollbar(popup, orient="horizontal")
        xscroll.grid(row=3, column=0, columnspan=4, sticky="ew")

        #checkboxes
        hdr_canvas = tk.Canvas(popup, height=40, highlightthickness=0,
                            xscrollcommand=xscroll.set)
        hdr_canvas.grid(row=0, column=0, columnspan=4,
                        sticky="ew", padx=5, pady=(10,0))
        hdr_inner = tk.Frame(hdr_canvas)
        hdr_canvas.create_window((0,0), window=hdr_inner, anchor="nw")
        def _on_hdr_config(e):
            hdr_canvas.configure(scrollregion=hdr_canvas.bbox("all"))
        hdr_inner.bind("<Configure>", _on_hdr_config)

        #Treeview to measure column widths
        cols = list(self.df_0.columns)
        tree = ttk.Treeview(popup, columns=cols, show="headings", height=12,
                            selectmode="none")
        for col in cols:
            tree.heading(col, text=col, anchor="w")
            tree.column(col, anchor="w", width=90)
        for idx, row in self.df_0.head(300).iterrows():
            tree.insert("", "end", iid=str(idx), values=list(row))

        #Create & align checkboxes
        font = tkfont.Font(font = "TkDefaultFont", size = 11)
        check_vars = {}
        for i, col in enumerate(cols):
            # ellipsize label
            w = tree.column(col)["width"]
            label = col
            if font.measure(label)+3 > w:
                lo, hi = 0, len(label)
                while lo < hi:
                    mid = (lo+hi)//2
                    if font.measure(label[:mid]+"...") <= w:
                        lo = mid+1
                    else:
                        hi = mid
                label = label[:lo-5] + "..."
            var = tk.BooleanVar(value=False)
            cb  = tk.Checkbutton(hdr_inner, text=label, variable=var)
            cb.grid(row=0, column=i, sticky="w", padx=0)
            hdr_inner.grid_columnconfigure(i, minsize=w)
            check_vars[i] = var

        #Auto-select pct/ppm on first open, else restore last choices
        if not self.data_columns:
            for i, col in enumerate(cols):
                if 'pct' in col.lower() or 'ppm' in col.lower():
                    check_vars[i].set(True)
        else:
            prev = set(self.data_columns)
            for i, col in enumerate(cols):
                if col in prev:
                    check_vars[i].set(True)

        #selection
        hdr_inner.bind_class("Checkbutton", "<B1-Motion>",
                            lambda e: e.widget.invoke())
        ctk.CTkButton(popup, text="Select All", width=90,
                    command=lambda: [v.set(True) for v in check_vars.values()])\
            .grid(row=1, column=0, sticky="w", padx=(10,0), pady=6)
        ctk.CTkButton(popup, text="Clear All", width=90,
                    command=lambda: [v.set(False) for v in check_vars.values()])\
            .grid(row=1, column=0, sticky="w", padx=(110,0), pady=6)

        #Sync scrolling
        def safe(x, *a):
            try: x(*a)
            except tk.TclError: pass

        def scroll_both(*a):
            safe(hdr_canvas.xview, *a)
            safe(tree.xview, *a)
        xscroll.config(command=scroll_both)

        def on_tree_x(f, l):
            safe(hdr_canvas.xview, "moveto", f)
            xscroll.set(f, l)
        tree.configure(xscrollcommand=on_tree_x)

        tree.grid(row=2, column=0, columnspan=4,
                sticky="nsew", padx=10, pady=5)

        #Cell highlight
        tree.tag_configure("cellsel", background="lightblue")
        def on_cell_click(evt):
            for itm in tree.get_children():
                vals = tree.item(itm, "values")
                clean = [str(v).strip("[]") for v in vals]
                tree.item(itm, values=clean, tags=[])

            r, c = tree.identify_row(evt.y), tree.identify_column(evt.x)
            if not (r and c): return
            vals = tree.item(r, "values")
            ci   = int(c.lstrip("#")) - 1
            new  = [f"[{v}]" if i==ci else v
                    for i, v in enumerate(vals)]
            tree.item(r, values=new, tags=("cellsel",))
        tree.bind("<Button-1>", on_cell_click)

        #Select Similar
        last = {}
        ctx  = tk.Menu(popup, tearoff=0)
        ctx.add_command(label="Select Similar", command=lambda: select_similar())
        def on_rc(evt):
            last['x'], last['y'] = evt.x, evt.y
            ctx.tk_popup(evt.x_root, evt.y_root)
        tree.bind("<Button-3>", on_rc)
        tree.bind("<Button-2>", on_rc)
        def select_similar():
            if 'x' not in last:
                messagebox.showinfo("No cell clicked",
                                    "Right-click on a data cell first.")
                return
            r = tree.identify_row(last['y'])
            c = tree.identify_column(last['x'])
            if not (r and c):
                messagebox.showinfo("Invalid click",
                                    "Right-click must be on a data cell.")
                return
            ri, ci = int(r), int(c.lstrip("#"))-1
            txt = str(self.df_0.iat[ri,ci]).strip()
            if not txt:
                messagebox.showinfo("Empty cell", "That cell is empty.")
                return
            matches = [i for i in range(len(cols))
                    if txt in str(self.df_0.iat[ri,i])]
            if not matches:
                messagebox.showinfo("No matches",
                    f"No other cells in row {ri+1} contain “{txt}.”")
                return
            for i in matches:
                check_vars[i].set(True)

        #Confirm & store choices
        def _confirm():
            chosen = [i for i,v in check_vars.items() if v.get()]
            if not chosen:
                messagebox.showwarning(
                    "No data columns", "Tick at least one column above."
                )
                return
            self.data_columns = [cols[i] for i in chosen]
            popup.destroy()
            self.process_sheet()

        ctk.CTkButton(popup, text="Confirm", command=_confirm)\
            .grid(row=1, column=3, sticky="e", padx=10, pady=6)


    def process_sheet(self):
        # Create widgets to select scaler/pca type, and column to use to filter data. 
        if self.group_column:
            valid_columns = [self.group_column]
        else:
            valid_columns = [col for col in self.df_0.columns 
                            if '_ppm' not in col and '_pct' not in col]

        self.scaler_combo = ctk.CTkComboBox(
            self.selection_frame, 
            values=[
                "Standard Scaler",
                "Logarithmic Scaler",
                "Logarithmic Scaler + Standard Scaler"
                ],
            state="readonly",
            font=(self.default_font_family, 12),
            dropdown_font=(self.default_font_family, 12)
        )
        self.scaler_combo.set("Standard Scaler")
        self.pca_type_combo = ctk.CTkComboBox(
            self.selection_frame, 
            values=[
                "PCA", 
                "Kernel PCA"
                ], 
            command=self.kernelstat, 
            state="readonly",
            font=(self.default_font_family, self.font_size_normal),
            dropdown_font=(self.default_font_family, self.font_size_normal)
        )
        self.pca_type_combo.set("PCA")
        self.slider = ctk.CTkSlider(self.selection_frame, from_=1, to=8, number_of_steps=7, command=self.on_slider_change)
        self.slider.set(6)

        if valid_columns:
            self.select_data_btn = ctk.CTkButton(self.selection_frame, text="Select Data Columns…", command=self.open_column_selector)
            self.select_data_btn.grid(row=0, column=0, columnspan=4, sticky="we", pady=(5,0), padx=5)
            ctk.CTkLabel(self.selection_frame, text="Filter by:").grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=(5,0))
            self.selected_column_combobox = ctk.CTkComboBox(
                self.selection_frame, 
                values=valid_columns, 
                state="readonly",
                font=(self.default_font_family, self.font_size_normal),
                dropdown_font=(self.default_font_family, self.font_size_normal),
                command = self.update_listbox
            )
            self.selected_column_combobox.grid(row=1, column=2, columnspan=2, sticky="we", padx=5, pady=(5,0))
            self.selected_column_combobox.set(valid_columns[0])

        else:
            self.output_text.insert("end", "No valid columns found in dataframe\n")

        self.update_listbox()

    def update_listbox(self, event=None):
        # create listbox containing unique groups in select column to filter (lithology stands for unique group/name)
        self.selected_column = self.selected_column_combobox.get()

        # if self.selected_column == "None(include ALL)":
        #     self.create_buttons()
        listbox_font_size = int(12 * self.tk.call('tk', 'scaling'))
        if self.selected_column:
            self.df_0[self.selected_column] = self.df_0[self.selected_column].apply(lambda x: x.strip().lower().title() if isinstance(x, str) and pd.notnull(x) else x)
            self.lithology_listbox = tk.Listbox(
                self.selection_frame, 
                selectmode=tk.MULTIPLE,
                font=(self.default_font_family, listbox_font_size),
                height=10
            )            
            self.lithologies = self.df_0[self.selected_column].unique()

            for lithology in self.lithologies:
                self.lithology_listbox.insert(tk.END, lithology)
            self.create_lithobuttons()
        else:
            self.output_text.insert("end", "Please select a valid column\n")
            self.create_buttons()

    def button_0(self):
        # Create sheet combobox and load button
        self.sheet_combobox = ctk.CTkComboBox(self.selection_frame, values=[], state="readonly")
        self.sheet_combobox.pack(padx=5, pady=5)
        self.sheet_combobox.set("Select a sheet")
        self.load_sheet_button = ctk.CTkButton(self.selection_frame, text="Load Sheet", command=self.load_selected_sheet)
        self.load_sheet_button.pack(pady=5)

    def create_lithobuttons(self):
        # Create lithology selection buttons
        self.lithology_listbox.grid(row=2, column=0, columnspan=4, sticky="we", padx=5, pady=(5,0))
        
        # Select all
        def select_all():
            self.lithology_listbox.selection_set(0, tk.END)
            
        def deselect_all():
            self.lithology_listbox.selection_clear(0, tk.END)
            
        # Bind select all to Command+A and Control+A
        self.lithology_listbox.bind('<Command-a>', lambda event: select_all())
        self.lithology_listbox.bind('<Control-a>', lambda event: select_all())
        # Bind deselect all to Command+D and Control+D
        self.lithology_listbox.bind('<Command-d>', lambda event: deselect_all())
        self.lithology_listbox.bind('<Control-d>', lambda event: deselect_all())

        self.create_buttons()

    def create_buttons(self):
        # Pack PCA and scaling options widgets
        self.current_button = None
        
        self.scaler_combo.grid(row=3, column=0, columnspan=4, sticky="we", padx=5, pady=(5,0))
  
        self.pca_type_combo.grid(row=4, column=0, columnspan=4, sticky="we", padx=5, pady=(5,0))

        ctk.CTkLabel(self.selection_frame, text="Number of PCA Components:").grid(row=9, column=0, columnspan=4, sticky="we", padx=5, pady=(5,0))

        self.slider.grid(row=10, column=0, columnspan=4, padx=10, pady=0)
        self.label = ctk.CTkLabel(self.selection_frame, text=f"Current value: {int(self.slider.get())}")
        self.label.grid(row=11, column=0, columnspan=4, padx=5, pady=0)

        # initiate widgets for kernal parameters
        self.gamma_slider = ctk.CTkSlider(self.selection_frame, from_=0, to=1, width=100, command=self.gamma_change)
        self.degree_slider = ctk.CTkSlider(self.selection_frame, from_=0, to=10, width=100, command=self.degree_change)
        self.coef_slider = ctk.CTkSlider(self.selection_frame, from_=0, to=10, width=100, command=self.coef_change)
        
        self.label1 = ctk.CTkLabel(self.selection_frame, text=f"Gamma: {self.gamma_slider.get():.2f}")
        self.label2 = ctk.CTkLabel(self.selection_frame, text=f"Degree: {self.degree_slider.get():.2f}")
        self.label3 = ctk.CTkLabel(self.selection_frame, text=f"Coef: {self.coef_slider.get():.2f}")

        # set defaults and configure
        filtered_columns = self.data_columns
        #filtered_columns = [col for col in self.df_0.columns if '_ppm' in col or '_pct' in col]
        
        num_filtered_features = len(filtered_columns)
        
        self.gamma_slider.set(1/num_filtered_features)
        self.degree_slider.set(3)
        self.coef_slider.set(1)

        self.gamma = 1/num_filtered_features
        self.degree = 3
        self.coef = 1
        
        self.label1.configure(text=f"Gamma: {self.gamma:.2f}")
        self.label2.configure(text=f"Degree: {self.degree:.2f}")
        self.label3.configure(text=f"Coef: {self.coef:.2f}")
        
        # kernel combobox
        self.kernel_combo = ctk.CTkComboBox(self.selection_frame, values=["linear", "poly", "rbf", "sigmoid", "cosine"], command=self.kernel_param, state="readonly")
        self.kernel_text = ctk.CTkLabel(self.selection_frame, text="Kernel:")
        self.kernel_combo.set("linear")

        self.apply_button = ctk.CTkButton(self.selection_frame, text="Apply", command= self.filter_dataframe)
        self.apply_button.grid(row=12, column=0, columnspan=4, padx=5, pady=(0,5))

        self.kernel_param()

    def kernel_param(self, *arg):
        self.kernel = self.kernel_combo.get()
         
        # clear all previous sliders
        try:
            self.gamma_slider.grid_forget()
            self.degree_slider.grid_forget()
            self.coef_slider.grid_forget()
            self.label1.grid_forget()
            self.label2.grid_forget()
            self.label3.grid_forget()
        except:
            pass

        if self.kernel == "rbf":
            self.gamma_slider.grid(row=6, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label1.grid(row=6, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)

        elif self.kernel == "poly":
            self.gamma_slider.grid(row=6, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label1.grid(row=6, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)
            
            self.degree_slider.grid(row=7, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label2.grid(row=7, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)

            self.coef_slider.grid(row=8, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label3.grid(row=8, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)

        elif self.kernel == "sigmoid":
            self.gamma_slider.grid(row=6, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label1.grid(row=6, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)
            
            self.coef_slider.grid(row=7, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label3.grid(row=7, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)

        else:
            pass
                
    def kernelstat(self, *args):
        # Show kernel options if Kernel PCA is selected
        pca_type = self.pca_type_combo.get()
        if pca_type == "Kernel PCA":
            self.kernel_combo.grid(row=5, column=1, columnspan=3, sticky="we", padx=5, pady=(5,0))
            self.kernel_text.grid(row=5, column=0, sticky="w", padx=(10,0), pady=(5,0))
            self.kernel_param()
        else:
            self.kernel_combo.grid_forget()
            self.kernel_text.grid_forget()
            # clear all previous sliders
            try:
                self.gamma_slider.grid_forget()
                self.degree_slider.grid_forget()
                self.coef_slider.grid_forget()
                self.label1.grid_forget()
                self.label2.grid_forget()
                self.label3.grid_forget()
            except:
                pass
            
    def on_slider_change(self, value):
        # Update label when slider changes
        self.label.configure(text=f"Current value: {int(value)}")

    def gamma_change(self, value):
        # Update label when slider changes
        self.label1.configure(text=f"Gamma: {value:.2f}")
        self.gamma = value

    def degree_change(self, value):
        # Update label when slider changes
        self.label2.configure(text=f"Degree: {value:.2f}")
        self.degree = value

    def coef_change(self, value):
        # Update label when slider changes
        self.label3.configure(text=f"Coef: {value:.2f}")
        self.coef = value

    def on_button_click(self, button, command):
        # Handle button click and change appearance
        if self.current_button is not None:
            self.current_button.configure(fg_color='transparent') #'#3B8ED0'
        else:
            pass
            
        button.configure(fg_color="grey")
        self.current_button = button
        command()

    def clear_all(self):
        # Clear all widgets in frames
        for widget in self.bargraph_frame.winfo_children():
            widget.destroy()
        for widget in self.box_frame.winfo_children():
            widget.destroy()
        for widget in self.box_frame_sub.winfo_children():
            widget.destroy()
        for widget in self.legend_frame.winfo_children():
            widget.destroy()
        for widget in self.selection_frame.winfo_children():
            widget.destroy()

    def clear(self):
        # Clear specific widgets in frames
        for widget in self.box_frame.winfo_children():
            widget.destroy()
        for widget in self.box_frame_sub.winfo_children():
            widget.destroy()
        self.output_text.delete("1.0", tk.END)
        for widget in self.legend_frame.winfo_children():
            widget.destroy()

    # def filter_dataframe(self):   
    #     # delete previous labels
    #     if hasattr(self, 'scaler_label') and self.scaler_label is not None:
    #         self.scaler_label.destroy()
    #         del self.scaler_label
            
    #     if hasattr(self, 'pca_label') and self.pca_label is not None:
    #         self.pca_label.destroy()
    #         del self.pca_label

    #     if hasattr(self, 'color_window') and self.color_window.winfo_exists():
    #         self.color_window.destroy()

    #     if hasattr(self, 'lithologies_label') and self.lithologies_label is not None:
    #         self.lithologies_label.destroy()
    #         del self.lithologies_label

    #     #set PCA/Kernel PCA parameters
    #     if self.pca_type_combo.get() == "PCA":
    #         self.pca_label = ctk.CTkLabel(self.selection_frame, text="PCA", font=("Arial", 12))
            
    #     if self.pca_type_combo.get() == "Kernel PCA":
    #         if self.kernel == "rbf":
    #             self.pca_label = ctk.CTkLabel(self.selection_frame, text= f"Kernel PCA-{self.kernel} ({self.gamma:.2f})", font=("Arial", 12))  
    #         elif self.kernel == "poly":
    #             self.pca_label = ctk.CTkLabel(self.selection_frame, text= f"Kernel PCA-{self.kernel} ({self.gamma:.2f}, {self.degree:.1f}, {self.coef:.1f})", font=("Arial", 12))  
    #         elif self.kernel == "rbf":
    #             self.pca_label = ctk.CTkLabel(self.selection_frame, text= f"Kernel PCA-{self.kernel} ({self.gamma:.2f}, {self.coef:.1f})", font=("Arial", 12))  
    #         else:
    #             self.pca_label = ctk.CTkLabel(self.selection_frame, text= f"Kernel PCA-{self.kernel}", font=("Arial", 12)) 
                
    #     self.pca_label.grid(row=14, column=0, columnspan=4, pady=(0,5))
            
    #     if self.scaler_combo.get() == "Select PCA Scaler:":
    #         self.scaler_label = ctk.CTkLabel(self.selection_frame, text="Select a Scaler", font=("Arial", 12))
    #         self.scaler_label.grid(row=13, column=0, columnspan=4, padx=5, pady=0)
    #         return
    #     else:
    #         # self.scaler_label.grid_forget()
    #         self.scaler_label = ctk.CTkLabel(self.selection_frame, text= f"Selected scaler: {self.scaler_combo.get()}", font=("Arial", 12), wraplength=200)
    #         self.scaler_label.grid(row=13, column=0, columnspan=4, padx=5, pady=0)
   
    #     self.clear()
    #     self.current_button = None

    #     #Filter/process dataframe based on selected lithology and parameters
    #     try:
    #         # Find selected lithologies(unique groups) and add check mark to them
    #         selected_indices = self.lithology_listbox.curselection()

    #         select_lithologies = [self.lithology_listbox.get(i) for i in selected_indices]
    #         selected_lithologies = [item.replace('✔️ ', '').strip() for item in select_lithologies]

    #         print(f"Selected column: {self.selected_column}")
    #         print(f"Selected rows: {selected_lithologies} (Type: {type(selected_lithologies[0]) if selected_lithologies else 'Empty'})")

    #         self.df_0[self.selected_column] = self.df_0[self.selected_column].astype(str).str.strip()

    #         print(f"Original DataFrame values in column {self.selected_column}: {self.df_0[self.selected_column].unique()}")

    #         # Create filtered DataFrame using the selected lithologies
    #         self.filtered_df = self.df_0[self.df_0[self.selected_column].isin(selected_lithologies)]

    #         item = None
    #         self.lithology_listbox.delete(0, tk.END)
    #         self.selected_items = {lithology: (lithology in selected_lithologies) for lithology in self.lithologies}
        
    #         for lithology, selected in self.selected_items.items():
    #             if selected:
    #                 item = "✔️ " + lithology
    #             else:
    #                 item = lithology
    #             self.lithology_listbox.insert(tk.END, item)
    
    #         def deselect_all():
    #             self.lithology_listbox.selection_clear(0, tk.END)
    
    #         self.lithology_listbox.bind('<Command-d>', lambda event: deselect_all())
    #         self.lithology_listbox.bind('<Control-d>', lambda event: deselect_all())

    #         if not selected_indices:
    #             self.lithologies_label = ctk.CTkLabel(self.selection_frame, text="No lithology selected:(", font=("Arial", 12))
    #             self.lithologies_label.grid(row=15, column=0, columnspan=4, padx=5, pady=(0,5))                   
    #     except:
    #         self.filtered_df = self.df_0

    #     # Cleaning Data Frame to contain only the data/elements
    #     filtered_columns = self.data_columns
    #     # filtered_columns = self.data_columns if self.data_columns is not None else [
    #     #     col for col in self.filtered_df.columns if '_ppm' in col or '_pct' in col
    #     # ]

    #     df_filtered = self.filtered_df.replace('<', '', regex=True)
    #     df_filtered[filtered_columns] = df_filtered[filtered_columns].apply(pd.to_numeric, errors='coerce')
    #     self.cleaned_df = df_filtered.dropna(subset=filtered_columns)
        
    #     df_filtered = self.cleaned_df[filtered_columns]

    #     self.cleaned_df.columns = self.cleaned_df.columns.str.strip().str.lower()

    #     self.df = df_filtered

    #     # Creating data frame with Rare Earth Elements
    #     self.df_c = self.df.copy()
    #     self.df_c.columns = self.df_c.columns.str.replace('_ppm', '').str.replace('_pct', '').str.replace('_Howell', '')
        
    #     LREE_elements = ['La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd']
    #     HREE_elements = ['Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
        
    #     LREE_elements_in_df = [element for element in LREE_elements if element in self.df_c.columns]
    #     HREE_elements_in_df = [element for element in HREE_elements if element in self.df_c.columns]
        
    #     if LREE_elements_in_df:
    #         self.df_c['LREE'] = self.df_c[LREE_elements_in_df].sum(axis=1)
        
    #     if HREE_elements_in_df:
    #         self.df_c['HREE'] = self.df_c[HREE_elements_in_df].sum(axis=1)
        
    #     if LREE_elements_in_df or HREE_elements_in_df:
    #         self.df_c['REE'] = self.df_c[LREE_elements_in_df + HREE_elements_in_df].sum(axis=1)

    #     self.output_text.insert("end", f"Filtered & Cleaned df:\n{self.df.shape}\n")
    #     self.perform_pca()

    def filter_dataframe(self):
        # delete previous labels
        for attr in ["scaler_label", "pca_label", "lithologies_label"]:
            if hasattr(self, attr) and getattr(self, attr) is not None:
                try:
                    getattr(self, attr).destroy()
                except Exception:
                    pass
                delattr(self, attr)

        if hasattr(self, "color_window") and self.color_window.winfo_exists():
            self.color_window.destroy()

        # set PCA/Kernel PCA label
        if self.pca_type_combo.get() == "PCA":
            self.pca_label = ctk.CTkLabel(
                self.selection_frame, text="PCA", font=("Arial", 12)
            )
        else:
            if self.kernel == "rbf":
                text = f"Kernel PCA-{self.kernel} ({self.gamma:.2f})"
            elif self.kernel == "poly":
                text = f"Kernel PCA-{self.kernel} ({self.gamma:.2f}, {self.degree:.1f}, {self.coef:.1f})"
            elif self.kernel == "sigmoid":
                text = f"Kernel PCA-{self.kernel} ({self.gamma:.2f}, {self.coef:.1f})"
            else:
                text = f"Kernel PCA-{self.kernel}"

            self.pca_label = ctk.CTkLabel(
                self.selection_frame, text=text, font=("Arial", 12)
            )

        self.pca_label.grid(row=14, column=0, columnspan=4, pady=(0, 5))

        # scaler label
        self.scaler_label = ctk.CTkLabel(
            self.selection_frame,
            text=f"Selected scaler: {self.scaler_combo.get()}",
            font=("Arial", 12),
            wraplength=200,
        )
        self.scaler_label.grid(row=13, column=0, columnspan=4, padx=5, pady=0)

        self.clear()
        self.current_button = None

        try:
            # selected groups/lithologies
            selected_indices = self.lithology_listbox.curselection()
            select_lithologies = [self.lithology_listbox.get(i) for i in selected_indices]
            selected_lithologies = [
                item.replace("✔️ ", "").strip()
                for item in select_lithologies
            ]

            print(f"Selected column: {self.selected_column}")
            print(f"Selected lithologies: {selected_lithologies}")

            # normalize selected column for comparison
            self.df_0[self.selected_column] = (
                self.df_0[self.selected_column]
                .astype(str)
                .str.strip()
            )

            # If no group selected, use all rows
            if selected_lithologies:
                self.filtered_df = self.df_0[
                    self.df_0[self.selected_column].isin(selected_lithologies)
                ].copy()
            else:
                self.filtered_df = self.df_0.copy()
                self.output_text.insert("end", "No group selected: using all rows.\n")

            # refresh listbox with check marks
            self.lithology_listbox.delete(0, tk.END)

            self.selected_items = {
                lithology: lithology in selected_lithologies
                for lithology in self.lithologies
            }

            for lithology, selected in self.selected_items.items():
                item = "✔️ " + lithology if selected else lithology
                self.lithology_listbox.insert(tk.END, item)

            if not selected_lithologies:
                self.lithologies_label = ctk.CTkLabel(
                    self.selection_frame,
                    text="No lithology selected: using all rows",
                    font=("Arial", 12),
                )
                self.lithologies_label.grid(
                    row=15, column=0, columnspan=4, padx=5, pady=(0, 5)
                )

        except Exception as e:
            print("Filtering by group failed:", e)
            self.filtered_df = self.df_0.copy()
            selected_lithologies = []

        # -------------------------------
        # Clean dataframe for PCA
        # -------------------------------

        if self.data_columns is None:
            self.output_text.insert("end", "No data columns selected.\n")
            return

        # Keep only geochemistry numeric columns
        filtered_columns = [
            col for col in self.data_columns
            if "_ppm" in str(col).lower() or "_pct" in str(col).lower()
        ]

        if not filtered_columns:
            self.output_text.insert(
                "end",
                "No ppm/pct numeric columns selected for PCA.\n"
            )
            return

        df_filtered = self.filtered_df.copy()

        # Clean values such as <0.01 and commas
        df_filtered[filtered_columns] = (
            df_filtered[filtered_columns]
            .replace(r"^\s*<\s*", "", regex=True)
            .replace(r",", "", regex=True)
            .apply(pd.to_numeric, errors="coerce")
        )

        print("Rows before filter:", len(self.df_0))
        print("Rows after group filter:", len(self.filtered_df))
        print("Filtered columns:", filtered_columns)

        # Drop rows missing any selected PCA variable
        self.cleaned_df = df_filtered.dropna(subset=filtered_columns).copy()

        if self.cleaned_df.empty:
            self.output_text.insert(
                "end",
                "No rows left after cleaning. Try selecting fewer elements or check missing values.\n"
            )
            return

        self.df = self.cleaned_df[filtered_columns].copy()

        # Lowercase metadata columns after PCA dataframe is created
        self.cleaned_df.columns = self.cleaned_df.columns.str.strip().str.lower()

        # Creating dataframe with Rare Earth Elements
        self.df_c = self.df.copy()
        self.df_c.columns = (
            self.df_c.columns
            .str.replace("_ppm", "", regex=False)
            .str.replace("_pct", "", regex=False)
            .str.replace("_Howell", "", regex=False)
        )

        LREE_elements = ["La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd"]
        HREE_elements = ["Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"]

        LREE_elements_in_df = [
            element for element in LREE_elements
            if element in self.df_c.columns
        ]
        HREE_elements_in_df = [
            element for element in HREE_elements
            if element in self.df_c.columns
        ]

        if LREE_elements_in_df:
            self.df_c["LREE"] = self.df_c[LREE_elements_in_df].sum(axis=1)

        if HREE_elements_in_df:
            self.df_c["HREE"] = self.df_c[HREE_elements_in_df].sum(axis=1)

        if LREE_elements_in_df or HREE_elements_in_df:
            self.df_c["REE"] = self.df_c[
                LREE_elements_in_df + HREE_elements_in_df
            ].sum(axis=1)

        self.output_text.insert("end", f"Filtered & Cleaned df:\n{self.df.shape}\n")

        self.perform_pca()
        
    def perform_pca(self):
        # Perform PCA and update output
        try:
            self.pca_instance = PCA_class(self.df, self.scaler_combo, self.pca_type_combo, self.output_text, self.slider, self.kernel_combo, self.gamma, self.degree, self.coef)
            self.pca_instance.get_variance_ratio()
            self.output_text.insert("end", f"PCA performed successfully. Shape of transformed data: {self.pca_instance.x.shape}\n")
            color_change.color_function(self)
            color_change.shape_map(self)
            self.editmenu.entryconfig("Edit Data Point Color/Shape", state="normal")
            self.group_titles()
            self.loading_graph()   
            self.terminal.register_to_scope('pca_instance', self.pca_instance)
            
        except Exception as e:
            self.output_text.insert("end", f"{e}\n")

    def group_titles(self):
        # Create labels for PCA and Cluster Analysis sections
        self.pca_list = ctk.CTkLabel(self.box_frame, text="PCA Analysis Graphs")
        self.pca_list.grid(row=0, column=0, columnspan=6, sticky="w", pady=(10,0), padx=5)
        
        self.cluster_list = ctk.CTkLabel(self.box_frame, text="Cluster Analysis")
        self.cluster_list.grid(row=2, column=2, columnspan=3, sticky="w", pady=(10,0), padx=(25,0))

        self.supervised_list = ctk.CTkLabel(self.box_frame, text="Supervised Learning")
        self.supervised_list.grid(row=4, column=0, columnspan=6, sticky="w", pady=(5,0), padx=5)

    # def loading(self):
    #     # Create loadings
    #     self.pca = self.pca_instance.pca

    #     if isinstance(self.pca, PCA):
    #         components = self.pca.components_

    #         self.loadings = pd.DataFrame(
    #             components.T,
    #             columns=['PC' + str(i) for i in range(1, components.shape[0] + 1)],
    #             index=self.df.columns
    #         )

    #     elif isinstance(self.pca, KernelPCA):
    #         # KernelPCA does not provide direct loadings like PCA
    #         Scaled_data = self.pca_instance.Scaled_data
    #         K = self.pca._get_kernel(Scaled_data, self.pca.X_fit_)  # Compute the kernel matrix
            
    #         # Use the eigenvectors to approximate loadings
    #         eigenvectors = self.pca.eigenvectors_
    #         loadings_approx = np.dot(K.T, eigenvectors)

    #         # Reshape to ensure the shape matches with the original features
    #         loadings_approx = loadings_approx.T
            
    #         # Compute the final loadings by taking the dot product with the original data
    #         loadings_final = np.dot(Scaled_data.T, loadings_approx.T)

    #         self.loadings = pd.DataFrame(
    #             loadings_final,
    #             columns=['PC' + str(i) for i in range(1, eigenvectors.shape[1] + 1)],
    #             index=self.df.columns
    #         )

    #     else:
    #         raise ValueError("self.pca must be an instance of PCA or KernelPCA")

    def loading(self):
        self.pca = self.pca_instance.pca

        if isinstance(self.pca, PCA):
            components = self.pca.components_

            self.loadings = pd.DataFrame(
                components.T,
                columns=[f"PC{i}" for i in range(1, components.shape[0] + 1)],
                index=self.df.columns
            )
            #HNG
            # Add aliases: 0 -> PC1, 1 -> PC2, etc.
            for i, col in enumerate(list(self.loadings.columns)):
                self.loadings[i] = self.loadings[col]

        elif isinstance(self.pca, KernelPCA):
            Scaled_data = self.pca_instance.Scaled_data
            K = self.pca._get_kernel(Scaled_data, self.pca.X_fit_)

            eigenvectors = self.pca.eigenvectors_
            loadings_approx = np.dot(K.T, eigenvectors)
            loadings_approx = loadings_approx.T
            loadings_final = np.dot(Scaled_data.T, loadings_approx.T)

            self.loadings = pd.DataFrame(
                loadings_final,
                columns=[f"PC{i}" for i in range(1, eigenvectors.shape[1] + 1)],
                index=self.df.columns
            )
            #HNG
            # Add aliases: 0 -> PC1, 1 -> PC2, etc.
            for i, col in enumerate(list(self.loadings.columns)):
                self.loadings[i] = self.loadings[col]

        else:
            raise ValueError("self.pca must be an instance of PCA or KernelPCA")
    
    def selection(self):
        # Create a combo box for selecting clustering methods and initiate the modules
        self.cluster_combo = ctk.CTkComboBox(
            self.box_frame, values=["K-mean", "Hierarchical", "DBSCAN", "Mean Shift", "Spectral", "GMM", "Affinity Propagation", "BIRCH"], width=100, height=20, command=self.update_cluster, state="readonly")

        self.cluster_combo.grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0), padx=5)
        self.cluster_combo.set("K-mean")
        self.cluster = self.cluster_combo.get()

        self.instance2d = Cluster2DPlotClass(self.shared_container, self.cluster, self.df_c, self.cleaned_df, self.box_frame, self.box_frame_sub, self.on_button_click, self.legend_frame, self.selected_column)
        self.instance3d = Cluster3DPlotClass(self.shared_container, self.cluster, self.df_c, self.cleaned_df, self.box_frame, self.box_frame_sub, self.on_button_click, self.legend_frame, self.selected_column)
        self.loading_cluster_instance = loading_cluster(self.shared_container, self.cluster, self.loadings, self.box_frame, self.box_frame_sub, self.on_button_click, self.apply_button, self.legend_frame)
        if "sample id" in self.cleaned_df.columns:  
            self.sample_cluster_instance = sample_cluster(self.shared_container, self.cluster, self.pca_df_scaled, self.df, self.cleaned_df, self.box_frame, self.box_frame_sub, self.on_button_click, self.apply_button, self.legend_frame)
        else:
            pass

    def update_cluster(self, *arg):
        # update cluster
        self.cluster = self.cluster_combo.get()
        self.instance2d.cluster_result = self.cluster
        self.instance3d.cluster_result = self.cluster
        self.loading_cluster_instance.cluster_result = self.cluster
        self.sample_cluster_instance.cluster_result = self.cluster

        # re-initiate cluster modules to refresh options in box_frame_sub
        for widget in self.box_frame_sub.winfo_children():
            if widget.winfo_name() == "size_combo_3d":
                self.instance3d.plot_3d_cluster_sub(self.cluster)  
                print("3d")
            elif widget.winfo_name() == "size_combo_2d":
                self.instance2d.plot_2d_cluster_sub(self.cluster)
                print("2d")
            elif getattr(widget, "custom_name", "") == "loading_check":
                self.loading_cluster_instance.plot_cluster_sub(self.cluster)  
                print("LC")
            elif getattr(widget, "custom_name", "") == "sample_check":
                self.sample_cluster_instance.plot_cluster_sub(self.cluster)  
                print("SC")
            else:
                pass

    def loading_graph(self):
        #preparing data
        self.loading()
        self.pca_df_scaled = self.pca_instance.pca_df_scaled
        self.pca_df_scaled.reset_index(drop=True, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.cleaned_df.reset_index(drop=True, inplace=True)
        self.df_c.reset_index(drop=True, inplace=True)

        # Initiate modules
        self.selection()
        loading_class(self.loadings, self.shared_container, self.box_frame, self.box_frame_sub, 
                    self.on_button_click, self.apply_button)
        class3d(self.shared_container, self.pca_df_scaled, self.df, self.cleaned_df, 
                self.box_frame, self.box_frame_sub, self.on_button_click, 
                self.apply_button, self.legend_frame, self.loadings, self.selected_column)
        class2d(self.shared_container, self.pca_df_scaled, self.df, self.cleaned_df, 
                self.box_frame, self.box_frame_sub, self.on_button_click, 
                self.apply_button, self.legend_frame, self.loadings, self.selected_column)
        supervised_learning(self.df, self.cleaned_df, self.on_button_click, 
                        self.apply_button, self.box_frame)
        
        image_path = 'images/icons/blank.png'
        pil_image = Image.open(image_path)
        self.icon_image = CTkImage(light_image=pil_image, dark_image=pil_image, size=(32, 32))

        if "sample id" in self.cleaned_df.columns:
            sample_class(self.shared_container, self.pca_df_scaled, self.df, self.cleaned_df,
                        self.box_frame, self.box_frame_sub, self.on_button_click, self.apply_button)
        else:
            print("Column Sample ID not in data frame, sample bar graph, and sample cluster bar graph not available") 
            blank_image_ = ctk.CTkLabel(self.box_frame, image=self.icon_image, text = "", width=20)
            blank_image_1 = ctk.CTkLabel(self.box_frame, image=self.icon_image, text = "", width=20)
            blank_image_.grid(row=3, column=1, sticky="w", pady=0, padx=5)
            blank_image_1.grid(row=1, column=1, sticky="w", pady=0, padx=5)

        try:
            depth_cols = self.cleaned_df.filter(like='depth').columns
            column_name = depth_cols[0]
            if "drillhole" in self.cleaned_df.columns and column_name in self.cleaned_df.columns:
                try:
                    drill_class(self.shared_container, self.pca_df_scaled, self.cleaned_df, 
                                self.df, self.box_frame, self.box_frame_sub, 
                                self.on_button_click, self.apply_button)
                except Exception as e:
                    print("DEBUG: drill_class threw an exception:", e)
            else:
                if "drillhole" not in self.cleaned_df.columns:
                    print("Column 'Drillhole' not in data frame, drill hole plot not available")
        except IndexError:
            print("Column 'Depth' not in data frame, drill hole plot not available")
            blank_image_2 = ctk.CTkLabel(self.box_frame, image=self.icon_image, text = "", width=20)
            blank_image_2.grid(row=1, column=4, sticky="w", pady=0, padx=5)

        self.save_pc_menu.entryconfig("Save PC by element excel", state=tk.NORMAL)
        if "sample id" in self.cleaned_df.columns:
            self.save_pc_menu.entryconfig("Save PC by sample excel", state=tk.NORMAL)
        
    def export_pc_by_sample(self):
        # Export PCA results by sample
        self.pca_df_scaled = self.pca_instance.pca_df_scaled
        self.pca_df_scaled.shape
        file_name = fd.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not file_name:
            return

        with pd.ExcelWriter(file_name, engine='openpyxl') as excel_writer:
            self.cleaned_df["sample id"].to_excel(excel_writer, sheet_name='Sheet1', index=False, header=True)
            self.pca_df_scaled.to_excel(excel_writer, sheet_name='Sheet1', startcol=1, index=False)
    
    def export_pc_by_element(self):
        # Export PCA loadings by element
        file_name = fd.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not file_name:
            return
        
        with pd.ExcelWriter(file_name, engine='openpyxl') as excel_writer:
            columns_df = pd.DataFrame(self.df.columns, columns=['Column Names'])
            columns_df.to_excel(excel_writer, sheet_name='Sheet1', index=False, header=True)
            self.loadings.to_excel(excel_writer, sheet_name='Sheet1', startcol=1, index=False)


def main():
    try:
        app = MainApp()
        app.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()






