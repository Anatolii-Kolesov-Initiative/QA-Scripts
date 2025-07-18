import os
import pandas as pd
import re
import csv
import numpy as np
from datetime import datetime 
from datetime import timedelta

################# WIP script combining MMM_columns_name_check_script_2025 & MMM_data_type_check_script_v2
# templates: https://interpublic-my.sharepoint.com/personal/ayman_kassem-toufic_initiative_com/_layouts/15/onedrive.aspx?csf=1&web=1&e=ekIQcp&CID=6b398471%2De431%2D4e1b%2Db7ae%2D0ccbee706f7d&id=%2Fpersonal%2Fayman%5Fkassem%2Dtoufic%5Finitiative%5Fcom%2FDocuments%2FNatwest%2FNatwest%20MMM%20Data%2F2025%2FGold%20Star%20Templates&FolderCTID=0x0120000A6605C59EE50740AFBBC7EAE6A969B4&view=0&noAuthRedirect=1

# prompt for the file path:
directory_path = input("Please enter the path to the CSV files: ")


# alternatively, specify the local directory with the files
#directory_path = r'C:\Users\anatolii.kolesov\Downloads\Feb MMM files' #directory_path = r'/Users/ayman.kassem-toufi/Downloads/Jan MMM File QA/Nov Files'


def sum_of_value(lis):
    SUM = 0
    for l in lis:
        if not pd.isnull(l):
            try:
                SUM += float(l)
            except:
                SUM = SUM
    return SUM

def validate_date_format(df, column_name, expected_formats=['%d/%m/%Y']):
    for expected_format in expected_formats:
        try:
            formatted_dates = pd.to_datetime(df[column_name], format=expected_format).dt.strftime(expected_format)
            df[column_name] = formatted_dates.fillna('NULL')
            print(f"All dates in column '{column_name}' were successfully converted to {expected_format}.")
            break
        except Exception as e:
            print(f"Failed to process column '{column_name}' with format {expected_format}: {e}")

    if df[column_name].isnull().all():
        print(f"Some dates in column '{column_name}' were empty and have been filled with 'NULL'.")

def determine_file_type(filename):
    file_types = {
        'Social': 'socials',
        'DirectDigital': 'direct_digital',
        'Programmatic': 'programmatic',
        'AdSmart': 'adsmart',
        'Radio': 'radio',
        'VOD': 'vod',
        'TV': 'tv',
        'Cinema': 'cinema',
        'OOH': 'ooh',
        'Performance': 'performance',
        'Print': 'print',
        'PPC': 'ppc'
    }
    for key, value in file_types.items():
        if key in filename:
            return value
    return None

def check_columns(file_columns, predefined_column_sets, file_type):
    if file_type in predefined_column_sets:
        expected_columns = predefined_column_sets[file_type]
        if file_columns == expected_columns:
            return file_type, [], []
        else:
            unmatched_columns = [col for col in file_columns if col not in expected_columns]
            expected_column_names = [col for col in expected_columns if col not in file_columns]
            return None, unmatched_columns, expected_column_names
    else:
        for set_name, columns in predefined_column_sets.items():
            if file_columns == columns:
                return set_name, [], []
        unmatched_columns = [col for col in file_columns if col not in sum(predefined_column_sets.values(), [])]
        expected_column_names = [col for col in sum(predefined_column_sets.values(), []) if col not in file_columns]
        return None, unmatched_columns, expected_column_names

