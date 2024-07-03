from pyexpat import model
import re
import pandas as pd
import numpy as np
import panel as pn
import plotly.graph_objects as go
from compare_players import normalize, format_data_table
import import_fg_projections as import_fg

pn.extension('plotly')
pn.extension('tabulator')
pn.config.raw_css.append("""
.tabulator .tabulator-cell {
    font-size: 14px;
}
.tabulator .tabulator-header .tabulator-col {
    font-size: 14px;
}
""")

# Assuming models and format_data_table are defined elsewhere in your script
# Load data
is_offszn = False
models = import_fg.pull_projections(is_offszn)

# Create a function that returns a plot_radial function and a update_data_table function with a specific player_type
def create_radials(models,player_type):

    

    if player_type == 'pitchers':
        models = {k: v for k, v in models.items() if '_pit' in k}
    elif player_type == 'hitters':
        models = {k: v for k, v in models.items() if '_bat' in k}
    
    method = 'minmax' # 'zscore', 'minmax', 'robust', 'log', 'boxcox'
    for k, v in models.items():
    # Normalize the data
        models[k] = normalize(v, player_type,method=method)

    # Conditional assignment of default_model
    if player_type == 'hitters':
        default_model = 'ratcdc_bat'
    elif player_type == 'pitchers':
        default_model = 'ratcdc_pit'

    # Widget for model selection with default value
    model_selector = pn.widgets.Select(name='Select Model', options=list(models.keys()), value=default_model)    

    # Define 'minpos' as a multi-select widget
    minpos = pn.widgets.MultiChoice(
    name='Select Position',
    options=[],
    description='Position',
    )

  
    @pn.depends(model_selector.param.value)
    def update_minpos_options(model_name):
        model_data = models[model_name]
        
        # Check if 'minpos' column exists in the model data
        if 'minpos' in model_data.columns:
            unique_positions = list(model_data['minpos'].unique())

            unique_positions = ['All'] + unique_positions

            
            # Update the options of the minpos widget
            minpos.options = unique_positions

            # Set the default value of the minpos widget to be all positions
            minpos.value = ['All']
        else:
            # If 'minpos' column doesn't exist, disable the widget
            minpos.disabled = True

        return minpos
    
    # Update the player_selector to be dependent on the model selected
    @pn.depends(model_selector.param.value, minpos.param.value)
    def update_player_selector(model_name, minpos_values):
        model_data = models[model_name]

        if 'All' in minpos_values:
            filtered_players = model_data
        elif 'minpos' in model_data.columns:

            filtered_players = model_data[model_data['minpos'].isin(minpos_values)]
        else:
            filtered_players = model_data

        # model_data['PlayerInfo'] = model_data['Name'] + " (" + model_data['minpos'] + " - " + model_data['Team'] + ")"
        # Only update the options if the player_selector options are empty
        # if not player_selector.options:
        player_selector.options = list(filtered_players['PlayerInfo'])
        return player_selector

    # Widget for player selection with auto-suggest feature
    # Widget for player selection with auto-suggest feature
    player_selector = pn.widgets.MultiChoice(
        name='Select Players', 
        options=[], 
        value=[], 
        placeholder='Type to search players...',
        sizing_mode='stretch_width'  # Make the widget stretch across the screen
    )
    # Create the DataFrame widget outside of the function
    # Create the DataFrame widget outside of the function
    df_widget = pn.widgets.Tabulator(

    name='Interactive DataFrame', 
    layout='fit_data'
    # ,
    # css=[{'selector': '.tabulator', 'props': [('font-size', '16px')]}]
    )
    # Define the formatting options

    # from panel.widgets.tabulator import Styler

    # # Define a function to apply the style
    # def highlight(value):
    #     return f'<div style="background-color:#FFFF00;">{value}</div>'

    # # Create a Styler object
    # styler = df_widget.Styler.from_columns({
    #     'OBP': highlight,
    #     'RBI': highlight,
    #     'HR': highlight,
    #     'R': highlight,
    #     'SB': highlight,
    #     'ERA': highlight,
    #     'SO': highlight,
    #     'WHIP': highlight,
    # })

    # # Apply the styler to the Tabulator widget
    # df_widget.formatters = styler
    
    df_widget.widths = {'Name': 120}
    df_widget.index_position = None

    @pn.depends(model_selector.param.value, player_selector.param.value, minpos.param.value)
    def update_data_table(model_name, players, minpos_values):
        model_data = models[model_name]

        # Filter the model_data based on the selected minpos values
        if 'All' not in minpos_values and 'minpos' in model_data.columns:
            model_data = model_data[model_data['minpos'].isin(minpos_values)]

        formatted_data = format_data_table(model_data, players, player_type)
        
        
        # Update the value of the DataFrame widget
        df_widget.value = formatted_data

        # df_widget.widths = {c: 100 for c in formatted_data.columns}

        
        df_widget.show_index = False

        return df_widget
    @pn.depends(model_selector.param.value, player_selector.param.value, minpos.param.value)
    def plot_radial(model_name, players, minpos_values):
        model_data = models[model_name]

        if 'All' not in minpos_values and 'minpos' in model_data.columns:
            model_data = model_data[model_data['minpos'].isin(minpos_values)]

        if player_type == 'pitchers':
            categories = ['ERA', 'SO', 'WHIP', 'W', 'SV']
        elif player_type == 'hitters':
            categories = ['OBP', 'RBI', 'HR', 'R', 'SB']

        categories_norm = [f'{cat}_norm' for cat in categories]  # Use normalized versions
        
        max_value = model_data[categories_norm].max().max()

        fig = go.Figure()

            # Assuming model_data contains the actual values in columns named after the categories
