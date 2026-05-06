import tkinter as tk
from yellowbrick.cluster import KElbowVisualizer  
from .custom_toolbar import CustomToolbar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from yellowbrick.cluster import KElbowVisualizer, SilhouetteVisualizer

def yellowbrick(self, X):
    plt.rcParams.update({"font.size": 10})

    # -------------------------------
    # Elbow Plot in a new tab
    # -------------------------------    
    # Only use KElbowVisualizer for KMeans
    if getattr(self, "cluster_result", None) != "K-mean":
        print("KElbowVisualizer is only available for K-means clustering.")
        return

    fig = plt.figure(figsize=(3, 3))
    ax = fig.add_subplot(111)

    try:
        model = KMeans(
            random_state=42,
            n_init="auto"
        )

        visualizer = KElbowVisualizer(
            model,
            k=(2, 9),
            force_model=True,
            timing=False,
            title="KElbowVisualizer",
            ax=ax
        )

        visualizer.fit(X)
        visualizer.ax.set_yticklabels([])
        visualizer.finalize()
        fig.tight_layout()

        #self.canvas1 = FigureCanvasTkAgg(fig, master=self.legend_frame)
        # Create new tab
        self.shared_container.create_tab()

        # Get current tab content frame
        tab_frame, content_frame = self.shared_container.current_tab

        # Create plotting frame
        plot_frame = tk.Frame(content_frame)
        plot_frame.pack(fill="both", expand=True)

        # Plot canvas
        self.canvas1 = FigureCanvasTkAgg(fig, master=plot_frame)

        #toolbar = CustomToolbar(self.canvas1, self.legend_frame)
        toolbar = CustomToolbar(self.canvas1, plot_frame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True)

    except Exception as e:
        print(f"Yellowbrick plot failed: {e}")

    finally:
        plt.close(fig)

    # -------------------------------
    # Silhouette Plot in a new tab
    # -------------------------------

    fig2 = plt.figure(figsize=(5, 4))
    ax2 = fig2.add_subplot(111)

    model2 = KMeans(
        n_clusters=5,
        random_state=42,
        n_init=10
    )

    visualizer2 = SilhouetteVisualizer(
        model2,
        force_model=True,
        ax=ax2,
        title="Silhouette Plot"
    )

    visualizer2.fit(X)
    visualizer2.finalize()
    fig2.tight_layout()

    # Create new tab
    self.shared_container.create_tab()
    tab_frame, content_frame = self.shared_container.current_tab

    plot_frame2 = tk.Frame(content_frame)
    plot_frame2.pack(fill="both", expand=True)

    self.canvas2 = FigureCanvasTkAgg(fig2, master=plot_frame2)

    toolbar2 = CustomToolbar(self.canvas2, plot_frame2)
    toolbar2.update()
    toolbar2.pack(side=tk.TOP, fill=tk.X)

    self.canvas2.get_tk_widget().pack(fill="both", expand=True)

    plt.close(fig2)



