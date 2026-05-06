import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, IntVar
from customtkinter import CTkImage

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import MouseButton

from PIL import Image
from tktooltip import ToolTip
from . import color_change
from .legend import legend

class class3d:
    def __init__(self, shared_container, pca_df_scaled, df, cleaned_df, box_frame, box_frame_sub, on_button_click, apply_button, legend_frame, loadings, selected_column):
        # Initialize the 3D class with necessary parameters
        self.apply_button = apply_button
        self.shared_container = shared_container
        self.on_button_click = on_button_click
        self.pca_df_scaled = pca_df_scaled
        self.df = df
        self.cleaned_df = cleaned_df
        self.selected_column = selected_column

        self.loadings = loadings
        # Remove '_ppm' and '_pct' from the index of self.loadings
        self.loadings.index = self.loadings.index.str.replace('_ppm', '').str.replace('_pct', '')

        self.box_frame = box_frame
        self.box_frame_sub = box_frame_sub
        self.legend_frame = legend_frame
        self.var = IntVar()
        self.var1 = IntVar()
        self.var2 = IntVar()
        self.plot_3d()

    def plot_3d(self):
        # Create button for displaying 3D PCA biplot
        #script_dir = os.path.dirname(os.path.abspath(__file__))
        #image_path = os.path.join(script_dir, "images", "images_program", "cube-3d-svgrepo-com.png")
        image_path = 'images/icons/cube-3d-svgrepo-com.png'
        pil_image = Image.open(image_path)

        # resized_image = pil_image.resize((32, 32), Image.LANCZOS)
        self.icon_image = CTkImage(light_image=pil_image, dark_image=pil_image, size=(32, 32))
        
        self.image_button = ctk.CTkLabel(self.box_frame, image=self.icon_image, text="", width=20)
        self.image_button.grid(row=1, column=2, sticky="w", pady=0, padx=5)

        # Bind button click to plot_3d_sub function
        self.image_button.bind("<Button-1>", lambda event: self.on_button_click(self.image_button, self.plot_3d_sub))

        ToolTip(self.image_button, msg="PCA 3D Biplot")

    def plot_3d_sub(self):
        # Create UI for selecting PCA components and options for 3D plot
        for widget in self.box_frame_sub.winfo_children():
            widget.destroy()

        pc_options = [f'PC{i+1}' for i in range(len(self.pca_df_scaled.T))]

        # Dropdowns for selecting PCA components
        ctk.CTkLabel(self.box_frame_sub, text="Select X-Axis:").pack(side="top", padx=5, pady=(5, 0))
        self.pc1_combo = ttk.Combobox(self.box_frame_sub, values=pc_options, state="readonly")
        self.pc1_combo.current(0)
        self.pc1_combo.pack(side="top", padx=5, pady=(3, 0))

        ctk.CTkLabel(self.box_frame_sub, text="Select Y-Axis:").pack(side="top", padx=5, pady=(5, 0))
        self.pc2_combo = ttk.Combobox(self.box_frame_sub, values=pc_options, state="readonly")
        self.pc2_combo.current(1)
        self.pc2_combo.pack(side="top", padx=5, pady=(3, 0))

        ctk.CTkLabel(self.box_frame_sub, text="Select Z-Axis:").pack(side="top", padx=5, pady=(5, 0))
        self.pc3_combo = ttk.Combobox(self.box_frame_sub, values=pc_options, state="readonly")
        self.pc3_combo.current(2)
        self.pc3_combo.pack(side="top", padx=5, pady=(3, 0))

        #select element for data point size
        ctk.CTkLabel(self.box_frame_sub, text="Element for Data Point Size:").pack(side="top", padx=5, pady=(5, 0))
        columns_with_na = ["N/A"] + self.df.columns.tolist()
        self.size_combo = ttk.Combobox(self.box_frame_sub, values=columns_with_na)
        self.size_combo.set("N/A")
        self.size_combo.pack(side="top", padx=5, pady=(3, 5))
        
        # Checkbox for displaying shapes
        if not color_change.ds.empty:
            self.checkbox = ctk.CTkCheckBox(self.box_frame_sub, text="Display shape", variable=self.var)
            self.checkbox.pack(side="top", anchor="w", padx=5, pady=(3, 0))

        # Checkbox for displaying trendlines
        self.checkbox = ctk.CTkCheckBox(self.box_frame_sub, text="Display Trendlines", variable=self.var2)
        self.checkbox.pack(side="top", anchor="w", padx=5, pady=(3, 0))

        # Checkbox for displaying legend
        self.checkbox1 = ctk.CTkCheckBox(self.box_frame_sub, text="Display Legend", variable=self.var1)
        self.checkbox1.pack(side="top", anchor="w", padx=5, pady=(3, 0))

        # Listbox for eigenvectors
        ctk.CTkLabel(self.box_frame_sub, text="Plot Eigenvectors:").pack(side="top", padx=5, pady=(10, 0))
        self.multiselect_3d = tk.Listbox(self.box_frame_sub, selectmode=tk.MULTIPLE)
        self.multiselect_3d.pack(side="top", padx=5, pady=5)
        for names in self.df.columns.tolist():
            self.multiselect_3d.insert(tk.END, names)

        # Select all items in the listbox
        def select_all():
            self.multiselect_3d.selection_set(0, tk.END)       
            
        # Deselect all items in the listbox
        def deselect_all():
            self.multiselect_3d.selection_clear(0, tk.END)

        self.multiselect_3d.bind('<Command-a>', lambda event: select_all())
        self.multiselect_3d.bind('<Control-a>', lambda event: select_all())
        
        self.multiselect_3d.bind('<Command-d>', lambda event: deselect_all())
        self.multiselect_3d.bind('<Control-d>', lambda event: deselect_all())

        # Apply button to show the 3D plot
        self.apply_plot_3d = ctk.CTkButton(self.box_frame_sub, text="apply", command=self.show_shape)
        self.apply_plot_3d.pack(side="top", padx=5, pady=5)
        
        # Display message for clicking data point if 'sample id' column exists
        if "sample id" in self.cleaned_df.columns:
            ctk.CTkLabel(self.box_frame_sub, text="Click Data Point for\n Sample ID").pack(side="top", padx=5, pady=(5, 0))
        
        self.box_frame_sub.update_idletasks()

    def show_shape(self):
        # Show 3D PCA plot with selected components and options         
        if not self.shared_container.current_tab:
            self.shared_container.create_tab() #("3D Biplot")

        plt.close('all')
        content_frame = self.shared_container.current_tab[1]
        for widget in content_frame.winfo_children():
            widget.destroy()
        for widget in self.legend_frame.winfo_children():
            widget.destroy()

        pc1 = self.pc1_combo.get()
        pc2 = self.pc2_combo.get()
        pc3 = self.pc3_combo.get()

        fig = plt.figure(figsize=(11, 11))
        self.ax = fig.add_subplot(111, projection='3d')
        xdata = self.pca_df_scaled[pc1]
        ydata = self.pca_df_scaled[pc2]
        zdata = self.pca_df_scaled[pc3]

        canvas = FigureCanvasTkAgg(fig, master=content_frame)
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, content_frame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, in_=content_frame)

        
        # Plot the points with shapes and colors
        element_size = self.size_combo.get()
        self.shapes = []
        from .color_change import column_to_use
        if element_size == "N/A":
            if column_to_use is not None:
                for i in range(len(self.df)):
                    shape = self.ax.scatter3D(xdata[i], ydata[i], zdata[i], c=color_change.dc['Color'][i], marker=color_change.ds["Shapes"][i])
                    self.shapes.append(shape)

                self.dots = self.ax.scatter3D(xdata, ydata, zdata, c=color_change.dc['Color'])

            else:
                for i in range(len(self.df)):
                    shape = self.ax.scatter3D(xdata[i], ydata[i], zdata[i], c=color_change.dc['Color'][i])
                    self.shapes.append(shape)
                    
                self.dots = self.ax.scatter3D(xdata, ydata, zdata, c=color_change.dc['Color'])                        

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
            def size_for_zn(x):
                if x < 1000:
                    return 20
                elif 1000 <= x <= 9999:
                    return 70
                elif x > 10000:
                    return 110
                # return 20  # Default size if none of the conditions match
            
            # Apply size mapping logic
            if element_size == 'Zn_ppm':
                sizes = self.df[element_size].apply(size_for_zn)
            else:
                sizes = self.df[element_size].apply(lambda x: map_size(x, 20, 100))

            if column_to_use is not None:
                for i in range(len(self.df)):
                    shape = self.ax.scatter3D(xdata[i], ydata[i], zdata[i], c=color_change.dc['Color'][i], marker=color_change.ds["Shapes"][i], s=sizes[i]
                    )
                    self.shapes.append(shape)   
                self.dots = self.ax.scatter3D(xdata, ydata, zdata, c=color_change.dc['Color'], s=sizes)

            else:
                for i in range(len(self.df)):
                    shape = self.ax.scatter3D(xdata[i], ydata[i], zdata[i], c=color_change.dc['Color'][i], s=sizes[i]
                    )
                    self.shapes.append(shape)
                self.dots = self.ax.scatter3D(xdata, ydata, zdata, c=color_change.dc['Color'], s=sizes)   

        # Plot trendlines if selected
        def plot_trendlines_3d():
            trendline = self.var2.get() == 1
            if trendline:
                #from mpl_toolkits.mplot3d import Axes3D
                from sklearn.linear_model import LinearRegression
                lithology_groups = self.cleaned_df.groupby(self.selected_column.lower())
                for name, group in lithology_groups:
                    x = self.pca_df_scaled.loc[group.index, pc1]
                    y = self.pca_df_scaled.loc[group.index, pc2]
                    z = self.pca_df_scaled.loc[group.index, pc3]
                    
                    X = np.vstack((x, y)).T
                    Y = z
                    
                    model = LinearRegression().fit(X, Y)
                    
                    trend_x = np.linspace(x.min(), x.max(), 100)
                    trend_y = np.linspace(y.min(), y.max(), 100)
                    trend_z = model.predict(np.vstack((trend_x, trend_y)).T)
                    color = color_change.color_map.get(name)
                    
                    self.ax.plot(trend_x, trend_y, trend_z, linestyle='--', label=f"Trendline {name}", color=color)
        
        plot_trendlines_3d()

        # Display sample IDs on click if selected
        if "sample id" in self.cleaned_df.columns:
            description = self.cleaned_df["sample id"]
            self.annotations = {}
            self.selected_points = set()
            
            from mpl_toolkits.mplot3d import proj3d
            
            def add_annotation(ind, source):
                if source == self.dots:
                    index = ind["ind"][0]
                    pos = source.get_offsets()[index]
                    text = f"{description.iloc[index]}"
                else:
                    index = ind
                    x, y, _ = proj3d.proj_transform(self.pca_df_scaled.iloc[index][pc1], self.pca_df_scaled.iloc[index][pc2], self.pca_df_scaled.iloc[index][pc3], self.ax.get_proj())
                    pos = (x, y)
                    text = f"{description.iloc[index]}"

                offsets = [(20, 20), (-20, 20), (20, -20), (-20, -20), (40, 40), (-40, 40), (40, -40), (-40, -40)]
                
                for offset in offsets:
                    annot = self.ax.annotate(text, xy=pos, xytext=offset,
                                        textcoords="offset points",
                                        bbox=dict(boxstyle="round", fc="w"),
                                        arrowprops=dict(arrowstyle="->",),
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
                annot = self.annotations.pop(index, None)
                if annot:
                    annot.remove()
                self.selected_points.discard(index)
                fig.canvas.draw_idle()
            
            def update_annotations(event):
                for index, annot in self.annotations.items():
                    if index in self.selected_points:
                        x, y, _ = proj3d.proj_transform(self.pca_df_scaled.iloc[index][pc1], self.pca_df_scaled.iloc[index][pc2], self.pca_df_scaled.iloc[index][pc3], self.ax.get_proj())
                        annot.xy = (x, y)
                fig.canvas.draw_idle()
            
            def on_click(event):
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
            
            fig.canvas.mpl_connect("button_press_event", on_click)
            fig.canvas.mpl_connect("motion_notify_event", update_annotations)

        self.setups(pc1, pc2, pc3)
        self.shape()
        legend(self)

    def shape(self):
        # Toggle visibility of shapes in the plot
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

    def setups(self, pc1, pc2, pc3):
        # Set up 3D biplot with loadings
        show_names = self.loadings.index.tolist()
        indx = self.loadings.index.get_indexer(show_names)
        scale = 1

        xs = scale * self.loadings[pc1]
        ys = scale * self.loadings[pc2]
        zs = scale * self.loadings[pc3]

        plt.title(f"3D PCA Biplot")

        self.ax.set_xlabel(pc1)
        self.ax.set_ylabel(pc2)
        self.ax.set_zlabel(pc3)
        x_arr = np.zeros(len(self.loadings[pc1]))
        y_arr = z_arr = x_arr

        all_points = np.concatenate((xs, ys, zs))
        min_value = np.min(all_points)
        max_value = np.max(all_points)
        axis_range = [min_value, max_value]

        self.ax.plot([x_arr.any() + axis_range[0], x_arr.any() + axis_range[1]], [y_arr.any(), y_arr.any()], [z_arr.any(), z_arr.any()], color='k', linestyle='--')
        self.ax.plot([x_arr.any(), x_arr.any()], [y_arr.any() + axis_range[0], y_arr.any() + axis_range[1]], [z_arr.any(), z_arr.any()], color='k', linestyle='--')
        self.ax.plot([x_arr.any(), x_arr.any()], [y_arr.any(), y_arr.any()], [z_arr.any() + axis_range[0], z_arr.any() + axis_range[1]], color='k', linestyle='--')

        self.arrow_list = []
        for i, name in enumerate(self.df.columns):
            ip = self.df.columns.get_loc(name)
            arrow = self.ax.quiver(x_arr[ip], y_arr[ip], z_arr[ip], xs.iloc[ip], ys.iloc[ip], zs.iloc[ip], color='r', arrow_length_ratio=0.1, linewidth=0.5)
            self.arrow_list.append(arrow)

        self.namelist = []
        for i, names in enumerate(show_names):
            ip = indx[i]
            n = self.ax.text(xs.iloc[ip] + 0.02, ys.iloc[ip] + 0.02, zs.iloc[ip] + 0.02, names, fontsize='small')
            self.namelist.append(n)

        selected_indices = self.multiselect_3d.curselection()
        self.selected_items = [self.multiselect_3d.get(i) for i in selected_indices]
        self.findname_specific()
        self.ax.callbacks.connect('ylim_changed', lambda ax: self.update_quiver_3d(self.arrow_list))
        self.ax.callbacks.connect('xlim_changed', lambda ax: self.update_quiver_3d(self.arrow_list))
        self.ax.callbacks.connect('zlim_changed', lambda ax: self.update_quiver_3d(self.arrow_list))
        
    # Add this function to handle quiver arrow updates when the axes change for 3D plots
    def update_quiver_3d(self, arrow_list_3d):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        zlim = self.ax.get_zlim()
        
        arrow_scale = max(abs(xlim[1] - xlim[0]), abs(ylim[1] - ylim[0]), abs(zlim[1] - zlim[0])) / 0.5
        
        for arrow in arrow_list_3d:
            arrow.set_segments([arrow.U, arrow.V, arrow.W], scale=arrow_scale)


    def findname_specific(self):
        # Highlight selected names and arrows in the plot
        options = self.df.columns.tolist()
        for i in range(len(options[:])):
            if options[i] in self.selected_items:
                self.namelist[i].set_visible(True)
                self.arrow_list[i].set_visible(True)
            else:
                self.namelist[i].set_visible(False)
                self.arrow_list[i].set_visible(False)
