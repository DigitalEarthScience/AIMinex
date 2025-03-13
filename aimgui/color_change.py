import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd

def update_ds_and_refresh_ui(selection, color_window, cleaned_df):
    global column_to_use, color_map1, ds
    column_to_use = selection

    # Clear the existing Rock Units section in the UI
    for widget in color_window.grid_slaves():
        if int(widget.grid_info()["column"]) in [4, 5, 6] and int(widget.grid_info()["row"]) > 0:
            widget.grid_forget()

    # Generate shape mapping for the newly selected column
    shape_index = cleaned_df[column_to_use].unique()

    # Recreate the shape map (similar to the shape_map function)
    shape_name_to_symbol = {
        "triangle": "^",
        "star": "*",
        "circle": "o",
        "square": "s",
        "diamond": "D",
        "pentagon": "p",
        "hexagon": "h",
        "octagon": "8",
        "plus": "+",
        "cross": "x",
        "inverse_triangle": "v",
        "thin_diamond": "d",
        "hourglass": "H",
        "triangle_left": "<",
        "triangle_right": ">",
        "horizontal_line": "_",
        "vertical_line": "|"
    }
    color_map1 = {}
    for i, shape in enumerate(shape_index):
        if i < len(shape_name_to_symbol):
            color_map1[shape] = list(shape_name_to_symbol.values())[i]
        else:
            color_map1[shape] = "^"  # Default shape if we run out of symbols
    
    # Update ds to match the unique shapes in the new column
    ds = pd.DataFrame()
    ds = cleaned_df[str(column_to_use)].str.strip().to_frame()
    ds = ds.rename(columns={ds.columns[0]: 'Shape'})
    ds["Shapes"] = ds["Shape"].map(color_map1)
    ds.reset_index(drop=True, inplace=True)


    # Rock Units Section
    rock_label = ctk.CTkLabel(color_window, text=column_to_use)
    rock_label.grid(row=1, column=4, padx=10, pady=10)

    shape_label = ctk.CTkLabel(color_window, text="Shape")
    shape_label.grid(row=1, column=5, padx=10, pady=10)

    shape_visual_label = ctk.CTkLabel(color_window, text="Selected Shape")
    shape_visual_label.grid(row=1, column=6, padx=10, pady=10)

    # Recreate the Rock Units Section based on the new column
    for idx, rock_unit in enumerate(shape_index):
        # Label for rock unit
        rock_label = ctk.CTkLabel(color_window, text=rock_unit)
        rock_label.grid(row=idx + 2, column=4, padx=10, pady=5)

        # Small rectangle to visualize the selected shape symbol
        rock_shape_visual = ttk.Label(color_window, text=color_map1.get(rock_unit, "^"))
        rock_shape_visual.grid(row=idx + 2, column=6, padx=10, pady=5)

        # Combobox for selecting shape symbol
        rock_shape_combo = ctk.CTkComboBox(
            color_window, 
            values=list(shape_name_to_symbol.keys()),
            state="readonly", 
            command=lambda selected_value, rock_unit=rock_unit, rock_shape_visual=rock_shape_visual: update_rock_shape_visual(selected_value, rock_unit, rock_shape_visual, shape_name_to_symbol)
        )
        rock_shape_combo.set(color_map1.get(rock_unit, "^"))  # Set default shape symbol
        rock_shape_combo.grid(row=idx + 2, column=5, padx=10, pady=5)



