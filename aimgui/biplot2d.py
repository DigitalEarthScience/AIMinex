import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, IntVar
from customtkinter import CTkImage

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import MouseButton

from PIL import Image
from tktooltip import ToolTip
from . import color_change
from .legend import legend


class class2d:
    def __init__(self, shared_container, pca_df_scaled, df, cleaned_df, box_frame, box_frame_sub, on_button_click, apply_button, legend_frame, loadings, selected_column):
        # Initialize the 2D class with required parameters
        self.shared_container = shared_container
        self.pca_df_scaled = pca_df_scaled
        self.df = df
        self.cleaned_df = cleaned_df

        self.loadings = loadings
        # Remove '_ppm' and '_pct' from the index of self.loadings
        self.loadings.index = self.loadings.index.str.replace('_ppm', '').str.replace('_pct', '')

        self.box_frame = box_frame
        self.box_frame_sub = box_frame_sub
        self.legend_frame = legend_frame

        self.var = IntVar()
        self.var1 = IntVar()
        self.var2 = IntVar()
        self.on_button_click = on_button_click
        self.apply_button = apply_button
        self.selected_column = selected_column
        
        self.plot_2d()

    def plot_2d(self):
        # Load and display the 2D plot icon button
        #script_dir = os.path.dirname(os.path.abspath(__file__))
        #image_path = os.path.join(script_dir, "images", "images_program", "chart-scatterplot-svgrepo-com.png")
        image_path = 'images/icons/chart-scatterplot-svgrepo-com.png'
        pil_image = Image.open(image_path)

        self.icon_image = CTkImage(light_image=pil_image, dark_image=pil_image, size=(32, 32))
        
        # Create a label with the image button
        self.image_button = ctk.CTkLabel(self.box_frame, image=self.icon_image, text="", width=20)
        self.image_button.grid(row=1, column=3, sticky="w", pady=0, padx=5)
        
        # Bind the button click to the sub plot function
        self.image_button.bind("<Button-1>", lambda event: self.on_button_click(self.image_button, self.plot_2d_sub))

        ToolTip(self.image_button, msg="PCA 2D Biplot")

    def plot_2d_sub(self):
        # Clear any existing widgets in the sub-frame
        for widget in self.box_frame_sub.winfo_children():
            widget.destroy()

        # Options for selecting principal components
        pc_options = [f'PC{i+1}' for i in range(len(self.pca_df_scaled.T))]
        
        # Dropdown for selecting the first principal component
        ctk.CTkLabel(self.box_frame_sub, text="Select PC1:").pack(side="top", padx=5, pady=(5, 0))
        self.pc1_combo = ttk.Combobox(self.box_frame_sub, values=pc_options, state="readonly")
        self.pc1_combo.current(0)
        self.pc1_combo.pack(side="top", padx=5, pady=(3, 0))
        
        # Dropdown for selecting the second principal component
        ctk.CTkLabel(self.box_frame_sub, text="Select PC2:").pack(side="top", padx=5, pady=(5, 0))
        self.pc2_combo = ttk.Combobox(self.box_frame_sub, values=pc_options, state="readonly")
        self.pc2_combo.current(1)
        self.pc2_combo.pack(side="top", padx=5, pady=(3, 0))
        
        #select element for data point size
        ctk.CTkLabel(self.box_frame_sub, text="Element for Data Point Size:").pack(side="top", padx=5, pady=(5, 0))
        columns_with_na = ["N/A"] + self.df.columns.tolist()
        self.size_combo = ttk.Combobox(self.box_frame_sub, values=columns_with_na, state="readonly")
        self.size_combo.set("N/A")
        self.size_combo.pack(side="top", padx=5, pady=(3, 5))
        
        # Checkbox for displaying shapes
        if not color_change.ds.empty:
            self.checkbox = ctk.CTkCheckBox(self.box_frame_sub, text="Display shape", variable=self.var)
            self.checkbox.pack(side="top", anchor="w", padx=5, pady=(3, 0))

        # Checkbox for displaying trendlines
        self.checkbox2 = ctk.CTkCheckBox(self.box_frame_sub, text="Display Trendlines", variable=self.var2)
        self.checkbox2.pack(side="top", anchor="w", padx=5, pady=(3, 0))
        
        # Checkbox for displaying legend
        self.checkbox1 = ctk.CTkCheckBox(self.box_frame_sub, text="Display Legend", variable=self.var1)
        self.checkbox1.pack(side="top", anchor="w", padx=5, pady=(3, 0))

        # Multiselect listbox for selecting columns
        ctk.CTkLabel(self.box_frame_sub, text="Plot Eigenvectors:").pack(side="top", padx=5, pady=(10, 0))
        self.multiselect_2d = tk.Listbox(self.box_frame_sub, selectmode=tk.MULTIPLE, exportselection=False)
        self.multiselect_2d.pack(side="top", padx=5, pady=5)
        for names in self.df.columns.tolist():
            self.multiselect_2d.insert(tk.END, names)
            
        # Function to deselect all items in the listbox
        def select_all():
            self.multiselect_2d.selection_set(0, tk.END)
            
        # Function to deselect all items in the listbox
        def deselect_all():
            self.multiselect_2d.selection_clear(0, tk.END)

        # Bind Command-d (select all) to the listbox
        self.multiselect_2d.bind('<Command-a>', lambda event: select_all())
        self.multiselect_2d.bind('<Control-a>', lambda event: select_all())
        
        # Bind Command-d (deselect all) to the listbox
        self.multiselect_2d.bind('<Command-d>', lambda event: deselect_all())
        self.multiselect_2d.bind('<Control-d>', lambda event: deselect_all())

        # Apply button to show the 2D plot
        self.apply_plot_2d = ctk.CTkButton(self.box_frame_sub, text="apply", command=self.show_shape)
        self.apply_plot_2d.pack(side="top", padx=5, pady=5)
        
        # Display message for clicking data point if 'sample id' column exists
        if "sample id" in self.cleaned_df.columns:
            ctk.CTkLabel(self.box_frame_sub, text="Click Data Point for \n Sample ID").pack(side="top", padx=5, pady=(5, 0))
            
        self.box_frame_sub.update_idletasks()

    def show_shape(self):            
        if not self.shared_container.current_tab:
            self.shared_container.create_tab() #("2D Biplot")

        plt.close('all')
        content_frame = self.shared_container.current_tab[1]
        for widget in content_frame.winfo_children():
            widget.destroy()
        for widget in self.legend_frame.winfo_children():
            widget.destroy()
    
        pc1 = self.pc1_combo.get()
        pc2 = self.pc2_combo.get()
    
        xdata = self.pca_df_scaled[pc1]
        ydata = self.pca_df_scaled[pc2]
        
        fig = plt.figure(figsize=(10, 10))
        
        # Subplot grid
        fig.suptitle(f'2D PCA Biplot', fontsize=14)
        gs = fig.add_gridspec(5, 5, hspace=0.4, wspace=0.4)
        self.ax = fig.add_subplot(gs[1:5, 0:4])
        ax_box_x = fig.add_subplot(gs[0, 0:4], sharex=self.ax)
        ax_box_y = fig.add_subplot(gs[1:5, 4], sharey=self.ax)


        # Plot the points with shapes and colors
        element_size = self.size_combo.get()
        self.shapes = []
        from .color_change import column_to_use
        if element_size == "N/A":
            if column_to_use is not None:
                for i in range(len(self.df)):
                    shape = self.ax.scatter(xdata[i], ydata[i], c=color_change.dc['Color'][i], marker=color_change.ds["Shapes"][i])
                    self.shapes.append(shape)

                self.dots = self.ax.scatter(xdata, ydata, c=color_change.dc['Color'])

            else:
                for i in range(len(self.df)):
                    shape = self.ax.scatter(xdata[i], ydata[i], c=color_change.dc['Color'][i])
                    self.shapes.append(shape)
                    
                self.dots = self.ax.scatter(xdata, ydata, c=color_change.dc['Color'])                        

        else:
            # Try to get element_size column values for size mapping
            self.max_ele = self.df[element_size].max()
            self.min_ele = self.df[element_size].min()
            
            # Function to map element_size values to point sizes
            def map_size(x, new_min, new_max):
                old_min = self.min_ele
                old_max = self.max_ele
                return ((np.log(x + 1) - np.log(old_min + 1)) / (np.log(old_max + 1) - np.log(old_min + 1))) * (new_max - new_min) + new_min
                
            # New logic for zn
            # def size_for_zn(x):
            #     if x < 10000:
            #         return 20
            #     elif 10000 <= x <= 99999:
            #         return 70
            #     elif x > 100000:
            #         return 120
            #     else:
            #         raise Exception ("size zn")
            
            # # Apply size mapping logic
            # if element_size == 'Zn_ppm':
            #     sizes = self.df[element_size].apply(size_for_zn)
            # else:
            sizes = self.df[element_size].apply(lambda x: map_size(x, 20, 100))

            if column_to_use is not None:
                for i in range(len(self.df)):
                    shape = self.ax.scatter(xdata[i], ydata[i], c=color_change.dc['Color'][i], marker=color_change.ds["Shapes"][i], s=sizes[i]
                    )
                    self.shapes.append(shape)   
                self.dots = self.ax.scatter(xdata, ydata, c=color_change.dc['Color'], s=sizes)

            else:
                for i in range(len(self.df)):
                    shape = self.ax.scatter(xdata[i], ydata[i], c=color_change.dc['Color'][i], s=sizes[i]
                    )
                    self.shapes.append(shape)
                self.dots = self.ax.scatter(xdata, ydata, c=color_change.dc['Color'], s=sizes)   

        def plot_trendlines():
            # Plot trendlines for lithology groups
            trendline = self.var2.get() == 1
            if trendline: #and 'lithology' in self.cleaned_df.columns:
                #import statsmodels.api as sm
                lithology_groups = self.cleaned_df.groupby(self.selected_column.lower())
                for name, group in lithology_groups:
                    x = self.pca_df_scaled.loc[group.index, pc1]
                    y = self.pca_df_scaled.loc[group.index, pc2]
                    
                    color = color_change.color_map.get(name)
                    
                    sns.regplot(x=x, y=y, ax=self.ax, scatter=False, label=f"Trendline {name}", color=color, ci=25, line_kws={'linewidth': 1})
        
        # Call the plot_trendlines function if enabled
        plot_trendlines()

        if "sample id" in self.cleaned_df.columns:
            # Annotate sample IDs on click
            description = self.cleaned_df["sample id"]
            self.annotations = {}
            self.selected_points = set()
            
            def add_annotation(ind, source):
                if source == self.dots:
                    index = ind["ind"][0]
                    pos = source.get_offsets()[index]
                    text = f"{description.iloc[index]}"
                else:
                    index = ind
                    pos = (self.pca_df_scaled.iloc[index][pc1], self.pca_df_scaled.iloc[index][pc2])
                    text = f"{description.iloc[index]}"
            
                offsets = [(20, 20), (-20, 20), (20, -20), (-20, -20), (40, 40), (-40, 40), (40, -40), (-40, -40)]
                
                # Try different annotation positions to avoid overlap
                for offset in offsets:
                    annot = self.ax.annotate(text, xy=pos, xytext=offset,
                                        textcoords="offset points",
                                        bbox=dict(boxstyle="round", fc="w"),
                                        arrowprops=dict(arrowstyle="->"),
                                        zorder=100)
                    fig.canvas.draw()
                    bbox = annot.get_window_extent()
                    overlap = False
                    for existing_annot in self.annotations.values():
                        existing_bbox = existing_annot.get_window_extent()
                        if bbox.overlaps(existing_bbox):
                            overlap = True
                            annot.remove()
                            break
                    if not overlap:
                        annot.set_visible(True)
                        self.annotations[index] = annot
                        self.selected_points.add(index)
                        fig.canvas.draw_idle()
                        return 
            
                # If all positions overlap, place annotation in the default position
                annot = self.ax.annotate(text, xy=pos, xytext=offsets[0],
                                    textcoords="offset points",
                                    bbox=dict(boxstyle="round", fc="w"),
                                    arrowprops=dict(arrowstyle="->"),
                                    zorder=100)
                annot.set_visible(True)
                self.annotations[index] = annot
                self.selected_points.add(index)
                fig.canvas.draw_idle()
            
            def remove_annotation(index):
                # Remove annotation from the plot
                annot = self.annotations.pop(index, None)
                if annot:
                    annot.remove()
                self.selected_points.discard(index)
                fig.canvas.draw_idle()
            
            def update_annotations(event):
                # Update annotation positions on mouse move
                for index, annot in self.annotations.items():
                    if index in self.selected_points:
                        annot.xy = (self.pca_df_scaled.iloc[index][pc1], self.pca_df_scaled.iloc[index][pc2])
                fig.canvas.draw_idle()
            
            def on_click(event):
                # Handle mouse click to add or remove annotations
                if event.inaxes == self.ax and event.button == MouseButton.LEFT:
                    contains_dots, ind_dots = self.dots.contains(event)
                    contains_shapes = False
                    shape_index = None
                    for i, shape in enumerate(self.shapes):
                        contains_shapes, ind_shapes = shape.contains(event)
                        if contains_shapes:
                            shape_index = i
                            break
                    
                    if contains_dots:
                        index = ind_dots["ind"][0]
                        if index in self.selected_points:
                            remove_annotation(index)
                        else:
                            add_annotation(ind_dots, self.dots)
                    elif contains_shapes:
                        if shape_index in self.selected_points:
                            remove_annotation(shape_index)
                        else:
                            add_annotation(shape_index, shape)
            
            # Connect event handlers for clicking and moving the mouse
            fig.canvas.mpl_connect("button_press_event", on_click)
            fig.canvas.mpl_connect("motion_notify_event", update_annotations)

        #if 'lithology' in self.cleaned_df.columns:
        # Create and display box plots for lithology
        filtered_df = self.cleaned_df.copy()
        
        xdata_filtered = self.pca_df_scaled.loc[filtered_df.index, pc1]
        ydata_filtered = self.pca_df_scaled.loc[filtered_df.index, pc2]

        palette = list(color_change.color_map.values())
        
        sns.boxplot(
            x=xdata_filtered, 
            y=filtered_df[self.selected_column.lower()], 
            hue=filtered_df[self.selected_column.lower()],
            ax=ax_box_x, 
            palette=palette, 
            orient='h',
            legend=False
        )
        sns.boxplot(
            y=ydata_filtered, 
            x=filtered_df[self.selected_column.lower()], 
            hue=filtered_df[self.selected_column.lower()],
            ax=ax_box_y, 
            palette=palette, 
            orient='v',
            legend=False
        )

        # Customize tick parameters for the box plots
        ax_box_x.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        ax_box_x.tick_params(axis='y', labelsize=8, left=False, right=True, labelleft=False, labelright=True)

        ax_box_y.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
        ax_box_y.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)

        ax_box_x.set_ylabel(None)
        ax_box_x.set_xlabel(None)
        
        ax_box_y.set_ylabel(None)
        ax_box_y.set_xlabel(None)

        self.ax.axvline(x=0, color='black', linewidth=0.5)
        self.ax.axhline(y=0, color='black', linewidth=0.5)

        # Create and display the plot canvas and toolbar
        canvas = FigureCanvasTkAgg(fig, master=content_frame)
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, content_frame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, in_=content_frame)
        
        # Setup additional plot features
        self.setups(pc1, pc2)
        self.shape()
        legend(self)

    def shape(self):
        # Show or hide shapes based on checkbox selection
        try:
            shape = self.var.get() == 1
            if shape:
                for shape in self.shapes:
                    shape.set_visible(True)
                self.dots.set_visible(False)
            else:
                self.dots.set_visible(True)
                for shape in self.shapes:
                    shape.set_visible(False)
        except:
            self.dots.set_visible(True)
            

    def setups(self, pc1, pc2):
        # Setup for 2D biplot with arrows and labels for loadings
        show_names = self.loadings.index.tolist()
        indx = self.loadings.index.get_indexer(show_names)
        
        self.xs = self.loadings[pc1]
        self.ys = self.loadings[pc2]

        self.arrow_list_2d = []
        
        self.x_arr = np.zeros(len(self.loadings[pc1]))
        self.y_arr = self.x_arr

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        arrow_scale = max(xlim[1] - xlim[0], ylim[1] - ylim[0])
        
        for i, name in enumerate(self.df.columns):
            ip = self.df.columns.get_loc(name)
            arrow_2d = self.ax.quiver(self.x_arr[ip], self.y_arr[ip], self.xs.iloc[ip], self.ys.iloc[ip], color='r', scale=arrow_scale, width=0.002)
            self.arrow_list_2d.append(arrow_2d)
        
        namelist_2d = []
        for i, names in enumerate(show_names):
            ip = indx[i]
            n = self.ax.text((1 / arrow_scale) * self.xs.iloc[ip], (1 / arrow_scale) * self.ys.iloc[ip], names, fontsize='small', ha='center', va='center')
            namelist_2d.append(n)

        selected_indices = self.multiselect_2d.curselection()
        self.selected_items = [self.multiselect_2d.get(i) for i in selected_indices]
        self.findname_specific_2d(namelist_2d)
        
        self.ax.set_xlabel(pc1)
        self.ax.set_ylabel(pc2)
        #self.ax.set_title(f"{pc1} vs {pc2}")
        self.prev_xlim = self.ax.get_xlim()
        self.prev_ylim = self.ax.get_ylim()
        
        # Connect to 'draw_event' to track canvas redraws
        self.ax.figure.canvas.mpl_connect('draw_event', self.on_draw_event)
        
    def on_draw_event(self, event):
        # Get the current axis limits
        curr_xlim = self.ax.get_xlim()
        curr_ylim = self.ax.get_ylim()
    
        # Check if the axis limits have changed
        if curr_xlim != self.prev_xlim or curr_ylim != self.prev_ylim:
            # Update the quiver arrows if the limits have changed
            self.update_quiver()
    
            # Save the current limits as the previous limits
            self.prev_xlim = curr_xlim
            self.prev_ylim = curr_ylim
    
    def update_quiver(self):
        # Store the current visibility state of the arrows
        arrow_visibility = [arrow.get_visible() for arrow in self.arrow_list_2d]
    
        # Clear old quivers
        for arrow in self.arrow_list_2d:
            arrow.remove()
    
        # Get the current axis limits
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
    
        # Calculate the appropriate scale for arrows
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
    
        arrow_scale = max(x_range, y_range)
    
        # Recreate the quivers with updated scale
        self.arrow_list_2d.clear()
        for i, name in enumerate(self.df.columns):
            ip = self.df.columns.get_loc(name)
            arrow_2d = self.ax.quiver(self.x_arr[ip], self.y_arr[ip], self.xs.iloc[ip], self.ys.iloc[ip], color='r', scale=arrow_scale, width=0.002)
            arrow_2d.set_visible(arrow_visibility[i])
            self.arrow_list_2d.append(arrow_2d)
    
        # Redraw the canvas to reflect changes
        self.ax.figure.canvas.draw_idle()


    def findname_specific_2d(self, namelist_2d):
        # Show or hide specific names and arrows based on user selection
        options = self.df.columns.tolist()
        for i in range(len(options[:])):
            if options[i] in self.selected_items:
                namelist_2d[i].set_visible(True)
                self.arrow_list_2d[i].set_visible(True)
            else:
                namelist_2d[i].set_visible(False)
                self.arrow_list_2d[i].set_visible(False)
