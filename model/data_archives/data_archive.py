from abc import ABC, abstractmethod

from urllib.request import urlopen
import json

from model.filter_builder import RaFilter

class DataArchive(ABC):

    @abstractmethod
    def __init__(self, ra_filter: RaFilter):
        pass

    @abstractmethod
    def get_observations(self):
        pass 


    def get_html(self, url):
        '''
        Returns json data read from the url given in parameter    
        '''
        page = urlopen(url)

        html_bytes = page.read()
        html = html_bytes.decode("utf-8")

        return json.loads(html)


    def freq_to_band(self, frequencies):
        pass