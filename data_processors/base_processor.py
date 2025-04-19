from abc import ABC, abstractmethod
import pandas as pd

class BaseProcessor(ABC):
    @property
    @abstractmethod
    def data_type_name(self) -> str:
        '''The name of the data in the 'Type' column'''
        pass

    def __init__(self, data_by_type: dict[str, pd.DataFrame]):
        if self.data_type_name not in data_by_type:
            raise ValueError(f"{self.__class__.__name__} requires {self.data_type_name} data in the provided data types.")
        self.data = data_by_type[self.data_type_name]

    @abstractmethod
    def Process(self, data: pd.DataFrame) -> None:
        '''Modify the data to make it usable for data visualization'''
        pass

    @abstractmethod
    def Display(self) -> None:
        '''Display all of the associated graphs and valuable data'''
        self.Process()
        pass
