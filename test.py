import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

def visualize_online_csv(url, visualization_type="scatter"):
  """
  Fetches an online CSV file, analyzes data, and creates visualizations.

  Args:
      url (str): URL of the online CSV repository.
      visualization_type (str, optional): Type of visualization to create. Defaults to "scatter".
  """

  try:
    # Read the CSV data from the URL
    data = pd.read_csv(url)  # Fixed typo (added space after 'read')

    # Get basic information about the data
    print(f"Dataframe information:\n {data.info()}")

    # Explore data types and handle missing values (if any)
    print(f"\nData types:\n {data.dtypes}")
    data.fillna(data.mean(), inplace=True)  # Simple imputation for missing values (adjust based on data)

    # Descriptive statistics summary
    print(f"\nDescriptive statistics:\n {data.describe()}")

    # Correlation matrix (useful for scatter plots)
    correlation_matrix = data.corr()

    # Choose visualization type based on user input or data characteristics
    if visualization_type == "scatter":
      # Scatter plot with potential highlighting based on correlation
      if len(correlation_matrix.columns) > 2:  # Check for at least 3 columns
        # Find the pair with the highest correlation (excluding 1.0 for self-correlation)
        highest_correlation = correlation_matrix.abs().where(~np.tril(np.ones(correlation_matrix.shape)).astype(bool)).unstack().sort_values(ascending=False).head(1).index[0]
        x_col, y_col = highest_correlation
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=x_col, y=y_col, data=data)
        plt.title(f"Scatter Plot: {x_col} vs. {y_col}")
        plt.show()
      else:
        print("Scatter plot not suitable for data with less than 3 columns.")

    elif visualization_type == "bar":
      # Bar chart for categorical data or frequency distribution
      categorical_cols = [col for col in data.columns if data[col].dtype == object]
      if len(categorical_cols) > 0:
        # Example: bar chart for categorical data
        col = categorical_cols[0]
        plt.figure(figsize=(8, 6))
        sns.countplot(x=col, data=data)
        plt.title(f"Bar Chart: Count of {col}")
        plt.xticks(rotation=45)  # Rotate x-axis labels for readability
        plt.show()
      else:
        # Example: bar chart for frequency distribution
        data.hist(figsize=(10, 6))
        plt.title("Frequency Distribution")
        plt.show()

    # ... other visualization type logic (unchanged)

  except Exception as e:
    print(f"Error: {e}")

# Example usage with a public weather data CSV
url = "https://raw.githubusercontent.com/datasets/weather-stations/master/weather-stations.csv"
visualization_type = "scatter"  # Choose from 'scatter', 'bar', 'box', 'heatmap', or 'choropleth' 

visualize_online_csv(url, visualization_type)
