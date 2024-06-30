# Import Packages + Starter Functions
import pandas as pd
import json
from bs4 import BeautifulSoup
import requests
# Import required libraries
from zipfile import ZipFile
import os

# pull projecitons from Fangraphs
def fg_projections_pull(fg_url):
    r = requests.get(fg_url)
    r_html = r.text


    # Your input data as string
    json_str = r_html

    # Load data using json module
    data = json.loads(json_str)

    # Iterate over the list and parse the HTML from 'Name' field
    for item in data:
        soup = BeautifulSoup(item['Name'], "html.parser")
        item['Name'] = soup.text

    # Create DataFrame
    df = pd.DataFrame(data)

    # only create the PlayerInfo column if the columns exist
    if 'minpos' in df.columns and 'Name' in df.columns and 'Team' in df.columns:
        df['PlayerInfo'] = df['Name'] + " (" + df['minpos'] + " - " + df['Team'] + ")"

    elif 'Name' in df.columns and 'Team' in df.columns:
        # assume it is a pitcher
        df['PlayerInfo'] = df['Name'] + " (" + 'P - ' + df['Team'] + ")"

    # drop rows where PlayerInfo is null
    df = df.dropna(subset=['PlayerInfo'])
    
    return df

# example 
# url = "https://www.fangraphs.com/api/projections?type=steamerr&stats=bat&pos=all&team=0&players=0&lg=all"
#fg_projections_pull(url).head()

#  ratcdc     =  "https://www.fangraphs.com/api/projections?type=ratcdc&stats=bat&pos=all&team=0&players=0&lg=all" 
#   ratdc =  "https://www.fangraphs.com/api/projections?type=ratcdc&stats=pit&pos=all&team=0&players=0&lg=all" 

def pull_projections(is_offszn = True):
    # pull different models  
    

    # # example urls for ZIPs
    # 'zips_ros_bat':'https://www.fangraphs.com/api/projections?type=rzips&stats=bat&pos=all&team=0&players=0&lg=all'
    # , 'zips_ros_pitch':'https://www.fangraphs.com/api/projections?type=rzips&stats=pit&pos=all&team=0&players=0&lg=all'

    # # rzips changed to steamerr
    # , 'steamer_ros_bat':'https://www.fangraphs.com/api/projections?type=steamerr&stats=bat&pos=all&team=0&players=0&lg=all'
    # , 'steamer_ros_pitch':'https://www.fangraphs.com/api/projections?type=steamerr&stats=pit&pos=all&team=0&players=0&lg=all'

    
    if is_offszn:
        proj_types = {'zipsdc': 'ZIPS DC',
                    'steamer': 'Steamer',
                    'atc': 'ATC',
                    'thebat': 'The Bat',
                    'fangraphsdc': 'Fangraphs DC'
                    }
    else:
        proj_types = {'rzipsdc': 'ZIPS DC',
        'steamerr': 'Steamer',
        'ratcdc': 'ATC DC',
        'rthebat': 'The Bat',
        'rfangraphsdc': 'Fangraphs DC'
        }
        
    
    stat_types = ['bat', 'pit']

    projection_urls = {}

    for proj in proj_types:
        for stat in stat_types:

            # don't pull if type 'pit' and proj is 'rzips' because zips doesn't do saves projections
            if proj in ['rzips','zips'] and stat == 'pit':
                continue

            else:
                url = f"https://www.fangraphs.com/api/projections?type={proj}&stats={stat}&pos=all&team=0&players=0&lg=all"
                # print(url)
                key = f'{proj}_{stat}'
                projection_urls[key] = url
    
    # create a new dict of key: value pairs for the projections


    projections = {}

    for model in projection_urls:

        url = projection_urls[model]
        projections[model] = fg_projections_pull(url)

    return projections
        




    




def format_projections(bat_df, pitch_df):
        
    # List of columns to round to whole numbers
    cols_round_whole = ['IP', 'SO', 'SV', 'W', 'L', 'G', 'PA', 'R', 'HR', 'RBI', 'SB']


    # Round the specified columns to whole numbers for batters and convert to integer type
    for col in cols_round_whole:
        if col in bat_df.columns and pd.api.types.is_numeric_dtype(bat_df[col]):
            bat_df[col] = bat_df[col].round(0).astype(int)

    # Round the specified columns to whole numbers for pitchers and convert to integer type
    for col in cols_round_whole:
        if col in pitch_df.columns and pd.api.types.is_numeric_dtype(pitch_df[col]):
            pitch_df[col] = pitch_df[col].round(0).astype(int)

    # Return the first few rows to check the results
    # bat_df.head(), pitch_df.head()


    # Round all other numbers to the third decimal point for batters
    for col in bat_df.columns:
        if col not in cols_round_whole and pd.api.types.is_numeric_dtype(bat_df[col]):
            bat_df[col] = bat_df[col].round(3)

    # Round all other numbers to the third decimal point for pitchers
    for col in pitch_df.columns:
        if col not in cols_round_whole and pd.api.types.is_numeric_dtype(pitch_df[col]):
            pitch_df[col] = pitch_df[col].round(3)