def check_file_date(filename):
    # Get the current month and year
    current_date = datetime.now()
    expected_month = (current_date.month - 2) % 12 + 1  # Previous month
    expected_year = current_date.year if current_date.month > 1 else current_date.year - 1

    valid_channels = [
        "AdSmart", "DirectDigital", "Cinema", "PPC", "Print", "Programmatic",
        "Radio", "Social", "TV", "VOD", "OOH"
    ]

    pattern = r'^Initiative_({}?)_(\d{{8}})_(\d{{8}})\.csv$'.format('|'.join(valid_channels))

    results = []

    # Iterate through files in the specified directory
    for filename in os.listdir(directory_path):
        if not filename.endswith('.csv'):
            continue  # Skip non-CSV files

        file_path = os.path.join(directory_path, filename)
        
        match = re.match(pattern, filename)
        if not match:
            results.append((filename, False, "File name does not match the expected format. Expected format Initiative_<channel>_<start_date>_<end_date>.csv"))
            continue

        channel, start_date, end_date = match.groups() # extracting the channel (not used anywhere further), start date and end date from the file name

        # Check if dates are in correct format (ddmmyyyy)
        try:
            start = datetime.strptime(start_date, "%d%m%Y")
            end = datetime.strptime(end_date, "%d%m%Y")
        except ValueError:
            results.append((filename, False, "Invalid date format. Expected ddmmyyyy."))
            continue

        # Check if the month is correct
        if start.month != expected_month or start.year != expected_year:
            results.append((filename, False, f"Expected month: {expected_month:02d}/{expected_year}, found: {start.month:02d}/{start.year}"))
            continue

        # Check if start date is the first day of the month
        if start.day != 1:
            results.append((filename, False, "Start date should be the first day of the month."))
            continue

        # Check if end date is the last day of the month
        last_day = (datetime(start.year, start.month % 12 + 1, 1) - timedelta(days=1)).day
        if end.day != last_day:
            results.append((filename, False, f"End date should be the last day of the month ({last_day})."))
            continue

        # If all checks pass, attempt to read the CSV file
        try:
            with open(file_path, 'r', newline='') as csvfile:
                csv_reader = csv.reader(csvfile)
                # Read the first row to verify it's a valid CSV
                header = next(csv_reader)
                # You can add additional checks here if needed, e.g., verifying specific column names
            results.append((filename, True, "Filename is valid and CSV is readable."))
        except Exception as e:
            results.append((filename, False, f"Filename is valid but encountered an error reading the CSV: {str(e)}"))

    return results

