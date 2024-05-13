from pyexpat import model
import pandas as pd
import numpy as np
import panel as pn
import plotly.graph_objects as go
import import_fg_projections as import_fg
from sklearn.preprocessing import RobustScaler
from scipy import stats

# pn.extension('plotly')

# # Load data
# is_offszn = False
# models = import_fg.pull_projections(is_offszn)

# # filter to only models that include 'pit' in the name
# models = {k: v for k, v in models.items() if '_pit' in k}

# Normalize the statistics

import numpy as np
from sklearn.preprocessing import RobustScaler
from scipy import stats

def normalize(df, player_type, method='zscore'):
    if player_type == 'pitchers':

    
        # limit to the top 400 players by IP or SV
        # if a player is in the top 400 in either IP or SV, they will be included
        
        # top 400 by IP
        df_ip = df[df['IP'] > 0].sort_values('IP', ascending=False).head(400)
        # top 400 by SV
        df_sv = df[df['SV'] > 0].sort_values('SV', ascending=False).head(400)
        # combine the two dataframes
        df = pd.concat([df_ip, df_sv]).drop_duplicates()

        # Normalize the statistics
        if method == 'zscore':
            for col in ['SO', 'W', 'SV']:
                df[col + '_norm'] = (df[col] - df[col].mean()) / df[col].std()
            for col in ['ERA', 'WHIP']:
                df[col + '_norm'] = (df[col].mean() - df[col]) / df[col].std()  # Invert the normalization for ERA and WHIP
        
        # In use in radial.py
        elif method == 'minmax':
            for col in ['SO', 'W', 'SV']:
                df[col + '_norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
            for col in ['ERA', 'WHIP']:
                df[col + '_norm'] = 1 - ((df[col] - df[col].min()) / (df[col].max() - df[col].min()))  # Invert the normalization for ERA and WHIP
        elif method == 'robust':
            scaler = RobustScaler()
            for col in ['SO', 'W', 'SV']:
                df[col + '_norm'] = scaler.fit_transform(df[[col]])
            for col in ['ERA', 'WHIP']:
                df[col + '_norm'] = 1 - scaler.fit_transform(df[[col]])  # Invert the normalization for ERA and WHIP
        elif method == 'log':
            for col in ['SO', 'W', 'SV']:
                df[col + '_norm'] = np.log(df[col])
            for col in ['ERA', 'WHIP']:
                df[col + '_norm'] = 1 - np.log(df[col])  # Invert the normalization for ERA and WHIP
        elif method == 'boxcox':
            for col in ['SO', 'W', 'SV']:
                df[col + '_norm'], _ = stats.boxcox(df[col])
            for col in ['ERA', 'WHIP']:
                df[col + '_norm'] = 1 - stats.boxcox(df[col])[0]  # Invert the normalization for ERA and WHIP
        else:
            raise ValueError(f"Unknown method: {method}")

    
    
    
    elif player_type == 'hitters':
        df = df[df['PA'] > 0].sort_values('PA', ascending=False).head(400)
    
    # Normalize the statistics
        if method == 'zscore':
            # Normalize the statistics
            for col in ['OBP', 'RBI', 'HR', 'R', 'SB']:
                df[col + '_norm'] = (df[col] - df[col].mean()) / df[col].std()
        elif method == 'minmax':
            for col in ['OBP', 'RBI', 'HR', 'R', 'SB']:
                df[col + '_norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
        elif method == 'robust':
            scaler = RobustScaler()
            for col in ['OBP', 'RBI', 'HR', 'R', 'SB']:
                df[col + '_norm'] = scaler.fit_transform(df[[col]])
        elif method == 'log':
            for col in ['OBP', 'RBI', 'HR', 'R', 'SB']:
                df[col + '_norm'] = np.log(df[col])
        elif method == 'boxcox':
            for col in ['OBP', 'RBI', 'HR', 'R', 'SB']:
                df[col + '_norm'], _ = stats.boxcox(df[col])
        else:
            raise ValueError(f"Unknown method: {method}")
    
    return df


# # Apply normalization to all models
# for k, v in models.items():
#     # Normalize the data
#     models[k] = normalize(v)

# Function to format the data table
def format_data_table(model_data, players, player_type):
    selected_data = model_data[model_data['PlayerInfo'].isin(players)].copy()
    
    if player_type == 'hitters':
        core_metrics = ['OBP', 'RBI', 'HR', 'R', 'SB']
        # Custom formatting for display
        for col in ['OBP','wOBA']:
            selected_data[col] = selected_data[col].apply(lambda x: f'{x:.3f}'.lstrip('0'))
        for col in ['RBI', 'HR', 'R', 'SB','wRC+','PA']:
            selected_data[col] = selected_data[col].round(0).astype(int)
        for col in ['WAR']:
            selected_data[col] = selected_data[col].apply(lambda x: f'{x:.2f}')
        # Return the DataFrame with the core metrics bolded
        return selected_data[['Name','Team','minpos','PA','WAR','wRC+','wOBA','OBP', 'RBI', 'HR', 'R', 'SB']] #.style.set_properties(subset=core_metrics, **{'font-weight': 'bold'})

    elif player_type == 'pitchers':
        core_metrics = ['ERA', 'SO', 'W', 'WHIP', 'SV']
        # Custom formatting for display
        for col in ['ERA', 'WHIP','WAR','FIP']:
            selected_data[col] = selected_data[col].apply(lambda x: f'{x:.2f}')
        for col in ['SO', 'W', 'SV','IP']:
            selected_data[col] = selected_data[col].apply(lambda x: f'{x:.0f}')
        # Return the DataFrame with the core metrics bolded
        return selected_data[['Name','Team','IP','WAR','FIP','ERA', 'SO', 'WHIP', 'W', 'SV']] #.style.set_properties(subset=core_metrics, **{'font-weight': 'bold'})