# and you have a list of players and their corresponding data in model_data

    
        for player in players:
            df_player = model_data[model_data['PlayerInfo'] == player]
            
            # Extract actual values for the categories
            metrics = df_player[categories].values.flatten().tolist()  # Adjust 'categories' as needed
            
            # Continue with metrics_norm and hover_text as before
            metrics_norm = df_player[categories_norm].values.flatten().tolist()
            metrics_norm += metrics_norm[:1]  # Complete the loop in the radar chart

            hover_text = f"{player}<br>" + "<br>".join([f"{cat}: {metrics[i]}" for i, cat in enumerate(categories)])
            
            # The rest of your code for adding traces and updating layout continues here
                    
            fig.add_trace(go.Scatterpolar(
                r=metrics_norm,
                theta=categories,
                fill='toself',
                name=player,
                hoverinfo='text',
                text=hover_text
            ))
            

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0, max_value])
            ),
            showlegend=True,
            autosize=True,  # Ensure the plot resizes
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=-0.25, 
                xanchor="center", 
                x=0.5
            ),
            template="plotly",
            dragmode=False,
            font = dict(
                size = 18
            )        )

        # # Apply margin settings as the last step
        # fig.update_layout(
        #     margin=dict(l=50, r=50, b=50, t=5, pad=2)
        # )

        # Use sizing_mode for responsive width
        plot = pn.pane.Plotly(fig, sizing_mode='stretch_both')

        return plot
    
    return model_selector, update_minpos_options, update_player_selector, update_data_table, plot_radial
    

# Create instances of update_data_table and plot_radial for hitters and pitchers
model_selector_hitters, update_minpos_options_hitters, update_player_selector_hitters, update_data_table_hitters, plot_radial_hitters = create_radials(models,'hitters')
model_selector_pitchers, update_minpos_options_pitchers, update_player_selector_pitchers, update_data_table_pitchers, plot_radial_pitchers = create_radials(models,'pitchers')

# Create accordions
accordion_hitters = pn.Accordion(('Model and Position Selector', pn.Column(model_selector_hitters, update_minpos_options_hitters)))
accordion_pitchers = pn.Accordion(('Model and Position Selector', pn.Column(model_selector_pitchers, update_minpos_options_pitchers)))

# Create the layout
# hitters
hitters_layout = pn.Column(
    update_player_selector_hitters,
    plot_radial_hitters,
    pn.Row(update_data_table_hitters, align='center'),  # Wrap the table in a pn.Row and align it to center
    accordion_hitters,
    sizing_mode='stretch_width'
)

# pitchers
pitchers_layout = pn.Column(
    update_player_selector_pitchers,
    plot_radial_pitchers,
    pn.Row(update_data_table_pitchers,align='center'),  # Wrap the table in a pn.Row and align it to center
    accordion_pitchers,
    sizing_mode='stretch_width'
)

tabs = pn.Tabs(
    ('Hitters', hitters_layout),  
    ('Pitchers', pitchers_layout),
    sizing_mode='stretch_width'
)
# To display the tabs in the notebook
tabs.servable()