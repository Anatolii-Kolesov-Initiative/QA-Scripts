import os
import pandas as pd

# Run first, BEFORE MMM_data_type_check

# Define the directory containing the CSV files 
csv_directory = r'/Users/anatolii.kolesov/Downloads/Dec MMM File QA' #csv_directory = r'/Users/ayman.kassem-toufi/Downloads/Jan MMM File QA/Nov Files'


# Define multiple sets of predefined columns with their respective orders
predefined_column_sets = {
    'direct_digital': ['Campaign Id', 'Campaign Name', 'Date', 'Franchise', 'Account', 'Channel', 'Product', 'GRPs_Impressions', 'Clicks', 'CTC', 'campaignNameFullyQualified'],
    'performance': ['Campaign ID', 'Campaign Name', 'Date', 'Franchise', 'Account', 'Channel', 'Product', 'Impressions', 'Clicks', 'CTC', 'Accepts', 'Refers', 'Declines'],
    'radio': ['Date (Daily)', 'Date From', 'Date To', 'Channel', 'Campaign name', 'Brand', 'Franchise', 'Product', 'Format / Length', 'CTC INC VAT', 'All Adult GRP', 'Target Audience GRP', 'Impacts'],
    'vod': ['Date (Daily)', 'Date From', 'Date To', 'Channel', 'Campaign name', 'Brand', 'Franchise', 'Product', 'Format / Length', 'Impressions', 'Clicks', 'CTC INC VAT', 'CTR'],
    'tv': ['Date (Daily)', 'Date From', 'Date To', 'Channel', 'Campaign name', 'Brand', 'Franchise', 'Product', 'Format / Length', 'CTC INC VAT', 'All Adult GRP', 'Target Audience GRP (ABC1 Ads)', '30 Equivalised TVRs (All Adult)', '30 Equivalised TVRs (ABC1 ADS)'],
    'cinema': ['Date (Daily)', 'Date From', 'Date To', 'Channel', 'Campaign name', 'Brand', 'Franchise', 'Product', 'Format / Length', 'CTC INC VAT', 'Target Audience Admissions'],
    'adsmart': ['Date (Daily)', 'Date From', 'Date To', 'Channel', 'Campaign Name', 'Brand', 'Franchise', 'Product', 'Format / Length', 'CTC INC VAT', 'Clicks', 'Impressions', 'CTR'],
    'programmatic': ['Campaign Id', 'Campaign Name', 'Date', 'Franchise', 'Account', 'Channel', 'Product', 'GRPs_Impressions', 'Clicks', 'CTC', 'campaignNameFullyQualified'],
    'ooh': ['Date (Daily)', 'Date From', 'Date To', 'Channel', 'Campaign Name', 'Brand', 'Franchise', 'Product', 'Format / Length', 'Format Size', 'Number of sites', 'CTC INC VAT', 'All Adult GRP', 'Target Audience GRP', 'Impacts'],
    'socials': ['Campaign Id', 'Campaign Name', 'Date', 'Franchise', 'Account', 'Channel', 'Product', 'GRPs_Impressions', 'Clicks', 'CTC', 'campaignNameFullyQualified'],
    'print': ['Date (Daily)', 'Date From', 'Date To', 'Channel', 'Campaign Name', 'Brand', 'Franchise', 'Product', 'Format / Length', 'Publication', 'CTC INC VAT', 'All Adult GRP', 'Target Audience GRP', 'Circulation'],
    'ppc': ['Campaign ID', 'Campaign Name', 'Date', 'Franchise', 'Account', 'Channel', 'Product', 'GRPs_Impressions', 'Clicks', 'CTC', 'campaignNameFullyQualified']
}

#NEW VERSION OF CODE, ADDED EXPECTED COLUMN NAME IN PRINT

# Function to check if the columns in the CSV file match any predefined column sets
def check_columns(file_path, predefined_column_sets, file_type):
    df = pd.read_csv(file_path)
    file_columns = df.columns.tolist()
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
        expected_column_names = [col for col in file_columns if col not in sum(predefined_column_sets.values(), [])]
        return None, unmatched_columns, expected_column_names

# Function to determine the file type based on the filename
def determine_file_type(filename):
    if 'Social' in filename:
        return 'socials'
    if 'DirectDigital' in filename:
        return 'direct_digital'
    if 'Programmatic' in filename:
        return 'programmatic'
    if 'AdSmart' in filename:
        return 'adsmart'
    if 'Radio' in filename:
        return 'radio'
    if 'VOD' in filename:
        return 'vod'
    if 'TV' in filename:
        return 'tv'
    if 'Cinema' in filename:
        return 'cinema'
    if 'OOH' in filename:
        return 'ooh'
    if 'Performance' in filename:
        return 'performance'
    if 'Print' in filename:
        return 'print'
    if 'PPC' in filename:
        return 'ppc'
    return None

# Loop through each CSV file in the directory
for filename in os.listdir(csv_directory):
    if filename.endswith('.csv'):
        file_path = os.path.join(csv_directory, filename)
        file_type = determine_file_type(filename)
        matching_set, unmatched_columns, expected_column_names = check_columns(file_path, predefined_column_sets, file_type)
        if matching_set:
            print(f"File {filename} matches the predefined column names and order of {matching_set} dictionary.")
        else:
            print(f"File {filename} does NOT match any predefined column names and order.")
            print(f"Unmatched or missing columns in {filename}: {unmatched_columns}")
            print(f"Expected columns: {filename}: {expected_column_names}")
        print('-----------------------------------------------------------------------------------------------\n')


