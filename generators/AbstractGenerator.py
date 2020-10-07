from abc import ABC, abstractmethod
import argparse

class AbstractGenerator(ABC):
    
    @abstractmethod
    def generate_subparser(parser) -> [str,argparse.ArgumentParser]:
        pass