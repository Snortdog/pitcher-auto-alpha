import os
import matplotlib.pyplot as plt
import pandas as pd
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

    # Add pitch plot
    ax1 = fig.add_subplot(311, aspect='equal')
    scatter = ax1.scatter(x=pitcher_data['PlateLocSide'], y=pitcher_data['PlateLocHeight'],
                        c=pitcher_data['TaggedPitchType'].map(pitch_type_colors).fillna('gray'), alpha=0.5)
    pitch_types = pitcher_data['TaggedPitchType'].unique()
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=pitch_type,
                                  markerfacecolor=pitch_type_colors.get(pitch_type, 'gray'), markersize=10)
                    for pitch_type in pitch_types]
    ax1.legend(handles=legend_elements, title="Pitch Types")
    strike_zone = Rectangle((-0.827, 1.5), 1.654, 1.7, fill=False, color='red')
    ax1.add_patch(strike_zone)

    # Add aggregated data as a table
    ax2 = fig.add_subplot(312)
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

    # Add whiff rate data as a table
    ax3 = fig.add_subplot(313)
    ax3.axis('tight')
    ax3.axis('off')
    whiff_rate_table = ax3.table(cellText=whiff_rate.values, colLabels=whiff_rate.columns, cellLoc='center', loc='center', fontsize=14)

    # Set header font size for whiff rate table
    for i in range(len(whiff_rate.columns)):
        whiff_rate_table[0, i].set_fontsize(14)

    for i in range(len(whiff_rate)):
        if i % 2 == 0:
            for j in range(len(whiff_rate.columns)):
                whiff_rate_table[(i+1, j)].set_facecolor('lightgray')

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