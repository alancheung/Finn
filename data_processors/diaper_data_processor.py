from data_processors.base_processor import BaseProcessor

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import timedelta

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
        # TODO figure out error: A value is trying to be set on a copy of a slice from a DataFrame.

        # Straight transformations
        self.data[f'{self.data_type_name}_Poop_Color'] = self.data['Duration']
        self.data[f'{self.data_type_name}_Poop_Type'] = self.data['Start Condition']

        self.data[f'{self.data_type_name}_Had_Fart'] = (self.data['Notes'].str
                                                        .contains(r'\bfart\b', case=False, na=False))
        
        self.data[f'{self.data_type_name}_Had_Rash'] = (self.data['Start Location'].str
                                                        .contains(r'\bDiaper rash\b', case=False, na=False))
        
        self.data[f'{self.data_type_name}_Pee_Amount'] = (self.data['Notes'].str
                                                          .extract(r'Pee:(\w+)', expand=False))

        self.data[f'{self.data_type_name}_Poop_Amount'] = (self.data['Notes'].str
                                                          .extract(r'Poo:(\w+)', expand=False))
        print(self.data.describe())
        return self.data

    def Display(self):
        '''Process and then display data
        '''
        self.Process()