import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, scrolledtext, Menu
from tkinter import *
from tkinter import filedialog as fd
from customtkinter import CTkImage
from tkinter import PanedWindow

import pandas as pd
import numpy as np

from sklearn.decomposition import PCA, KernelPCA

from PIL import Image
import webbrowser
import os
import platform

from .terminal import MATerminal
from .pca import PCA_class
from .supervised import supervised_learning
from .tab import SharedContainer
from .loadings import loading_class
from .loading_cluster import loading_cluster
from .sample import sample_class
from .sample_cluster import sample_cluster
from .drill import drill_class
from .biplot2d import class2d
from .biplot3d import class3d
from .cluster2d import Cluster2DPlotClass
from .cluster3d import Cluster3DPlotClass
from .about import show_about
from . import color_change


class MainApp(ctk.CTk):   
    def __init__(self):
        super().__init__()
        self.title("MinexAI")
        #setting logo
        logo_dir = os.path.dirname(os.path.abspath(__file__))
        if platform.system() == 'Windows':
            logo_path = os.path.join(logo_dir, 'images', 'images_program', 'logo.ico')
            self.iconbitmap(logo_path)
        else:
            logo_path = os.path.join(logo_dir, 'images', 'images_program', 'logo.png')
            logo = tk.PhotoImage(file=logo_path)
            self.iconphoto(False, logo)

        ctk.set_appearance_mode("Light")
        style = ttk.Style()
        style.theme_use("default")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        self.geometry(f"{screen_width}x{screen_height}")
        self.filtered_df = pd.DataFrame()
        self.box_frame_sub_visible = True
        self.create_widgets()

        # Set application color scheme
        system_select_bg = self.option_get('selectBackground', '')

        if not system_select_bg:
            system_select_bg = 'LightSkyBlue1'
        
        self.tk_setPalette(background='white', foreground='black', selectBackground=system_select_bg, activeForeground='black')

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
            relief="flat"
        )
        self.output_text.pack(fill="both", expand=True)

        menubar = Menu(self)
        self.filemenu = Menu(menubar, tearoff=0)

        # Create file menu options
        self.filemenu.add_command(label="Open File", command=self.load_data)
        self.filemenu.add_command(label="New Tab", command=lambda: self.shared_container.create_tab())
        self.filemenu.entryconfig("New Tab", state=tk.DISABLED)
        
        self.save_pc_menu = tk.Menu(self.filemenu, tearoff=0)
        
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
        self.editmenu = Menu(menubar, tearoff=0)
        self.editmenu.add_command(label="Edit Data Point Color/Shape", command=lambda: color_change.open_color_window(self), state="disabled")

        menubar.add_cascade(label="Edit", menu=self.editmenu)

        # Create help menu options
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=self.open_help_html)
        helpmenu.add_separator()
        helpmenu.add_command(label="Short-Cuts:", command=None)
        helpmenu.add_command(label="Deselect_all", command=None, accelerator="Cmd+d")
        helpmenu.add_separator()
        helpmenu.add_command(label="About...", command=show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.config(menu=menubar)
        
        #initialize terminal
        self.terminal = MATerminal(self.output_text, self)

        #make sure color matches during night
        style = ttk.Style()
        style.map('TCombobox', 
        fieldbackground=[('readonly', 'white')],
        background=[('readonly', 'lightgrey')])


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
            self.output_text.insert("end", f"Error loading file: \n")

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
            
            for widget in self.selection_frame.winfo_children():
                widget.destroy()
            
        except Exception as e:
            self.output_text.insert("end", f"Error loading sheet: {str(e)}\n")
        
        self.process_sheet()

    def process_sheet(self):
        # Create widgets to select scaler/pca type, and column to use to filter data. 
        valid_columns = [col for col in self.df_0.columns if '_ppm' not in col and '_pct' not in col] #["None(include ALL)"]+

        self.scaler_combo = ctk.CTkComboBox(self.selection_frame, values=["Standard Scaler", "Logarithmic Scaler"], state="readonly")
        self.scaler_combo.set("Standard Scaler")
        self.pca_type_combo = ctk.CTkComboBox(self.selection_frame, values=["PCA", "Kernel PCA"], command=self.kernelstat, state="readonly")
        self.pca_type_combo.set("PCA")
        self.slider = ctk.CTkSlider(self.selection_frame, from_=1, to=8, number_of_steps=7, command=self.on_slider_change)
        self.slider.set(6)

        if valid_columns:
            ctk.CTkLabel(self.selection_frame, text="Filter by:").grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5,0))
            self.selected_column_combobox = ctk.CTkComboBox(self.selection_frame, values=valid_columns, state="readonly", command = self.update_listbox)
            self.selected_column_combobox.grid(row=0, column=2, columnspan=3, sticky="we", padx=5, pady=(5,0))
            self.selected_column_combobox.set(valid_columns[0])

        else:
            self.output_text.insert("end", "No valid columns found in dataframe\n")

        self.update_listbox()

    def update_listbox(self, event=None):
        # create listbox containing unique groups in select column to filter (lithology stands for unique group/name)
        self.selected_column = self.selected_column_combobox.get()

        # if self.selected_column == "None(include ALL)":
        #     self.create_buttons()
        if self.selected_column:
            self.df_0[self.selected_column] = self.df_0[self.selected_column].apply(lambda x: x.strip().lower().title() if isinstance(x, str) and pd.notnull(x) else x)
            self.lithology_listbox = tk.Listbox(self.selection_frame, selectmode=tk.MULTIPLE)
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
        self.lithology_listbox.grid(row=1, column=0, columnspan=4, sticky="we", padx=5, pady=(5,0))
        
        def deselect_all():
            self.lithology_listbox.selection_clear(0, tk.END)
            
        self.lithology_listbox.bind('<Command-d>', lambda event: deselect_all())
        self.lithology_listbox.bind('<Control-d>', lambda event: deselect_all())

        self.create_buttons()

    def create_buttons(self):
        # Pack PCA and scaling options widgets
        self.current_button = None
        
        self.scaler_combo.grid(row=2, column=0, columnspan=4, sticky="we", padx=5, pady=(5,0))
  
        self.pca_type_combo.grid(row=3, column=0, columnspan=4, sticky="we", padx=5, pady=(5,0))

        ctk.CTkLabel(self.selection_frame, text="Number of PCA Components:").grid(row=8, column=0, columnspan=4, sticky="we", padx=5, pady=(5,0))

        self.slider.grid(row=9, column=0, columnspan=4, padx=10, pady=0)
        self.label = ctk.CTkLabel(self.selection_frame, text=f"Current value: {int(self.slider.get())}")
        self.label.grid(row=10, column=0, columnspan=4, padx=5, pady=0)

        # initiate widgets for kernal parameters
        self.gamma_slider = ctk.CTkSlider(self.selection_frame, from_=0, to=1, width=120, command=self.gamma_change)
        self.degree_slider = ctk.CTkSlider(self.selection_frame, from_=0, to=10, width=120, command=self.degree_change)
        self.coef_slider = ctk.CTkSlider(self.selection_frame, from_=0, to=10, width=120, command=self.coef_change)
        
        self.label1 = ctk.CTkLabel(self.selection_frame, text=f"Gamma: {self.gamma_slider.get():.2f}")
        self.label2 = ctk.CTkLabel(self.selection_frame, text=f"Degree: {self.degree_slider.get():.2f}")
        self.label3 = ctk.CTkLabel(self.selection_frame, text=f"Coef: {self.coef_slider.get():.2f}")

        # set defaults and configure
        filtered_columns = [col for col in self.df_0.columns if '_ppm' in col or '_pct' in col]
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
        self.kernel_combo = ctk.CTkComboBox(self.selection_frame, values=["linear", "poly", "rbf", "sigmoid", "cosine", "precomputed"], command=self.kernel_param, state="readonly")
        self.kernel_text = ctk.CTkLabel(self.selection_frame, text="Kernel:")
        self.kernel_combo.set("linear")

        self.apply_button = ctk.CTkButton(self.selection_frame, text="Apply", command= self.filter_dataframe)
        self.apply_button.grid(row=11, column=0, columnspan=4, padx=5, pady=(0,5))

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
            self.gamma_slider.grid(row=5, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label1.grid(row=5, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)

        elif self.kernel == "poly":
            self.gamma_slider.grid(row=5, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label1.grid(row=5, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)
            
            self.degree_slider.grid(row=6, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label2.grid(row=6, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)

            self.coef_slider.grid(row=7, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label3.grid(row=7, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)

        elif self.kernel == "sigmoid":
            self.gamma_slider.grid(row=5, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label1.grid(row=5, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)
            
            self.coef_slider.grid(row=5, column=1, columnspan=3, sticky="e", padx=(10,0), pady=0)
            self.label3.grid(row=5, column=0, sticky="w", columnspan=2, padx=(10,0), pady=0)

        else:
            pass
                
    def kernelstat(self, *args):
        # Show kernel options if Kernel PCA is selected
        pca_type = self.pca_type_combo.get()
        if pca_type == "Kernel PCA":
            self.kernel_combo.grid(row=4, column=1, columnspan=3, sticky="we", padx=5, pady=(5,0))
            self.kernel_text.grid(row=4, column=0, sticky="w", padx=(10,0), pady=(5,0))
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

    def filter_dataframe(self):   
        # delete previous labels
        if hasattr(self, 'scaler_label') and self.scaler_label is not None:
            self.scaler_label.destroy()
            del self.scaler_label
            
        if hasattr(self, 'pca_label') and self.pca_label is not None:
            self.pca_label.destroy()
            del self.pca_label

        if hasattr(self, 'color_window') and self.color_window.winfo_exists():
            self.color_window.destroy()

        if hasattr(self, 'lithologies_label') and self.lithologies_label is not None:
            self.lithologies_label.destroy()
            del self.lithologies_label

        #set PCA/Kernel PCA parameters
        if self.pca_type_combo.get() == "PCA":
            self.pca_label = ctk.CTkLabel(self.selection_frame, text="PCA", font=("Arial", 12))
            
        if self.pca_type_combo.get() == "Kernel PCA":
            if self.kernel == "rbf":
                self.pca_label = ctk.CTkLabel(self.selection_frame, text= f"Kernel PCA-{self.kernel} ({self.gamma:.2f})", font=("Arial", 12))  
            elif self.kernel == "poly":
                self.pca_label = ctk.CTkLabel(self.selection_frame, text= f"Kernel PCA-{self.kernel} ({self.gamma:.2f}, {self.degree:.1f}, {self.coef:.1f})", font=("Arial", 12))  
            elif self.kernel == "rbf":
                self.pca_label = ctk.CTkLabel(self.selection_frame, text= f"Kernel PCA-{self.kernel} ({self.gamma:.2f}, {self.coef:.1f})", font=("Arial", 12))  
            else:
                self.pca_label = ctk.CTkLabel(self.selection_frame, text= f"Kernel PCA-{self.kernel}", font=("Arial", 12)) 
                
        self.pca_label.grid(row=13, column=0, columnspan=4, pady=(0,5))
            
        if self.scaler_combo.get() == "Select PCA Scaler:":
            self.scaler_label = ctk.CTkLabel(self.selection_frame, text="Select a Scaler", font=("Arial", 12))
            self.scaler_label.grid(row=12, column=0, columnspan=4, padx=5, pady=0)
            return
        else:
            # self.scaler_label.grid_forget()
            self.scaler_label = ctk.CTkLabel(self.selection_frame, text= f"Selected scaler: {self.scaler_combo.get()}", font=("Arial", 12))
            self.scaler_label.grid(row=12, column=0, columnspan=4, padx=5, pady=0)
   
        self.clear()
        self.current_button = None

        #Filter/process dataframe based on selected lithology and parameters
        try:
            # Find selected lithologies(unique groups) and add check mark to them
            selected_indices = self.lithology_listbox.curselection()

            select_lithologies = [self.lithology_listbox.get(i) for i in selected_indices]
            selected_lithologies = [item.replace('✔️ ', '').strip() for item in select_lithologies]

            print(f"Selected column: {self.selected_column}")
            print(f"Selected rows: {selected_lithologies} (Type: {type(selected_lithologies[0]) if selected_lithologies else 'Empty'})")

            self.df_0[self.selected_column] = self.df_0[self.selected_column].astype(str).str.strip()

            print(f"Original DataFrame values in column {self.selected_column}: {self.df_0[self.selected_column].unique()}")

            # Create filtered DataFrame using the selected lithologies
            self.filtered_df = self.df_0[self.df_0[self.selected_column].isin(selected_lithologies)]

            item = None
            self.lithology_listbox.delete(0, tk.END)
            self.selected_items = {lithology: (lithology in selected_lithologies) for lithology in self.lithologies}
        
            for lithology, selected in self.selected_items.items():
                if selected:
                    item = "✔️ " + lithology
                else:
                    item = lithology
                self.lithology_listbox.insert(tk.END, item)
    
            def deselect_all():
                self.lithology_listbox.selection_clear(0, tk.END)
    
            self.lithology_listbox.bind('<Command-d>', lambda event: deselect_all())
            self.lithology_listbox.bind('<Control-d>', lambda event: deselect_all())

            if not selected_indices:
                self.lithologies_label = ctk.CTkLabel(self.selection_frame, text="No lithology selected:(", font=("Arial", 12))
                self.lithologies_label.grid(row=14, column=0, columnspan=4, padx=5, pady=(0,5))                   
        except:
            self.filtered_df = self.df_0

        # Cleaning Data Frame to contain only the data/elements
        filtered_columns = [col for col in self.filtered_df.columns if '_ppm' in col or '_pct' in col]

        df_filtered = self.filtered_df.replace('<', '', regex=True)
        df_filtered[filtered_columns] = df_filtered[filtered_columns].apply(pd.to_numeric, errors='coerce')
        self.cleaned_df = df_filtered.dropna(subset=filtered_columns)
        
        df_filtered = self.cleaned_df[filtered_columns]

        self.cleaned_df.columns = self.cleaned_df.columns.str.strip().str.lower()

        self.df = df_filtered

        # Creating data frame with Rare Earth Elements
        self.df_c = self.df.copy()
        self.df_c.columns = self.df_c.columns.str.replace('_ppm', '').str.replace('_pct', '').str.replace('_Howell', '')
        
        LREE_elements = ['La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd']
        HREE_elements = ['Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
        
        LREE_elements_in_df = [element for element in LREE_elements if element in self.df_c.columns]
        HREE_elements_in_df = [element for element in HREE_elements if element in self.df_c.columns]
        
        if LREE_elements_in_df:
            self.df_c['LREE'] = self.df_c[LREE_elements_in_df].sum(axis=1)
        
        if HREE_elements_in_df:
            self.df_c['HREE'] = self.df_c[HREE_elements_in_df].sum(axis=1)
        
        if LREE_elements_in_df or HREE_elements_in_df:
            self.df_c['REE'] = self.df_c[LREE_elements_in_df + HREE_elements_in_df].sum(axis=1)

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
            self.expand_buttons()
            self.loading_graph()   
            self.terminal.register_to_scope('pca_instance', self.pca_instance)
            
        except ValueError as e:
            self.output_text.insert("end", f"{e}\n")

    def expand_buttons(self):
        # Create labels for PCA and Cluster Analysis sections
        self.pca_list = ctk.CTkLabel(self.box_frame, text="PCA Analysis Graphs")
        self.pca_list.grid(row=0, column=0, columnspan=6, sticky="w", pady=(10,0), padx=5)
        
        self.cluster_list = ctk.CTkLabel(self.box_frame, text="Cluster Analysis")
        self.cluster_list.grid(row=2, column=2, columnspan=3, sticky="w", pady=(10,0), padx=(25,0))

        self.supervised_list = ctk.CTkLabel(self.box_frame, text="Supervised Learning")
        self.supervised_list.grid(row=4, column=0, columnspan=6, sticky="w", pady=(5,0), padx=5)

    def loading(self):
        # Create loadings
        self.pca = self.pca_instance.pca

        if isinstance(self.pca, PCA):
            components = self.pca.components_

            self.loadings = pd.DataFrame(
                components.T,
                columns=['PC' + str(i) for i in range(1, components.shape[0] + 1)],
                index=self.df.columns
            )

        elif isinstance(self.pca, KernelPCA):
            # KernelPCA does not provide direct loadings like PCA
            Scaled_data = self.pca_instance.Scaled_data
            K = self.pca._get_kernel(Scaled_data, self.pca.X_fit_)  # Compute the kernel matrix
            
            # Use the eigenvectors to approximate loadings
            eigenvectors = self.pca.eigenvectors_
            loadings_approx = np.dot(K.T, eigenvectors)

            # Reshape to ensure the shape matches with the original features
            loadings_approx = loadings_approx.T
            
            # Compute the final loadings by taking the dot product with the original data
            loadings_final = np.dot(Scaled_data.T, loadings_approx.T)

            self.loadings = pd.DataFrame(
                loadings_final,
                columns=['PC' + str(i) for i in range(1, eigenvectors.shape[1] + 1)],
                index=self.df.columns
            )

        else:
            raise ValueError("self.pca must be an instance of PCA or KernelPCA")
    
    def selection(self):
        # Create a combo box for selecting clustering methods and initiate the modules
        self.cluster_combo = ctk.CTkComboBox(
            self.box_frame, values=["K-mean", "Hierarchical", "DBSCAN", "Mean Shift", "Spectral", "GMM", "Affinity Propagation", "BIRCH"], width=100, height=20, command=self.update_cluster, state="readonly")

        self.cluster_combo.grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0), padx=5)
        self.cluster_combo.set("K-mean")
        self.cluster = self.cluster_combo.get()

        self.instance2d = Cluster2DPlotClass(self.shared_container, self.cluster, self.df_c, self.cleaned_df, self.box_frame, self.box_frame_sub, self.on_button_click, self.legend_frame)
        self.instance3d = Cluster3DPlotClass(self.shared_container, self.cluster, self.df_c, self.cleaned_df, self.box_frame, self.box_frame_sub, self.on_button_click, self.legend_frame)
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
        # preparing data
        self.loading()
        self.pca_df_scaled = self.pca_instance.pca_df_scaled
        self.pca_df_scaled.reset_index(drop=True, inplace=True)

        self.df.reset_index(drop=True, inplace=True)
        self.cleaned_df.reset_index(drop=True, inplace=True)
        self.df_c.reset_index(drop=True, inplace=True)

        # Initiate modules
        self.selection()
        loading_class(self.loadings, self.shared_container, self.box_frame, self.box_frame_sub, self.on_button_click, self.apply_button)
        class3d(self.shared_container, self.pca_df_scaled, self.df, self.cleaned_df, self.box_frame, self.box_frame_sub, self.on_button_click, self.apply_button, self.legend_frame, self.loadings, self.selected_column)
        class2d(self.shared_container, self.pca_df_scaled, self.df, self.cleaned_df, self.box_frame, self.box_frame_sub, self.on_button_click, self.apply_button, self.legend_frame, self.loadings, self.selected_column)
        supervised_learning(self.df, self.cleaned_df, self.on_button_click, self.apply_button, self.box_frame)
                    
        column_name = self.cleaned_df.filter(like='depth').columns[0]
        if "drillhole" in self.cleaned_df.columns and column_name in self.cleaned_df.columns:
            drill_class(self.shared_container, self.pca_df_scaled, self.cleaned_df, self.df, self.box_frame, self.box_frame_sub, self.on_button_click, self.apply_button)
        else:
            print("Column Drillhole or Depth not in data frame, drill hole plot not avaliable")
            image_button2 = ctk.CTkLabel(self.box_frame, image=self.icon_image, text = "", width=20)
            image_button2.grid(row=1, column=4, sticky="w", pady=0, padx=5)

        if "sample id" in self.cleaned_df.columns:
            sample_class(self.shared_container, self.pca_df_scaled, self.df, self.cleaned_df, self.box_frame, self.box_frame_sub, self.on_button_click, self.apply_button)
        else:
            print("Column Sample ID not in data frame, sample bar graph, and sample cluster bar graph not avaliable")
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, "images", "images_program", "blank.png")
            pil_image = Image.open(image_path)
            self.icon_image = CTkImage(light_image=pil_image, dark_image=pil_image, size=(32, 32))
    
            image_button = ctk.CTkLabel(self.box_frame, image=self.icon_image, text = "", width=20)
            image_button1 = ctk.CTkLabel(self.box_frame, image=self.icon_image, text = "", width=20)
            image_button.grid(row=3, column=1, sticky="w", pady=0, padx=5)
            image_button1.grid(row=1, column=1, sticky="w", pady=0, padx=5)

            
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