def open_color_window(self):
    global dc, ds, color_map, color_map1
    # Check if the window already exists and destroy it if it does
    if hasattr(self, 'color_window') and self.color_window.winfo_exists():
        self.color_window.destroy()

    # Create a new window for manual color editing
    self.color_window = tk.Toplevel(self)
    self.color_window.title("Edit Colors")
    self.color_window.geometry("1000x600")


    scrollable_frame = ctk.CTkScrollableFrame(self.color_window)
    scrollable_frame.pack(fill="both", expand=True)

    # Combobox to select the column for shape mapping
    column_label = ctk.CTkLabel(scrollable_frame, text="Define shape by")
    column_label.grid(row=0, column=4, padx=10, pady=10)

    color_label = ctk.CTkLabel(scrollable_frame, text='*Color Options from "Filter by" Column')
    color_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
    
    column_options = [col for col in self.cleaned_df.columns if '_ppm' not in col.lower() and '_pct' not in col.lower()]
    column_select_combo = ctk.CTkComboBox(
        scrollable_frame,
        values=column_options,
        state="readonly",
        command=lambda selection: update_ds_and_refresh_ui(selection, self.color_window, self.cleaned_df)
    )
    column_select_combo.set(column_to_use)
    column_select_combo.grid(row=0, column=5, padx=10, pady=10, columnspan=3, sticky="ew")

    # Lithologies Section
    lithology_label = ctk.CTkLabel(scrollable_frame, text=self.selected_column)
    lithology_label.grid(row=1, column=0, padx=10, pady=10)

    color_label = ctk.CTkLabel(scrollable_frame, text="Color")
    color_label.grid(row=1, column=1, padx=10, pady=10)

    visual_label = ctk.CTkLabel(scrollable_frame, text="Selected Color")
    visual_label.grid(row=1, column=2, padx=10, pady=10)

    # Generate the list of comboboxes for lithology color selection
    for idx, lithology in enumerate(self.lithologies):
        # Label for lithology
        litho_label = ctk.CTkLabel(scrollable_frame, text=lithology)
        litho_label.grid(row=idx + 2, column=0, padx=10, pady=5)

        # Small rectangle to visualize the selected color
        color_visual = ttk.Label(scrollable_frame, text="   ", background=color_map.get(str(lithology), "black"))
        color_visual.grid(row=idx + 2, column=2, padx=10, pady=5)

        # Combobox for selecting color
        color_combo = ctk.CTkComboBox(
            scrollable_frame, 
            values=[
                "lime", "green", "olive",
                "blue", "navy", "teal", "cyan", "turquoise", "indigo",
                "deeppink", "pink", "magenta", "violet", "lavender", "purple",
                "black", "grey", "darkgrey", "dimgrey", "lightgrey", "slategray", "darkslategray", "lightsteelgray", "gainsboro", "silver",
                "sienna", "brown", "beige", "maroon",
                "red", "orange", "coral", "gold", "yellow",
                "white"
            ], 
            state="readonly", 
            command=lambda selected_value, lithology=str(lithology), color_visual=color_visual: update_color_visual(selected_value, lithology, color_visual)
        )
        color_combo.set(color_map.get(str(lithology), "black"))
        color_combo.grid(row=idx + 2, column=1, padx=10, pady=5)
            
    # Rock Units Section
    rock_label = ctk.CTkLabel(scrollable_frame, text=column_to_use)
    rock_label.grid(row=1, column=4, padx=10, pady=10)
    
    shape_label = ctk.CTkLabel(scrollable_frame, text="Shape")
    shape_label.grid(row=1, column=5, padx=10, pady=10)
    
    shape_visual_label = ctk.CTkLabel(scrollable_frame, text="Selected Shape")
    shape_visual_label.grid(row=1, column=6, padx=10, pady=10)
    
    # Define a mapping between user-friendly names and symbols
    shape_name_to_symbol = {
        "triangle": "^",
        "star": "*",
        "circle": "o",
        "square": "s",
        "diamond": "D",
        "pentagon": "p",
        "hexagon": "h",
        "octagon": "8",
        "plus": "+",
        "cross": "x",
        "inverse_triangle": "v",
        "thin_diamond": "d",
        "hourglass": "H",
        "triangle_left": "<",
        "triangle_right": ">",
        "horizontal_line": "_",
        "vertical_line": "|"
    }

    self.shape_index = self.cleaned_df[column_to_use].unique()

    for idx, rock_unit in enumerate(self.shape_index):
        # Label for rock unit
        rock_label = ctk.CTkLabel(scrollable_frame, text=rock_unit)
        rock_label.grid(row=idx + 2, column=4, padx=10, pady=5)

        # Small rectangle to visualize the selected shape symbol
        rock_shape_visual = ttk.Label(scrollable_frame, text=color_map1.get(rock_unit, "^"))
        rock_shape_visual.grid(row=idx + 2, column=6, padx=10, pady=5)

        # Combobox for selecting shape symbol
        rock_shape_combo = ctk.CTkComboBox(
            scrollable_frame, 
            values=list(shape_name_to_symbol.keys()),
            state="readonly", 
            command=lambda selected_value, rock_unit=rock_unit, rock_shape_visual=rock_shape_visual: update_rock_shape_visual(selected_value, rock_unit, rock_shape_visual, shape_name_to_symbol)
        )
        rock_shape_combo.set(color_map1.get(rock_unit, "^"))  # Set default color or shape symbol
        rock_shape_combo.grid(row=idx + 2, column=5, padx=10, pady=5)

    # Apply Button to save the changes
    # apply_button = ctk.CTkButton(self.color_window, text="Apply Colors", command=lambda: apply_color_change(self))
    # apply_button.grid(row=max(len(self.lithologies), len(ds['Shape'].unique())) + 3, column=0, columnspan=7, stick = "ew", padx=10, pady=(10,0))

    label = ctk.CTkLabel(scrollable_frame, text="Redraw graphs to apply change")
    label.grid(row=max(len(self.lithologies), len(ds['Shape'].unique())) + 4, column=0, columnspan=7, stick = "ew", padx=10, pady=(0,10))


    
