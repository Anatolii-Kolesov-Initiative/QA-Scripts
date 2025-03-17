import os
import pandas as pd
import re
import math
import numpy as np

from datetime import datetime

## RUN SECOND, AFTER MMM_COLUMN_NAMES_CHECK_SCRIPT_2025

#specify files location here:
csv_directory = r'/Users/anatolii.kolesov/Downloads/MMM files Feb' #csv_directory = r'/Users/ayman.kassem-toufi/Downloads/Jan MMM File QA/Nov Files'


def sum_of_value(lis):
    SUM = 0
    for l in lis:
        if not pd.isnull(l):
            try:
                SUM += float(l)
            except:
                SUM = SUM
    return SUM


def extract_date_format_from_filename(filename):
    # Regex to extract date-like patterns from the file name
    matches = re.findall(r'(\d{2})(\d{2})(\d{4})', filename)
    if matches:
        # Assuming the file name contains dates in ddmmyyyy format
        return '%d%m%Y'
    return None



def validate_date_format(df, column_name, expected_formats=['%d/%m/%Y']):
    for expected_format in expected_formats:
        try:
            # Try converting the dates using the current format
            formatted_dates = pd.to_datetime(df[column_name], format=expected_format).dt.strftime(expected_format)
            df[column_name] = formatted_dates.fillna('NULL')
            print(f"All dates in column '{column_name}' were successfully converted to {expected_format}.")
            break  # Stop the loop if successful
        except Exception as e:
            print(f"Failed to process column '{column_name}' with format {expected_format}: {e}")

    if df[column_name].isnull().all():
        print(f"Some dates in column '{column_name}' were empty and have been filled with 'NULL'.")



# def validate_date_format(df, column_name, expected_format='%d/%m/%Y'):
#     # Attempt to convert and format the dates in the column to the expected European format
#     try:
#         # Convert dates; coerce errors to NaT (not-a-time)
#         formatted_dates = pd.to_datetime(df[column_name]).dt.strftime(expected_format)
        
#         # Replace NaT with 'NULL' and update the original column
# #         mask = df.applymap(lambda x: x == float('nan'))
# #         cols = df.columns[(mask).any()]
# #         for col in df[cols]:
# #             df.loc[mask[col], col] = 'NULL'
            
# #         df[column_name] = formatted_dates.fillna('NULL')
        
#         # Provide feedback on the processing status
#         if 'NULL' in df[column_name].values:
#             print(f"Some dates in column '{column_name}' were empty and have been filled with 'NULL'.")
#         else:
#             print(f"All dates in column '{column_name}' were successfully converted to {expected_format}.")
#     except Exception as e:
#         print(f"Error processing column '{column_name}': {e}")


def process_csv_files(folder_path):
    
    # Get current date to create a unique output folder
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_folder = os.path.join(folder_path, f"Output_{current_date}")
    
    # Create output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Loop through all files in the specified folder
    for filename in os.listdir(folder_path):
        print('--------------------------------------------------------------------------------------------------------')
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            try:
                # Read the CSV file
                df = pd.read_csv(file_path)
                
                # Print the filename and its column names
                print(f"File: {filename}")
                print("Column headers are:", df.columns.tolist())
                
                df.columns = df.columns.str.strip()
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                
                print("\n")
                print("Column headers after processing are:", df.columns.tolist())
                print("\n")
                print(df.dtypes)
                print("\n")
                print(df.head(5))
                print("\n")
                
                # Check for date columns using regex
                date_columns = [col for col in df.columns if re.search(r'date', col, re.I)]
                print("Date Columns:", date_columns)
                
                # Validate and format date columns if necessary
                date_formats = ['%d/%m/%Y', '%d/%m/%y']  # List of possible date formats
                for date_column_name in date_columns:
                    if date_column_name in df.columns:
                        validate_date_format(df, date_column_name, date_formats)
                        
                        if df[date_column_name].isnull().all():
                            # If the entire column is empty, leave it as is (no action needed)
                            pass  # This line is just a placeholder indicating no operation

                    
                    else:
                        print(f"Date column {date_column_name} not found.")
                    print(df.dtypes)
                
                # Flag empty rows and columns
                empty_rows = df[df.isnull().all(axis=1)]
                empty_columns = df.columns[df.isnull().all()]
                
                # Output findings
                print(f"Number of empty rows: {len(empty_rows)}")
                print(f"Number of empty columns: {len(empty_columns)}")
                if len(empty_columns) > 0:
                    print("Empty columns are:", empty_columns.tolist())
                    
                print("\n")
                
                # converting other columnn into appropriate dtypes:
                for col in df.columns:
                    if re.search(r'\b((?:GRPs?_)?Impressions?|CLICKS?)\b', col, re.I):
