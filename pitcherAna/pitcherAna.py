import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math 
from matplotlib.patches import Rectangle
from tkinter import filedialog
from tkinter import Tk
from matplotlib.backends.backend_pdf import PdfPages

# Define pitch type colors
pitch_type_colors = {
    'Fastball': 'red',
    'Slider': 'blue',
    'Changeup': 'green',
    'Curveball': 'purple',
    'Cutter': 'orange',
    'Sinker': 'yellow'
}

root = Tk()
root.withdraw()

file_path = filedialog.askopenfilename()
data = pd.read_csv(file_path)
data.sort_values(by='Pitcher', inplace=True)

# Filter out pitchers from the specific team
pitchers = data[data['PitcherTeam'] == 'SOU_GOL']['Pitcher'].unique().tolist()

# Create a new directory for the selected file
new_directory = os.path.splitext(file_path)[0]
os.makedirs(new_directory, exist_ok=True)

# Define the aggregation operations for each column
agg_operations = {
    'RelSpeed': ['mean', 'max'], 
    'SpinRate': ['mean'], 
    'SpinAxis': ['mean'], 
    'RelHeight': ['mean'], 
    'Extension': ['mean'], 
    'VertBreak': ['mean'], 
    'InducedVertBreak': ['mean'], 
    'HorzBreak': ['mean'], 
    'ZoneSpeed': ['mean'], 
    'VertApprAngle': ['mean']
}

def create_heatmap(data, batter_side, ax):
    # filter data based on batter team and batter side
    filtered_data = data[(data['BatterTeam'] != 'SOU_GOL') & (data['BatterSide'] == batter_side)]
    
    # define success
    conditions = [
        (filtered_data['PitchCall'] == 'StrikeSwinging'), 
        (filtered_data['PitchCall'] == 'InPlay')
    ]
    values = [0, filtered_data['ExitSpeed']]
    filtered_data['Success'] = np.select(conditions, values)

    # plot heat map
    hb = ax.hist2d(filtered_data['PlateLocSide'], filtered_data['PlateLocHeight'], weights=filtered_data['Success'], 
                   bins=[np.arange(-3, 3.5, 0.5), np.arange(0, 5.5, 0.5)], cmap='viridis')
    ax.set_title(f'Heat map for {batter_side} Batter')
    plt.colorbar(hb[3], ax=ax)

