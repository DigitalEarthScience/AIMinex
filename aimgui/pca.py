import pandas as pd
import numpy as np

from sklearn.decomposition import PCA, KernelPCA
from sklearn.preprocessing import StandardScaler, FunctionTransformer

class PCA_class:
    def __init__(self, df, scaler_combo, pca_type_combo, output_text, slider, kernel_combo, gamma, degree, coef):
        # Initialize the PCA class with necessary parameters and perform PCA
        self.df = df
        self.gamma = gamma
        self.degree = degree
        self.coef = coef
        self.scaler_combo = scaler_combo
        self.pca_type_combo = pca_type_combo
        self.kernel_combo = kernel_combo
        self.output_text = output_text
        self.slider = slider
        self.perform_pca()
        self.bargraph_frame = None

    def perform_pca(self):
        # Perform scaling and PCA based on selected options
        try:
            pca_type = self.pca_type_combo.get()
            if pca_type == "PCA":
                if self.scaler_combo.get() == "Standard Scaler":
                    scaling = StandardScaler()
                elif self.scaler_combo.get() == "Logarithmic Scaler":
                    scaling = FunctionTransformer(np.log10, validate=True)
                else:
                    raise ValueError("Invalid scaler selected")
                
                scaling.fit(self.df)
                self.Scaled_data = scaling.transform(self.df)
                
                self.pca = PCA(n_components=int(self.slider.get()))
                self.pca.fit(self.Scaled_data)
                self.x = self.pca.transform(self.Scaled_data)
            
            elif pca_type == "Kernel PCA":
                kernel_type = self.kernel_combo.get()
                
                if self.scaler_combo.get() == "Standard Scaler":
                    scaling = StandardScaler()
                elif self.scaler_combo.get() == "Logarithmic Scaler":
                    scaling = FunctionTransformer(np.log10, validate=True)
                else:
                    raise ValueError("Invalid scaler selected")
                
                scaling.fit(self.df)
                self.Scaled_data = scaling.transform(self.df)
                
                self.pca = KernelPCA(
                    n_components=int(self.slider.get()),
                    kernel=kernel_type,
                    gamma=self.gamma,
                    degree=self.degree,
                    coef0=self.coef
                )
                self.pca.fit(self.Scaled_data)
                self.x = self.pca.transform(self.Scaled_data)
            
            else:
                raise ValueError("Invalid PCA type selected")
            
            self.create_pca_df()
        
        except Exception as e:
            self.output_text.insert("end", f'Error during PCA: {e}\n')
            raise

    def create_pca_df(self):  
        # Create a DataFrame for the PCA results
        if isinstance(self.pca, PCA):
            num_components = self.pca.n_components_
        elif isinstance(self.pca, KernelPCA):
            num_components = self.pca.n_components
        
        self.pca_df = pd.DataFrame(
            data=self.x, 
            columns=['PC'+str(i) for i in range(1, num_components+1)]
        )
        self.scale_pca()
        
    def scale_pca(self):
        # Scale the PCA results
        self.pca_df_scaled = self.pca_df.copy()
        scaler_df = self.pca_df[self.pca_df.columns]
        scaler = 1 / (scaler_df.max() - scaler_df.min())
        for index in scaler.index:
            self.pca_df_scaled[index] *= scaler[index]
    
    def get_variance_ratio(self):
        # Output the explained variance ratio for each principal component
        if isinstance(self.pca, PCA) and hasattr(self.pca, 'explained_variance_ratio_'):
            explained_variance_ratio = self.pca.explained_variance_ratio_
            for i, variance in enumerate(explained_variance_ratio, start=1):
                self.output_text.insert("end", f'Principal Component {i}: \n{variance:.2%} of variance\n')
        else:
            # Kernel PCA doesn't directly provide the explained variance ratio.
            # We estimate it from the eigenvalues.
            self.output_text.insert("end", "Kernel PCA doesn\'t directly provide the explained variance ratio.\n")
            self.output_text.insert("end", "We estimate them using the eigenvalues!\n")
            # Eigenvalues from the Kernel PCA
            eigenvalues = self.pca.eigenvalues_
            
            # Explained variance ratio
            explained_variance_ratio = eigenvalues / np.sum(eigenvalues)
            for i, variance in enumerate(explained_variance_ratio, start=1):
                self.output_text.insert("end", f'Principal Component {i}: \n{variance:.2%} of variance\n')