# Return the first few rows to check the results
#merged_bat.head(), merged_pitch.head()

#    bat_df.set_index('Name',inplace = True)
#    pitch_df.set_index('Name',inplace = True)

    return bat_df, pitch_df





def merge_projections(projections,steamer_key = 'steamer_ros',zips_key = 'zips_ros'):

    merged_dfs = {}
    # Define the list of columns to keep
    pitcher_cols_to_keep = ['Name','Team','IP','ERA','FIP','WHIP','SO','SV','W','L','K%','WAR','RA9-WAR']
    batter_cols_to_keep = ['Name','Team','minpos','Pos','G', 'PA','R','HR','RBI','SB','OBP','wRC+','wOBA','WAR']

    # Select the relevant columns from each DataFrame
    steamer_bat = projections[steamer_key + '_bat']
    steamer_pitch = projections[steamer_key + '_pitch']
    zips_bat = projections[zips_key + '_bat']
    zips_pitch = projections[zips_key + '_pitch']

    steamer_bat = steamer_bat[batter_cols_to_keep]
    steamer_pitch = steamer_pitch[pitcher_cols_to_keep]
    zips_bat = zips_bat[batter_cols_to_keep]
    zips_pitch = zips_pitch[pitcher_cols_to_keep]

    # Merge the steamer and zips dataframes for batters and pitchers separately
    merged_bat = pd.merge(steamer_bat, zips_bat, on=['Name', 'Team'], suffixes=('_steamer', '_zips'))
    merged_pitch = pd.merge(steamer_pitch, zips_pitch, on=['Name', 'Team'], suffixes=('_steamer', '_zips'))

    # Calculate the average for each player between the two datasets for batters
    for column in ['G', 'PA', 'R','HR','RBI','SB','OBP','wRC+','wOBA','WAR']:
        merged_bat[column] = merged_bat[[f'{column}_steamer', f'{column}_zips']].mean(axis=1)

    # Calculate the average for each player between the two datasets for pitchers
    for column in ['IP','ERA','FIP','WHIP','SO','SV','W','L','K%','WAR','RA9-WAR']:
        merged_pitch[column] = merged_pitch[[f'{column}_steamer', f'{column}_zips']].mean(axis=1)

    # Drop the redundant columns
    merged_bat.drop(columns=[col for col in merged_bat.columns if '_steamer' in col or '_zips' in col], inplace=True)
    merged_pitch.drop(columns=[col for col in merged_pitch.columns if '_steamer' in col or '_zips' in col], inplace=True)

    # Return the first few rows to check the results
    #merged_bat.head(), merged_pitch.head()


    return format_projections(merged_bat, merged_pitch)
    




# Assuming dataframes are already created and named: steamer_bat, steamer_pitch, zips_bat, zips_pitch
# For the purpose of this example, let's create some dummy dataframes


# Save dataframes as CSV files
# Let's modify the previous code to not have explicit references to "/mnt/data"

# Save dataframes as CSV files


def projections_to_csv_zip(projections):

    steamer_bat = projections['steamer_bat']
    steamer_pitch = projections['steamer_pitch']
    zips_bat = projections['zips_bat']
    zips_pitch = projections['zips_pitch']

    steamer_bat.to_csv('steamer_bat.csv', index=False)
    steamer_pitch.to_csv('steamer_pitch.csv', index=False)
    zips_bat.to_csv('zips_bat.csv', index=False)
    zips_pitch.to_csv('zips_pitch.csv', index=False)

    # Create a ZipFile object
    with ZipFile('projfiles.zip', 'w') as zipf:
        # Add multiple files to the zip
        zipf.write('steamer_bat.csv')
        zipf.write('steamer_pitch.csv')
        zipf.write('zips_bat.csv')
        zipf.write('zips_pitch.csv')

    # Let's also remove the original CSV files to clean up
    os.remove('steamer_bat.csv')
    os.remove('steamer_pitch.csv')
    os.remove('zips_bat.csv')
    os.remove('zips_pitch.csv')

    print('projfiles.zip created') # Return the path of the created zip file
    


def projections_to_excel(bat_proj, pitch_proj, folderpath='/Users/alexmaisel/Library/CloudStorage/OneDrive-Personal/git_output'):
    # Define the file path
    filepath = os.path.join(folderpath, 'fangraphs_ros_proj.xlsx')

    # Create a Pandas Excel writer using openpyxl as the engine
    writer = pd.ExcelWriter(filepath, engine='openpyxl', mode='a', if_sheet_exists='replace')

    # Write each dataframe to a different worksheet, without the index
    bat_proj.to_excel(writer, sheet_name='Batting Projections', index=False)
    pitch_proj.to_excel(writer, sheet_name='Pitching Projections', index=False)

    # Close the Pandas Excel writer and output the Excel file
    writer.save()