#                         df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                        df[col] = df[col].astype(str).str.replace(',', '').astype(float)
                    elif re.search(r'\b(CTC(?:\sINC\sVAT)?)\b', col, re.I):
                          # Convert the column to strings to ensure proper replacement
                        df[col] = df[col].astype(str)
                        # Remove the pound sign and commas
                        df[col] = df[col].replace({'£': '', ',': ''}, regex=True).str.strip()
                        # Convert to numeric, forcing non-convertible values to NaN
                        df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
                
                    elif re.search(r'\bCTR\b', col, re.I):
                        df[col] = df[col].replace(r'^[^\d.-]+', '', regex=True)
                        # Convert the cleaned strings to float, coerce errors, and fill NaN with 0
                        df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
                        # Unifying data format to one type of float instead of float and scientific
                        df[col] = df[col].apply(lambda x: f"{x:.5f}")

                        
                    elif re.search(r'\bcampaign(?:\sid)?\b', col, re.I):
#                         df[col] = df[col].fillna('NULL')
                        df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else x)
#                         df[col] = df[col].apply(lambda x: f"{int(float(x))}" if x.replace('.', '', 1).isdigit() else x)
                        
                    elif re.search(r'\bimpact(?:s)?\b', col, re.I):
                        df[col] = df[col].astype(str)
                        # Replace known non-numeric strings with NaN
                        df[col] = df[col].replace(['NOT ON ROUTE', 'Not on Route', 'n/a - NI panels not in Route'], np.nan)
                        # Remove commas from the strings
                        df[col] = df[col].str.replace(',', '')
                        # Convert to numeric, forcing non-convertible values to NaN
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                    elif re.search(r'\bAll\sAdult\sGRP(?:s)?|Target\sAudience\sGRP(?:s)?\b', col, re.I):
                        df[col] = df[col].astype(str)
                        # Replace known non-numeric strings with NaN
                        df[col] = df[col].replace(['NOT ON ROUTE', 'Not on Route', 'n/a - NI panels not in Route'], np.nan)
                        # Remove commas from the strings
                        df[col] = df[col].str.replace(',', '')
                        # Convert to numeric, forcing non-convertible values to NaN
                        df[col] = pd.to_numeric(df[col], errors='coerce')

                        
                    elif re.search(r'\bcirculation\b', col, re.I):
                        df[col] = df[col].astype(str).str.replace(',', '').astype(float)
                    
                    print(f"Processed {col} - new data type: {df[col].dtypes}")
                
                # Replace 'NULL', 'NA', 'null', 'na' with empty strings
                df = df.replace(['NULL', 'NA', 'null', 'na', 'N/A', 'N/a', 'n/A', 'n/a'], '')
                
                # removing all NULL rows:
                df = df[df.apply(sum_of_value, axis = 1) > 0]
                df = df[[col for col in df.columns if not col.startswith('Unnamed')]]
                for col in df.columns:
                    print(f"FINAL Processed {col} - new data type: {df[col].dtypes}")

                    

                # Save transformed data to a new CSV file
                output_file_path = os.path.join(output_folder, filename)
                df.to_csv(output_file_path, encoding='utf-8', index=False)
                
                print(f"Processed and saved: {output_file_path}")
                print("\n")  # New line for better readability between files


            except Exception as e:
                print(f"Failed to process {filename}: {e}")

#run the main function using the file directory specified at the top
process_csv_files(csv_directory)


