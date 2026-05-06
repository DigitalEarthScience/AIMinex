Functions and Methods
=====================
This program offers two primary categories of plotting functions: Principal Component Analysis (PCA) and Data Clustering. There are two types of PCA (Normal and Kernel) and various clustering methods. Class prediction is also available under the Supervised Learning section.
For more information on the differences between the PCAs and types of clustering methods, please click on the links below:

| :doc:`PCA vs KernelPCA <pca>`, :doc:`Clustering Methods <clustering>` 

Plotting Functions:
---------------------
a) PCA Functions
    .. image:: ../images/doc/pca_functions.png
        :width: 100%
        
  1. PC Bar Graph by elements:
        This function creates and displays bar graphs for each PC component by elements. The class supports sorting and grouping elements, the user can select specific elements to group and plot together, and when Sort Label is selected, each of the selected groups is sorted based on their PC values for each PC component.

        | Steps:
        
        | i. Select elements to group
       
        .. image:: ../images/doc/ele1.png
            :width: 100%
        
        | ii. Select group/s to plot  
        
        .. image:: ../images/doc/ele2.png
            :width: 100%

  2. PC Bar Graph by samples:
        | Similar to PC Bar Graph by elements, this function graphs a bar graph for each PC component and displays the value for the Samples instead of the elements.

        | This Function is responsible for creating and displaying Principal Component Analysis (PCA) bar graphs by samples. It initializes with necessary parameters, sets up the UI for selecting PCA graph options, and updates plots based on user selections. The class uses normalization techniques for color scaling and leverages Matplotlib for plotting the bar charts.

        .. image:: ../images/doc/sam.png
            :width: 100%

  3. PCA 3D Biplot
        | The 3D Biplot displays 3D PCA biplots of the selected PC axis. The class supports displaying shapes (lithology classification of the data points), trendlines, legends, and provides interactive annotations for sample IDs on click. The data points represent the associated sample data and the optional quivers are the associated eigenvalues for the elements.

        | #The length of the quivers represents the variant in the elements.

        .. image:: ../images/doc/3db.png
            :width: 100%

  4. PCA 2D Biplot
        | Similar to the 3D Biplot, the 2D Biplot displays 2D PCA biplots of the selected PC axis, extra features include sets of box plots on each axis displaying the variance in the data and the outliers (The coloured section represents 50% of the data, and the center line inside the coloured part represents the median point).

        .. image:: ../images/doc/2db.png
            :width: 100%

        | Box Plot :

        .. image:: ../images/doc/boxplot.png
            :width: 100%

  5. Drill Hole Depth Chart
        | The Drill Hole depth chart displays PC charts with PCA data for each drill hole and their associated samples, ordered in depth. It processes and visualizes the depth data for different drill holes, allowing the user to select a specific drill hole and plot the PCA scatter plots along with the depth chart. 

        .. image:: ../images/doc/dh.png
            :width: 100%

        | *Note:column Depth and Drillhole are required for this function*

b) Clustering Function

    .. image:: ../images/doc/cluster_functions.png
        :width: 100%

  Before diving into the different plotting functions, it's important to understand the different types of clustering methods available.
  Some clustering methods allow the user to select the number of clusters; these methods include K-means, Hierarchical, Spectral, Gaussian Mixture Model (GMM), and BIRCH. Users can choose the number of clusters based on recommendations from tools like Yellowbrick(for more detail click :doc:`here <yellowbrick>`) or decide independently.
  On the other hand, some clustering methods automatically determine the optimal number of clusters; including DBSCAN, Mean-Shift, and Affinity Propagation.
  For more information on the different clustering methods and their processing logic, click :doc:`here <clustering>`.
  #data saving is available for all clustering functions, for more information on the steps click :doc:`here <save_excel>`.

  1. PC Cluster BarGraph by elements 
        | This function performs clustering analysis on PCA loadings (PC Bar Graph by elements) and displays the results as bar graphs by elements. The class supports multiple clustering techniques and uses Yellowbrick to visualize the optimal number of clusters when the number of clusters needs to be manually determined.

        .. image:: ../images/doc/elecbg.png
            :width: 100%    

  2. PC Cluster BarGraph by Samples
        | The PC Cluster BarGraph by Samples function performs clustering analysis on PCA-transformed data and displays the results as bar graphs by samples. This class supports multiple clustering techniques and uses Yellowbrick to visualize the optimal number of clusters when the number of clusters needs to be manually determined.

        .. image:: ../images/doc/samcbg.png
            :width: 100%  

  3. 3D Element-Sample Cluster Plots
        | The Cluster3DPlotClass is designed to create and display 3D cluster plots based on selected axes and clustering algorithms. The class provides functionalities for customizing the plot, such as displaying shapes and colouring by clusters, and includes an interactive feature to show annotations on data points. 

        .. image:: ../images/doc/3dc.png
            :width: 100%  

  4. 2D Element-Sample Cluster Plots
        | This class plots a 2D cluster plot that allows users to select different elements as axes, apply different clustering algorithms, and visualize the results using mesh grids for background contours.
        
        .. image:: ../images/doc/2dc.png
            :width: 100%  

c) Supervised Learnings

    .. image:: ../images/doc/supervised_icon.png
        :width: 100%

  Supervised learning is a category of machine learning that uses labelled datasets to train algorithms/models to predict outputs and observe patterns; it is commonly used for classification tasks and data predictions. 

  1. Supervised Learnings-Data Prediction
        | The Data Prediction function uses element values as the input (X) data to predict the category (e.g., lithology) that each sample belongs to. This program uses the SVC and Random Forest classifier from the Scikit learn library and incorporates commonly used parameters to enhance performance (for more details, visit `SVC <https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html>`_ or `Random Forest <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html>`_ ). Users can either manually input data or upload an Excel sheet to extract the data from, provided it follows the correct format (see step iiib). *Note: Only columns with specified/inputted values are used for model training.*

        | Steps:

        | i) Select Model

        .. image:: ../images/doc/spv1.png
            :width: 100%

        | ii) Adjust parameters and select the column to predict. (Original Parameters set to default setting)

        .. image:: ../images/doc/spv2.png
            :width: 100%

        | iii)  Input data manually or by importing an Excel Sheet

            a) Manually: Click on the plus button to create new rows for input data

                .. image:: ../images/doc/spv3a.png
                    :width: 100%
            
            b) Import Excel: Upload an Excel file with the correct format (see below)

                .. image:: ../images/doc/spv3b.png
                    :width: 100%
            
            Sample Excel Spread-Sheet:

                .. image:: ../images/doc/test.png
                    :width: 100%
            
        | iv) Input/modify data and predict

        .. image:: ../images/doc/spv4.png
            :width: 100%            

        | v) View prediction at the bottom. Column names that don't match in the original Excel file will be excluded and printed as a warning.

        .. image:: ../images/doc/spv5.png
            :width: 100%     

