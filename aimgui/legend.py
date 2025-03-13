import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .custom_toolbar import CustomToolbar
from matplotlib.lines import Line2D

def legend(self):
    # Create and display legends for lithology and rock type
    from . import color_change
    Legend = self.var1.get() == 1
    if Legend:
        for widget in self.legend_frame.winfo_children():
            widget.destroy()
        
        if not color_change.dc.empty and not color_change.ds.empty:
            unique_lithologies = self.cleaned_df[self.selected_column.strip().lower()].unique()
            
            from .color_change import column_to_use
            unique_shapes = self.cleaned_df[column_to_use.strip().lower()].unique()
    
            # For lithologies
            handle1 = []
            label1 = []
            #print (f"color_map{color_change.color_map}")
            for lithology in unique_lithologies:
                color = color_change.color_map[lithology.title()]
                l1 = Line2D([], [], color=color, marker='o', linestyle='None', markeredgewidth=1.5, label=lithology)
                handle1.append(l1)
                label1.append(lithology.title())
    
            # For shapes
            handle2 = []
            label2 = []
            #print (f"color_map1{color_change.color_map1}")
            for shape in unique_shapes:
                str(shape).strip().lower()
                marker = color_change.color_map1[shape]
                l2 = Line2D([], [], color='black', marker=marker, linestyle='None', markeredgewidth=1.5, label=shape)
                handle2.append(l2)
                label2.append(shape.title())
    
            total_entries = len(label1) + len(label2)
            height_per_entry = 0.19
            fig_height = total_entries * height_per_entry + 1

            if fig_height < 3.15:
                fig_height = 3.15
    
            figx = plt.figure(figsize=(3, fig_height), constrained_layout=True)
            axx = figx.add_subplot(111)
            axx.axis('off')

            self.legend1 = axx.legend(handle1, label1, loc='upper left', bbox_to_anchor=(0, 1), title=str(self.selected_column).title(), fontsize=10, labelspacing=0.3)

            # Get the bounding box of the first legend in axis coordinates
            figx.canvas.draw()
            renderer = figx.canvas.get_renderer()
            bbox = self.legend1.get_window_extent(renderer=renderer)

            bbox = bbox.transformed(axx.transAxes.inverted())

            second_legend_y = bbox.y0

            self.legend2 = axx.legend(handle2, label2, loc='upper left', bbox_to_anchor=(0, second_legend_y), title=str(column_to_use).title(), fontsize=10, labelspacing=0.3)
            axx.add_artist(self.legend1)
            axx.add_artist(self.legend2)

            self.canvas1 = FigureCanvasTkAgg(figx, master=self.legend_frame)
            toolbar = CustomToolbar(self.canvas1, self.legend_frame)
            toolbar.update()
            toolbar.pack(side=tk.TOP, fill=tk.X)
    
            self.canvas1.get_tk_widget().pack(fill="both", expand=True)
            self.legend_frame.update_idletasks()
            self.legend_frame._parent_canvas.yview_moveto(0)

            self.legend1.set_visible(self.var1.get() == 1)
            self.legend2.set_visible(self.var1.get() == 1)
        else:
            pass
    else:
        pass


