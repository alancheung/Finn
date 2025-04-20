from data_processors.base_processor import BaseProcessor

import time
import matplotlib.pyplot as plt
import numpy as np

from typing import Literal 

class DiaperDataProcessor(BaseProcessor):
    '''Processes Diaper data for things like TODO'''

    '''Maps the words used to numerical values'''
    __AMT_MAPPING = {
        'none': 0,
        'small': 1,
        'medium': 2,
        'large': 3
    }

    @property
    def data_type_name(self) -> str:
        return 'Diaper'
        
    def Process(self):
        '''
        @param data Provided data.
        Process the following data:
            TODO 
            - Probability by hour of a small, medium, large pee diapers
            - Probability by hour of a small, medium, large poop diapers
            - Probabiltiy of a diaper by time between changes.

        @example 
        "Diaper","2025-04-16 10:37",,,,,"Both, pee:medium poo:small",
        "Diaper","2025-04-16 07:31",,,,,"Pee:small",
        "Diaper","2025-03-06 03:33",,"red","Loose","Diaper rash","Poo:large","Orange"
        '''
        start = time.time()
        
        # Straight transformations
        self.data[f'{self.data_type_name}_Poop_Color'] = self.data['Duration']
        self.data[f'{self.data_type_name}_Poop_Type'] = self.data['Start Condition']

        self.data[f'{self.data_type_name}_Had_Fart'] = (self.data['Notes'].str
                                                        .contains(r'\bfart\b', case=False, na=False))
        
        self.data[f'{self.data_type_name}_Had_Rash'] = (self.data['Start Location'].str
                                                        .contains(r'\bDiaper rash\b', case=False, na=False))
        
        self.data[f'{self.data_type_name}_Pee_Amount'] = (self.data['End Condition'].str
                                                          .extract(r'[Pp]ee:(\w+)', expand=False).astype(str))
        self.data[f'{self.data_type_name}_Pee_Amount_Value'] = (self.data[f'{self.data_type_name}_Pee_Amount']
                                                                .map(self.__AMT_MAPPING))
        
        self.data[f'{self.data_type_name}_Poo_Amount'] = (self.data['End Condition'].str
                                                          .extract(r'[Pp]oo:(\w+)', expand=False).astype(str))
        self.data[f'{self.data_type_name}_Poo_Amount_Value'] = (self.data[f'{self.data_type_name}_Poo_Amount']
                                                                 .map(self.__AMT_MAPPING))

        # print(self.data.describe())
        print(self.data['Diaper_Pee_Amount'].head(), self.data['Notes'].head())
        print(f'Diaper Data Process: {((time.time() - start) * 1000):.2f} ms')
        return self.data

    def Display(self):
        '''Process and then display data
        '''
        self.Process()

        _, large_pee_probabilities = self.get_hourly_probabilties_of('pee', 'large')
        _, medium_pee_probabilities = self.get_hourly_probabilties_of('pee', 'medium')
        _, small_pee_probabilities = self.get_hourly_probabilties_of('pee', 'small')

        _, large_poo_probabilities = self.get_hourly_probabilties_of('poo', 'large')
        _, medium_poo_probabilities = self.get_hourly_probabilties_of('poo', 'medium')
        _, small_poo_probabilities = self.get_hourly_probabilties_of('poo', 'small')
    
        # Setup more spacing between ticks
        spacing = np.arange(24) * 2 # numTicks(aka hours in day) * spacing

        # Shift the bars to be side by side
        bar_width = 0.4
        offsets = [-bar_width, 0, bar_width]
        
        _, (pee_type_plot, poo_type_plot, pee_total_plot, poo_total_plot) = plt.subplots(4, 1, figsize=(18, 24), sharex=True)
        plt.subplots_adjust(hspace=0.3)

        # Plot Pee
        pee_type_plot.bar(spacing + offsets[0], small_pee_probabilities.values, width=bar_width, color='lightblue', edgecolor='black', label='Small Pee')
        pee_type_plot.bar(spacing + offsets[1], medium_pee_probabilities.values, width=bar_width, color='deepskyblue', edgecolor='black', label='Medium Pee')
        pee_type_plot.bar(spacing + offsets[2], large_pee_probabilities.values, width=bar_width, color='gold', edgecolor='black', label='Large Pee')
        pee_type_plot.set_title('Probability of Pee Type by Hour')
        pee_type_plot.set_ylabel('Probability')
        pee_total_plot.set_xticks(spacing)
        pee_total_plot.set_xticklabels([str(h) for h in range(24)])
        pee_type_plot.grid(axis='y', linestyle='--', alpha=0.7)
        pee_type_plot.legend()

        # Plot Poo
        poo_type_plot.bar(spacing + offsets[0], small_poo_probabilities.values, width=bar_width, color='peru', edgecolor='black', label='Small Poo')
        poo_type_plot.bar(spacing + offsets[1], medium_poo_probabilities.values, width=bar_width, color='chocolate', edgecolor='black', label='Medium Poo')
        poo_type_plot.bar(spacing + offsets[2], large_poo_probabilities.values, width=bar_width, color='saddlebrown', edgecolor='black', label='Large Poo')
        poo_type_plot.set_title('Probability of Poo Type by Hour')
        poo_type_plot.set_ylabel('Probability')
        pee_total_plot.set_xticks(spacing)
        pee_total_plot.set_xticklabels([str(h) for h in range(24)])
        poo_type_plot.grid(axis='y', linestyle='--', alpha=0.7)
        poo_type_plot.legend()

        # Distribution of pee events
        pee_events = self.data[self.data['Diaper_Pee_Amount_Value'].notna()]
        pee_counts_by_hour = pee_events['Start'].dt.hour.value_counts().sort_index()
        pee_counts_by_hour = pee_counts_by_hour.reindex(range(24), fill_value=0)

        pee_total_plot.bar(spacing, pee_counts_by_hour.values, width=bar_width * 2, color='lightgreen', edgecolor='black')
        pee_total_plot.set_title('Distribution of Pee Diapers by Hour')
        pee_total_plot.set_ylabel('Count')
        pee_total_plot.set_xticks(spacing)
        pee_total_plot.set_xticklabels([str(h) for h in range(24)])
        pee_total_plot.grid(axis='y', linestyle='--', alpha=0.7)
        pee_total_plot.legend()

        # Distribution of poo events
        poo_events = self.data[self.data['Diaper_Poo_Amount_Value'].notna()]
        poo_counts_by_hour = poo_events['Start'].dt.hour.value_counts().sort_index()
        poo_counts_by_hour = poo_counts_by_hour.reindex(range(24), fill_value=0)

        poo_total_plot.bar(spacing, poo_counts_by_hour.values, width=bar_width * 2, color='plum', edgecolor='black')
        poo_total_plot.set_title('Distribution of Poo Diapersby Hour')
        poo_total_plot.set_xlabel('Hour of Day')
        poo_total_plot.set_ylabel('Count')
        poo_total_plot.set_xticks(spacing)
        poo_total_plot.set_xticklabels([str(h) for h in range(24)])
        poo_total_plot.grid(axis='y', linestyle='--', alpha=0.7)
        poo_total_plot.legend()

        plt.show()

    def get_hourly_probabilties_of(self, diaper_type: Literal['Pee', 'Poo'], amount: Literal['small', 'medium', 'large']):
        # Small capitalize for Python
        type_data = self.data[self.data[f'{self.data_type_name}_{diaper_type.capitalize()}_Amount'] == amount]
        hourly_counts = type_data['Hour'].value_counts().sort_index()

        # Normalize to probability distribution
        probabilities = (hourly_counts / hourly_counts.sum()).reindex(range(24), fill_value=0)
        return hourly_counts, probabilities