# pitcher-auto-alpha

This program analyzes Trackman baseball pitch data, which is aggregated by pitcher, and generates a detailed report in PDF format for each pitcher. The program expects the data to be in CSV format with specific columns present.

# Important!!!
You must replace 'SOU_GOL' in the filter out pitchers from the specific team line with your team idenfifier or the program will not work!!!!

# Dependencies
This program depends on the following Python libraries:

os

matplotlib

pandas

math

tkinter

matplotlib.backends.backend_pdf

Ensure you have all these dependencies installed before running the program. You can install these libraries using pip:

pip install matplotlib pandas tkinter

Note: os and math are part of the standard Python library and do not need to be installed separately.

# Usage
Run the program.

The program will open a file dialog. Select the CSV file with the data to be analyzed.

The program will automatically create a new directory based on the selected file's name, and within that directory, it will create a sub-directory for each pitcher.

Inside each pitcher's directory, the program will create a PDF file with detailed reports including various types of charts and tables.

# Program Features
The program performs the following operations:

It filters out pitchers from a specific team.

The data is then aggregated by each pitcher. Various metrics such as release speed, spin rate, spin axis, release height, extension, vertical break, induced vertical break, horizontal break, zone speed, and vertical approach angle are averaged. The maximum release speed is also determined.

The whiff rate for each type of pitch is calculated. Whiff rate is the number of swinging strikes divided by the total number of swings for a particular pitch type.

The program then generates a PDF report for each pitcher, which includes:

A scatter plot representing pitch locations by pitch type.

A table of aggregated data for each pitch type.

A table of whiff rate data for each pitch type.

Tables of line-by-line data in chunks of 50 rows each.

# Data Format
The input data should be in CSV format with the following columns:

Pitcher: The name of the pitcher.

PitcherTeam: The team the pitcher belongs to.

TaggedPitchType: The type of pitch thrown.

PitchCall: The result of the pitch.

RelSpeed: The release speed of the pitch.

SpinRate: The spin rate of the pitch.

SpinAxis: The spin axis of the pitch.

RelHeight: The release height of the pitch.

Extension: The extension of the pitcher's arm when throwing.

VertBreak: The vertical break of the pitch.

InducedVertBreak: The induced vertical break of the pitch.

HorzBreak: The horizontal break of the pitch.

ZoneSpeed: The speed of the pitch in the strike zone.

VertApprAngle: The vertical approach angle of the pitch.

ExitSpeed: The exit speed of the ball when hit.

Distance: The distance the ball traveled.

PlateLocSide: The location of the pitch in relation to the side of the plate.

PlateLocHeight: The height of the pitch when it crosses the plate.

# Sample Output
Upon running this script, a new directory is created based on the input CSV file name. Within this directory, there will be a directory for each pitcher, which will contain a PDF report for that pitcher.

The generated PDF report will include:

Page 1:

A scatter plot of pitches by type, with different colors representing different pitch types.

A table summarizing the aggregated data, which includes average values and maximum values for various metrics.

A table showing the whiff rate for each pitch type.

Subsequent pages: Tables containing line-by-line data. If there is a lot of data, it will be split into chunks of 50 rows per page.

At the end of the execution, the program will print the path to the generated PDF report in the console.

# Troubleshooting

Issue: The program doesn't run or shows an error related to a missing module.

Solution: Ensure you have installed all the necessary Python modules listed in the 'Dependencies' section of this document.

Issue: The program doesn't read the file or the data correctly.

Solution: Ensure that your CSV file is correctly formatted, with all the necessary columns. The expected columns are listed in the 'Data Format' section of this document.

Issue: The program creates a PDF, but some of the pages are blank or the data doesn't look right.

Solution: Ensure that your data is valid and correctly formatted. Check for any missing or malformed data that could be causing the issue.