def update_color_visual(selected_value, lithology, color_visual):
    # Declare dc as global to access the global dataframe
    global dc, color_map
    
    # Update the rectangle color preview with the selected color
    color_visual.configure(background=selected_value)
    
    # Update the color map and global dc dataframe immediately
    color_map[lithology] = selected_value
    dc.loc[dc['Lithology'] == lithology, 'Color'] = selected_value

def update_rock_shape_visual(selected_shape_name, rock_unit, rock_shape_visual, shape_name_to_symbol):
    global ds, color_map1
    # Convert the selected name back to the corresponding symbol
    selected_symbol = shape_name_to_symbol.get(selected_shape_name)
    
    # Update the shape visualization (display the selected symbol)
    rock_shape_visual.configure(text=selected_symbol)
    
    # Update the shape map and global ds dataframe with the symbol, not the name
    color_map1[rock_unit] = selected_symbol
    ds.loc[ds['Shape'] == rock_unit, 'Shapes'] = selected_symbol



def color_function(self):
    global dc, color_map
    # Generate color mapping
    try:
        dc = pd.DataFrame()

        dc = self.cleaned_df[self.selected_column.lower()]
        dc = dc.to_frame()
        dc = dc.rename(columns={dc.columns[0]: 'Lithology'})
        
        color_list = dc['Lithology'].unique()
        default_colors = ["lime", "blue", "cyan", "deeppink", "pink", "black", "black", "black", "grey", "lightgrey"]
        color_map = {}
        # Populate the dictionary with symbols for each shape
        for i, color in enumerate(color_list):
            if i < len(default_colors):
                color_map[color] = default_colors[i]
            else:
                # If run out of default colors, map to a placeholder or a random color
                color_map[color] = "red"

        # color_map = {
        #     'Calcitic Marble': 'lime',
        #     'Dolomitic Marble': 'blue',
        #     'Di-Tr Dolomitic Marble': 'cyan',
        #     'Apatite Marble': 'deeppink',
        #     'Siliceous Calcitic Marble': 'steelblue',
        #     #'Carbonatite': 'deeppink',
        #     #'Carbonatite-Like': 'pink',
        
        #     'Syenite': 'black',
        #     'Altered Syenite': 'black',
        #     'Intrusion': 'black',
        #     'Skarn': 'sienna',
        #     'Syenite-Like': 'black',
        #     'Impure Siliciclastic': 'dimgrey',
        #     'Pure Siliciclastic': 'lightgrey',
        #     'Siliciclastic': 'grey'
            
        # }

        dc['Color'] = dc['Lithology'].map(color_map)
        dc.reset_index(drop=True, inplace=True)

    except Exception as e:
        color_map = {}
        dc = pd.DataFrame()
        self.output_text.insert("end", f"Error generating {self.selected_column}-color map: {e}\n")     
    
def shape_map(self):
    global ds, color_map1, column_to_use
    # Generate shape mapping for rock units
    try:
        if 'rock unit' in self.cleaned_df.columns:
            column_to_use = 'rock unit'
        else:
            column_to_use = next((col for col in self.cleaned_df.columns if '_ppm' not in col.lower() and '_pct' not in col.lower()), None)
        
        if column_to_use is None:
            raise ValueError("No suitable column found for shape mapping.")
        
        #self.cleaned_df = self.cleaned_df.applymap(lambda x: x.strip().lower() if isinstance(x, str) and pd.notnull(x) else x)
        self.cleaned_df = self.cleaned_df.apply(lambda col: col.map(lambda x: x.strip().lower() if isinstance(x, str) and pd.notnull(x) else x))

        ds = pd.DataFrame()
        ds = self.cleaned_df[str(column_to_use)]
        ds = ds.str.strip().to_frame()
        ds = ds.rename(columns={ds.columns[0]: 'Shape'})
        
        shape_list = ds['Shape'].unique()
        
        default_symbols = ["^", "*", "o", "s", "D"]
        color_map1 = {}
        # Populate the dictionary with symbols for each shape
        for i, shape in enumerate(shape_list):
            if i < len(default_symbols):
                color_map1[shape] = default_symbols[i]
            else:
                # If run out of default colors, map to a placeholder or a random color
                color_map1[shape] = "^"
            
        
        # color_map1 = {
        #     'Marble Units': "^",
        #     'Altered Intrusion': "*",
        #     'Siliciclastic': "o",
        #     'Intrusion': "s",
        #     'Anomalous Rock': "D",
        # }

        ds["Shapes"] = ds["Shape"].map(color_map1)
        ds.reset_index(drop=True, inplace=True)

    except Exception as e:
        color_map1 = {}
        ds = pd.DataFrame()
        self.output_text.insert("end", f"Error generating {column_to_use} shape map: {e}\n") 
        self.output_text.insert("end", f"Column {column_to_use} does not exist, or check error in name?\n") 
