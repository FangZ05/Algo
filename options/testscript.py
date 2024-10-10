# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 19:44:26 2024

@author: Fang
"""

class MyClass:
    def __init__(self, input_value):
        self.input_value = input_value  # Private variable to store the input


    @property
    def constant(self):
        # Calculate the constant based on the input value
        return self.input_value * 3.14  # Example calculation

    def display_values(self):
        print(f"Input Value: {self.input_value}")
        print(f"Constant: {self.constant}")
        
