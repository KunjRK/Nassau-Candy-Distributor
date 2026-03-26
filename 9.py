import pandas as pd

# 1. Load the dataset
df = pd.read_csv('Nassau Candy Distributor.csv')

# 2. Validate and convert date formats
# Using dayfirst=True to match the DD-MM-YYYY format in the data
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')

# Remove rows where dates could not be parsed
df = df.dropna(subset=['Order Date', 'Ship Date'])

# 3. Calculate Lead Time and remove negative values
df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
df = df[df['Lead Time'] >= 0]

# 4. Handle missing shipment records and critical fields
# Standardize by dropping rows with crucial missing information
df = df.dropna(subset=['Ship Mode', 'Customer ID', 'Sales'])

# 5. Standardize geographic fields
geo_columns = ['Country/Region', 'City', 'State/Province', 'Postal Code', 'Region']
for col in geo_columns:
    if df[col].dtype == 'object':
        df[col] = df[col].astype(str).str.strip().str.title()

# 6. Remove duplicate rows
df = df.drop_duplicates()

# Save the final cleaned dataset
df.to_csv('Cleaned_Nassau_Candy_Distributor.csv', index=False)

print("Data Cleaning Complete. Saved to 'Cleaned_Nassau_Candy_Distributor.csv'.")