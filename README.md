# llm
# llm
# llm
# llm
import pandas as pd

# Path to the CSV file
csv_file = "path/to/your/file.csv"

# Path to save the Excel file
excel_file = "path/to/your/file.xlsx"

# Read the CSV file
data = pd.read_csv(csv_file)

# Save to Excel file
data.to_excel(excel_file, index=False, engine='openpyxl')

print(f"CSV has been converted to Excel and saved at {excel_file}")
# llm2
