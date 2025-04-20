from data_processors.base_processor import BaseProcessor

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import timedelta

class FeedDataProcessor(BaseProcessor):
    @property
    def data_type_name(self) -> str:
        return 'Feed'
        
    def Process(self):
        '''
        @param data Provided 'Feed' data.
        Process the following data:
            - Amount as an integer
            TODO 
            - End Time
            - Average pull amount
            - Keywords (tired, asleep)
            - Further distinguish by breast milk and formula
            - Group into hours

        Ex. Feed	2025-03-26 02:55			Breast Milk	Bottle	45ml	0325 - 2 - 0342\n0313 - 40ml\nBurp\nSecond small take\n\nNo good burps
        '''
        self.data['Feed_Amount'] = self.data['End Condition'].str.extract(r'(\d+)').astype(int)
        self.data['RollingAvg'] = self.data['Feed_Amount'].rolling(window=7).mean()

    def Display(self):
        '''Process and then display 'Feed' data
        '''
        self.Process()

        x = self.data['Start'].map(pd.Timestamp.toordinal)  # Convert 'Start' dates to ordinal numbers (for fitting)
        y = self.data['Feed_Amount']

        # Create a best-fit line (degree 1 for linear)
        slope, intercept = np.polyfit(x, y, 1)

        def calculate_crossing(y_value):
            '''Local function to determine X for a given y_value'''
            x_cross = (y_value - intercept) / slope
            crossing_date = pd.Timestamp.fromordinal(int(round(x_cross)))
            
            return crossing_date
        crossing_90 = calculate_crossing(90)
        crossing_120 = calculate_crossing(120)

        # Create extended date range from start to crossing_120 so the graph looks nice
        start_date = self.data['Start'].min()
        end_date = pd.to_datetime(crossing_120)
        extended_dates = pd.date_range(start=start_date, end=end_date, freq='D')

        # Convert extended dates to ordinal and compute best fit line for full range
        extended_x = extended_dates.map(pd.Timestamp.toordinal)
        extended_best_fit = slope * extended_x + intercept

        # Plot original self.data + rolling average + best fit line
        plt.figure(figsize=(12, 6))
        plt.plot(self.data['Start'], self.data['Feed_Amount'], label='Original', alpha=0.5)
        plt.plot(self.data['Start'], self.data['RollingAvg'], label='7-Day Rolling Avg', color='red', linewidth=2)
        plt.plot(extended_dates, extended_best_fit, label='Line of Best Fit', color='green', linewidth=2, linestyle='--')

        # Threshold lines
        plt.axvline(pd.to_datetime(crossing_90), color='gray', linestyle='--', label=f'Expected 90ml Average on {crossing_90}')
        plt.axvline(pd.to_datetime(crossing_120), color='lightgray', linestyle='--', label=f'Expected 120ml Average on {crossing_120}')

        # Labels, grid, legend
        plt.title('Feed Amount Over Time with Rolling Average and Line of Best Fit')
        plt.xlabel('Start Date')
        plt.ylabel('Feed Amount')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)

        # Extend x-axis to show crossing_120
        plt.xlim([start_date, end_date + timedelta(days=3)])
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=7)) 
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        plt.tight_layout()
