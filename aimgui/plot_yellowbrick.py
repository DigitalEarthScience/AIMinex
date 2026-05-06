import tkinter as tk
from yellowbrick.cluster import KElbowVisualizer  
from .custom_toolbar import CustomToolbar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def yellowbrick(self, X):
    # Create and display the KElbowVisualizer for clustering
    plt.rcParams.update({'font.size': 10})
    fig = plt.figure(figsize=(3, 3))
    ax = fig.add_subplot(111)
    ax.axis('off')
    #try:
    model = self.pipe.named_steps['model']
    if 'n_clusters' in model.get_params():
        del model.get_params()['n_clusters']

    # X = self.pca_df_scaled.values
    visualizer = KElbowVisualizer(model, k=(1, 9), timing=False, title="KElbowVisualizer").fit(X)

    visualizer.ax.set_yticklabels([])
    visualizer.finalize()
    fig.tight_layout()

    self.canvas1 = FigureCanvasTkAgg(fig, master=self.legend_frame)
    toolbar = CustomToolbar(self.canvas1, self.legend_frame)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)
    self.canvas1.get_tk_widget().pack(fill="both", expand=True)

    plt.close(fig)
    # except:
    #     pass


        
        # visualizer.ax.set_xlabel("")
        # visualizer.ax.set_ylabel("")
        # visualizer.ax.set_yticklabels([])
        # visualizer.ax.set_xticklabels([])



