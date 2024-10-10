# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 13:41:46 2022

@author: Fang-
"""
import plotly.express as px
import plotly.io as pio
#pio.renderers.default='browser'

fig = px.bar(x=["a", "b", "c"], y=[1, 3, 2])
fig.show()