# main function checking the column names & saving the processed files as csv
def process_and_validate_csv_files(directory_path):
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_folder = os.path.join(directory_path, f"Output_{current_date}")
    for filename, is_valid, message in check_file_date(directory_path):
        print(f"File {filename} is {'valid' if is_valid else 'invalid'}: {message}")
        if not is_valid and message == "File name does not match the expected format. Expected format Initiative_<channel>_<start_date>_<end_date>.csv":
            print("Stopping execution due to invalid file name.") ## if the file name does not match the predefined pattern, the script stops
            return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    ## column names dictionary below updated with the 2025 templates
    predefined_column_sets = {
    "direct_digital": ["Date", "Channel", "Franchise", "Product L2", "Brand", "Platform Campaign Name", "Advvy Campaign Name", "Clicks", "CTC", "GRPs_Impressions"],
    'performance': ['Campaign ID', 'Campaign Name', 'Date', 'Franchise', 'Account', 'Channel', 'Product', 'Impressions', 'Clicks', 'CTC', 'Accepts', 'Refers', 'Declines'],
    "radio": ["Date", "Date From", "Date To", "Channel", "Franchise", "Product L2", "Brand", "Platform Campaign Name", "Advvy Campaign Name", "CTC", "Format / Length", "All Adult GRP", "Target Audience GRP", "Impacts"],
    "vod": ["Date", "Date From", "Date To", "Channel", "Franchise", "Product", "Brand", "Platform Campaign Name", "Advvy Campaign Name", "Impressions", "Clicks", "CTC", "Format / Length"],
    "tv": ["Date", "Date From", "Date To", "Channel", "Franchise", "Product", "Brand", "Platform Campaign Name", "Advvy Campaign Name", "CTC", "Format / Length", "All Adult GRP", "Target Audience GRP (ABC1 Ads)", "30 Equivalised TVRs (All Adult)", "30 Equivalised TVRs (ABC1 ADS)"],
    "cinema": ["Date", "Date From", "Date To", "Channel", "Franchise", "Product L2", "Brand", "Platform Campaign Name", "Advvy Campaign Name", "CTC", "Format / Length", "Target Audience Admissions"],
    "adsmart": ["Date", "Date From", "Date To", "Channel", "Franchise", "Product L2", "Brand", "Platform Campaign Name", "Advvy Campaign Name", "Impressions", "Clicks", "CTC", "Format / Length"],
    "programmatic": ["Date", "Channel", "Franchise", "Product L2", "Brand", "Platform Campaign Name", "Advvy Campaign Name", "Clicks", "CTC", "GRPs_Impressions"],
    "ooh": ["Date", "Date From", "Date To", "Channel", "Franchise", "Product L2", "Brand", "Platform Campaign Name", "Advvy Campaign Name", "CTC", "Format / Length", "All Adult GRP", "Target Audience GRP", "Impacts", "Format Size", "Number of sites"],
    "socials": ["Date", "Channel", "Franchise", "Product L2", "Brand", "Platform Campaign Name", "Advvy Campaign Name", "Clicks", "CTC", "GRPs_Impressions"],
    "print": ["Date", "Date From", "Date To", "Channel", "Franchise", "Product L2", "Brand", "Platform Campaign Name", "Advvy Campaign Name", "CTC", "Format / Length", "All Adult GRP", "Target Audience GRP"],
    "ppc": ["Date", "Channel", "Franchise", "Product L2", "Brand", "Platform Campaign Name", "Advvy Campaign Name", "Clicks", "CTC", "GRPs_Impressions"]
}

    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            print('--------------------------------------------------------------------------------------------------------')
            file_path = os.path.join(directory_path, filename)
            try:
                print(f"Processing file: {filename}")
                
                # Check file date
                check_file_date(filename)
                
                
                # Read the CSV file
                df = pd.read_csv(file_path)
                
                # Determine file type and check columns
                file_type = determine_file_type(filename)
                matching_set, unmatched_columns, expected_column_names = check_columns(df.columns.tolist(), predefined_column_sets, file_type)
                
                if matching_set:
                    print(f"File matches the predefined column names and order of {matching_set} dictionary.")
                else:
                    print(f"File does NOT match some of the predefined column names and order.")
                    print(f"Unmatched or missing columns: {unmatched_columns}")
                    print(f"Expected columns: {expected_column_names}")
                
                # Print column headers and data types
                print("Column headers are:", df.columns.tolist())
                print("\nColumn data types:")
                print(df.dtypes)
                
                # Clean column names and data
                df.columns = df.columns.str.strip()
                df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
                
                # Process date columns
                date_columns = [col for col in df.columns if re.search(r'date', col, re.I)]
                print("\nDate Columns:", date_columns)
                date_formats = ['%d/%m/%Y', '%d/%m/%y']
                for date_column_name in date_columns:
                    validate_date_format(df, date_column_name, date_formats)
                
                # Process other columns
                for col in df.columns:
                    if re.search(r'\b((?:GRPs?_)?Impressions?|CLICKS?)\b', col, re.I):
                        df[col] = df[col].astype(str).str.replace(',', '').astype(float)
                    elif re.search(r'\b(CTC(?:\sINC\sVAT)?)\b', col, re.I):
                        df[col] = df[col].astype(str).replace({'£': '', ',': ''}, regex=True).str.strip()
                        df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
                    elif re.search(r'\bCTR\b', col, re.I):
                        df[col] = df[col].replace(r'^[^\d.-]+', '', regex=True)
                        df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
                        df[col] = df[col].apply(lambda x: f"{x:.5f}")
                    elif re.search(r'\bcampaign(?:\sid)?\b', col, re.I):
                        df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else x)
                    elif re.search(r'\bimpact(?:s)?\b', col, re.I):
                        df[col] = df[col].astype(str).replace(['NOT ON ROUTE', 'Not on Route', 'n/a - NI panels not in Route'], np.nan)
                        df[col] = df[col].str.replace(',', '')
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    elif re.search(r'\bAll\sAdult\sGRP(?:s)?|Target\sAudience\sGRP(?:s)?\b', col, re.I):
                        df[col] = df[col].astype(str).replace(['NOT ON ROUTE', 'Not on Route', 'n/a - NI panels not in Route'], np.nan)
                        df[col] = df[col].str.replace(',', '')
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    elif re.search(r'\bcirculation\b', col, re.I):
                        df[col] = df[col].astype(str).str.replace(',', '').astype(float)
                    
                    print(f"Processed {col} - new data type: {df[col].dtypes}")
                
                # Replace null values and remove empty rows/columns
                df = df.replace(['NULL', 'NA', 'null', 'na', 'N/A', 'N/a', 'n/A', 'n/a'], '')
                df = df[df.apply(sum_of_value, axis=1) > 0]
                df = df[[col for col in df.columns if not col.startswith('Unnamed')]]
                
                # Check for any remaining empty or null values
                cols_with_missing = []
                for col in df.columns:
                    # Count nulls
                    null_count = df[col].isnull().sum()
                    # Count empty strings (only makes sense on object columns)
                    empty_count = 0
                    if df[col].dtype == object:
                        empty_count = df[col].astype(str).str.strip().eq('').sum()
                    # If either is non-zero, flag it
                    if null_count or empty_count:
                        cols_with_missing.append((col, null_count, empty_count))

                if cols_with_missing:
                    print("Columns with empty or null values:")
                    for col, n_null, n_empty in cols_with_missing:
                        print(f"  {col}: {n_null} nulls, {n_empty} empty strings")
                else:
                    print("No columns have empty or null values.")




                # Save transformed data
                output_file_path = os.path.join(output_folder, filename)
                df.to_csv(output_file_path, encoding='utf-8', index=False)
                print(f"\nProcessed and saved: {output_file_path}")
                
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
            
            print("\n")  # New line for better readability between files

# Usage
process_and_validate_csv_files(directory_path)