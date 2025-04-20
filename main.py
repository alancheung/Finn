# Pathing/File Dialog
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Statistics
import pandas as pd
from data_processors import FeedDataProcessor, DiaperDataProcessor
import matplotlib as plt

# DEBUG flags
import sys
DEBUG = sys.gettrace() is not None

def main():
    '''
    Program main method
    '''
    raw_data = get_file_data()
    data_by_type = get_data_types(raw_data=raw_data)

    feed_processor = FeedDataProcessor(data_by_type)
    feed_processor.Display()

    diaper_processor = DiaperDataProcessor(data_by_type)
    diaper_processor.Display()

    plt.show()

    # print(f'Imported file "{os.path.basename(data_file_path)}" from path {data_file_path}')
    # print(rawData.length)

    # print(raw_data.describe())
    # print(data_types.keys())
    print(data_by_type['Feed'].describe())
    print(data_by_type['Feed'].head())

def get_file_data():
    '''Open a file dialog for the user to select a file. If the program is in
    debug mode, a debug file is chosen. Then, read data from the given path.
    '''
    data_file_path = None
    if DEBUG:
        data_file_path = './Untracked/HuckleberryData04182025.csv'
    else: 
        Tk().withdraw()  # We don't want a full GUI, so hide the root window
        data_file_path = askopenfilename(
            initialdir=(os.path.join(os.path.expanduser("~"), "Downloads")), 
            filetypes=[("Huckleberry CSV Files", "*.csv")]
        )

        if (not data_file_path):
            raise FileNotFoundError()

    data = pd.read_csv(data_file_path)

    # Not exactly "raw"
    data['Start'] = pd.to_datetime(data['Start'])
    data['End'] = pd.to_datetime(data['End'])
    data['Hour'] = data['Start'].dt.hour

    return data

def get_data_types(raw_data):
    '''
    @param raw_data The raw data from Pandas containing all untyped data.
    @returns Dictionary of types in raw_data partioned by the 'Type' column
    Get all of the 'Type' records from the data set.

    Expected: ['Diaper', 'Feed', 'Pump', 'Meds', 'Growth', 'Skin to skin', 'Sleep', 'Tummy time', 'Indoor play', 'Temp']
    '''
    # Get all unique types
    types = raw_data['Type'].unique()

    # Create a dictionary to hold the separate DataFrames
    type_groups = {type_name: raw_data[raw_data['Type'] == type_name] for type_name in types}
    return type_groups

if __name__ == "__main__":
    main()