for pitcher in pitchers:
    pitcher_data = data[data['Pitcher'] == pitcher]
    pitcher_data_with_exit_speed = pitcher_data[~pitcher_data['ExitSpeed'].isna()]
    aggregated_data = pitcher_data_with_exit_speed.groupby('TaggedPitchType').agg(agg_operations).reset_index()
    aggregated_data = aggregated_data.round(2)  # round to 2 decimal places

    total_swings = pitcher_data[pitcher_data['PitchCall'].isin(['StrikeSwinging', 'InPlay', 'FoulBall'])].groupby('TaggedPitchType').size()
    swings_and_misses = pitcher_data[pitcher_data['PitchCall'] == 'StrikeSwinging'].groupby('TaggedPitchType').size()
    whiff_rate = (swings_and_misses / total_swings).reset_index()
    whiff_rate.columns = ['TaggedPitchType', 'WhiffRate']
    whiff_rate['WhiffRate'] = whiff_rate['WhiffRate'].round(2)

     # Define the strike zone
    strike_zone = {'left': -.827, 'right': .827, 'bottom': 1.5, 'top': 3.2}

     # calculate total pitches and swings outside the zone for each pitch type
    outside_zone_data = pitcher_data[
        (pitcher_data['PlateLocSide'] < strike_zone['left']) | 
        (pitcher_data['PlateLocSide'] > strike_zone['right']) | 
        (pitcher_data['PlateLocHeight'] < strike_zone['bottom']) | 
        (pitcher_data['PlateLocHeight'] > strike_zone['top'])
    ]

    total_pitches_outside_zone = outside_zone_data.groupby('TaggedPitchType').size()
    total_swings_outside_zone = outside_zone_data[
        outside_zone_data['PitchCall'].isin(['StrikeSwinging', 'InPlay', 'FoulBall'])
    ].groupby('TaggedPitchType').size()

    # calculate chase rate
    chase_rate = (total_swings_outside_zone / total_pitches_outside_zone).reset_index()
    chase_rate.columns = ['TaggedPitchType', 'ChaseRate']
    chase_rate['ChaseRate'] = chase_rate['ChaseRate'].round(2)
    
     # Calculate the 'Strike%'
    strikes = pitcher_data[pitcher_data['PitchCall'].isin(['StrikeCalled', 'StrikeSwinging', 'InPlay', 'FoulBall'])].groupby('TaggedPitchType').size()
    total_pitches = pitcher_data.groupby('TaggedPitchType').size()
    strike_percent = (strikes / total_pitches).reset_index()
    strike_percent.columns = ['TaggedPitchType', 'Strike%']
    strike_percent['Strike%'] = strike_percent['Strike%'].round(2)

    # Calculate 'InZone%'
    in_zone_data = pitcher_data[
        (pitcher_data['PlateLocSide'] >= strike_zone['left']) & 
        (pitcher_data['PlateLocSide'] <= strike_zone['right']) & 
        (pitcher_data['PlateLocHeight'] >= strike_zone['bottom']) & 
        (pitcher_data['PlateLocHeight'] <= strike_zone['top'])
    ]
    in_zone_pitches = in_zone_data.groupby('TaggedPitchType').size()
    in_zone_percent = (in_zone_pitches / total_pitches).reset_index()
    in_zone_percent.columns = ['TaggedPitchType', 'InZone%']
    in_zone_percent['InZone%'] = in_zone_percent['InZone%'].round(2)

    # Calculate 'InZoneWhiff%'
    in_zone_whiffs = in_zone_data[in_zone_data['PitchCall'] == 'StrikeSwinging'].groupby('TaggedPitchType').size()
    in_zone_whiff_percent = (in_zone_whiffs / in_zone_pitches).reset_index()
    in_zone_whiff_percent.columns = ['TaggedPitchType', 'InZoneWhiff%']
    in_zone_whiff_percent['InZoneWhiff%'] = in_zone_whiff_percent['InZoneWhiff%'].round(2)

    # Calculate 'Usage'
    usage = (total_pitches / len(pitcher_data)).reset_index()
    usage.columns = ['TaggedPitchType', 'Usage']
    usage['Usage'] = usage['Usage'].round(2)

    # Calculate 'CSW%'
    csw = pitcher_data[pitcher_data['PitchCall'].isin(['StrikeSwinging', 'StrikeCalled'])].groupby('TaggedPitchType').size()
    csw_percent = (csw / total_pitches).reset_index()
    csw_percent.columns = ['TaggedPitchType', 'CSW%']
    csw_percent['CSW%'] = csw_percent['CSW%'].round(2)

    # Calculate 'Swing%'
    swings = pitcher_data[pitcher_data['PitchCall'].isin(['InPlay', 'StrikeSwinging', 'FoulBall'])].groupby('TaggedPitchType').size()
    swing_percent = (swings / total_pitches).reset_index()
    swing_percent.columns = ['TaggedPitchType', 'Swing%']
    swing_percent['Swing%'] = swing_percent['Swing%'].round(2)

    # Calculate 'PitchesThrown'
    pitches_thrown = total_pitches.reset_index()
    pitches_thrown.columns = ['TaggedPitchType', 'PitchesThrown']

     # Merge whiff_rate into aggregated_data
    stats_dataframes = [whiff_rate, chase_rate, strike_percent, in_zone_percent, in_zone_whiff_percent, usage, csw_percent, swing_percent, pitches_thrown]
    for stats_df in stats_dataframes:
        aggregated_data = pd.merge(aggregated_data, stats_df, on='TaggedPitchType', how='left')

    
    # Transpose the DataFrame
    aggregated_data.set_index('TaggedPitchType', inplace=True)
    aggregated_data = aggregated_data.transpose().reset_index()
    aggregated_data.columns.names = [None]  # Remove the top level column name
    aggregated_data.rename(columns={'index': 'AggregatedData'}, inplace=True)


   

    
    # Create a directory for each pitcher inside the new directory
    pitcher_directory = os.path.join(new_directory, pitcher)
    os.makedirs(pitcher_directory, exist_ok=True)

    # Define the pdf path
    pdf_output_path = os.path.join(pitcher_directory, f"{pitcher}_{os.path.basename(file_path).split('.')[0]}.pdf")

    pdf_pages = PdfPages(pdf_output_path)

    # Line by line data
    line_by_line_columns = ['TaggedPitchType', 'PitchCall', 'RelSpeed', 'SpinRate', 'SpinAxis', 'RelHeight', 'Extension', 'VertBreak', 
                            'InducedVertBreak', 'HorzBreak', 'ZoneSpeed', 'VertApprAngle', 'ExitSpeed', 'Distance']
    line_by_line_data = pitcher_data[line_by_line_columns].copy()
    line_by_line_data = line_by_line_data.round(2)  # round to 2 decimal places
    line_by_line_data['ExitSpeed'] = line_by_line_data['ExitSpeed'].fillna('Not Applicable')
    
     # Loop through chunks of line_by_line_data
    rows_per_page = 50
    chunks = [line_by_line_data[i:i+rows_per_page] for i in range(0, line_by_line_data.shape[0], rows_per_page)]
    
    # Create a figure and add subplots to it
    fig = plt.figure(figsize=(20, 20))
    fig.suptitle('Southern Miss Baseball\n' + f"{pitcher} {os.path.basename(file_path).split('.')[0]}", fontsize=20, y=0.92)

    ax1 = fig.add_subplot(311, aspect='equal')
    scatter = ax1.scatter(x=pitcher_data['PlateLocSide'], y=pitcher_data['PlateLocHeight'],
                        c=pitcher_data['TaggedPitchType'].map(pitch_type_colors).fillna('gray'), alpha=0.5)
    pitch_types = pitcher_data['TaggedPitchType'].unique()
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=pitch_type,
                                  markerfacecolor=pitch_type_colors.get(pitch_type, 'gray'), markersize=10)
                    for pitch_type in pitch_types]
    ax1.legend(handles=legend_elements, title="Pitch Types")
    strike_zone = {'left': -.827, 'right': .827, 'bottom': 1.5, 'top': 3.2}
    strike_zone_rect = Rectangle((strike_zone['left'], strike_zone['bottom']), 
                                strike_zone['right'] - strike_zone['left'], 
                                strike_zone['top'] - strike_zone['bottom'], 
                                fill=False)
    ax1.add_patch(strike_zone_rect)
    ax1.set_xlim([-3, 3])  # setting x-axis limits
    ax1.set_ylim([0, 5])   # setting y-axis limits
    
    ax3 = fig.add_subplot(312, aspect='equal')  # adding the third subplot
    scatter = ax3.scatter(x=pitcher_data['HorzBreak'], y=pitcher_data['InducedVertBreak'],
                          c=pitcher_data['TaggedPitchType'].map(pitch_type_colors).fillna('gray'), alpha=0.5)
    ax3.set_title('Movement (Horz/IVB)')  # setting the title of the plot

    ax3.axhline(0, color='black', linewidth=0.5)  # horizontal line at y=0
    ax3.axvline(0, color='black', linewidth=0.5)  # vertical line at x=0

    ax3.set_xlim([-30, 30])  # setting x-axis limits
    ax3.set_ylim([-30, 30])  # setting y-axis limits

    pitch_types = pitcher_data['TaggedPitchType'].unique()
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=pitch_type,
                                  markerfacecolor=pitch_type_colors.get(pitch_type, 'gray'), markersize=10)
                    for pitch_type in pitch_types]
    ax3.legend(handles=legend_elements, title="Pitch Types")

    # Create heat map for Left Batter
    #create_heatmap(pitcher_data, 'Left', ax4)
    #ax4.set_title('Heatmap vs Left')

    # Create heat map for Right Batter
    #ax5 = fig.add_subplot(514)
    #create_heatmap(pitcher_data, 'Right', ax5)
    #ax5.set_title('Heatmap vs Right')

    # Add aggregated data as a table
    ax2 = fig.add_subplot(313)
    ax2.axis('tight')
    ax2.axis('off')
    aggregated_table = ax2.table(cellText=aggregated_data.values, colLabels=aggregated_data.columns, cellLoc = 'center', loc='center', fontsize=14)

    # Set header font size for aggregated table
    for i in range(len(aggregated_data.columns)):
        aggregated_table[0, i].set_fontsize(14)

    for i in range(len(aggregated_data)):
        if i % 2 == 0:
            for j in range(len(aggregated_data.columns)):
                aggregated_table[(i+1, j)].set_facecolor('lightgray')

    

    # Save the figure to the pdf
    pdf_pages.savefig(fig, bbox_inches='tight')
    plt.close(fig)  # Close the figure to free up memory

    for chunk in chunks:
        # Create a figure and add subplots to it
        fig = plt.figure(figsize=(20, 20))
        
         # Add line-by-line data as a table
        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        line_by_line_table = ax.table(cellText=chunk.values, colLabels=chunk.columns, cellLoc = 'center', loc='center', fontsize=14)

        # Set header font size for line_by_line table
        for i in range(len(chunk.columns)):
            line_by_line_table[0, i].set_fontsize(14)

        for i in range(len(chunk)):
            if i % 2 == 0:
                for j in range(len(chunk.columns)):
                    line_by_line_table[(i+1, j)].set_facecolor('lightgray')

        # Save the figure to the pdf
        pdf_pages.savefig(fig, bbox_inches='tight')
        plt.close(fig)  # Close the figure to free up memory

    # Close the pdf file
    pdf_pages.close()

    print(f"All data saved to {pdf_output_path}")