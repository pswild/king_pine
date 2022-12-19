# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""
Visuals for paper on emissions impact of King Pine wind farm.

Created on Mon Dec 12 21:56:51 2022

@author: pswild
"""

import os
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt

# --- PATH ---# 

# Get path.
here = os.path.dirname(os.path.realpath(__file__))

#--- OUTPUT ---# 

# ISO-NE generated emissions profile. 
generated_emissions_file = os.path.join(here, 'output/generated_emissions_profile.csv')

# King Pine avoided emissions profile. 
avoided_emissions_file = os.path.join(here, 'output/avoided_emissions_profile.csv')

def visualize():
    '''.'''

    return

if __name__ == '__main__':

    # Read in grid generation and emissions generated.
    grid_output = None
    if os.path.exists(generated_emissions_file):
        grid_output = pd.read_csv(generated_emissions_file, index_col=False)

    # Convert from string to datetime and remove hours.
    grid_output['Date'] = pd.to_datetime(grid_output['Date'], format='%m-%d %H:%M').dt.strftime('%U')

    # Read in wind generation and emissions avoided.
    wind_output = None
    if os.path.exists(avoided_emissions_file):
        wind_output = pd.read_csv(avoided_emissions_file, index_col=False)

    # Convert from string to datetime and remove hours.
    wind_output['Date'] = pd.to_datetime(wind_output['Date'], format='%m-%d %H:%M').dt.strftime('%U')

    # Rename columns. 
    grid_output.rename(columns={"Generation (MWh)": "Grid Generation (MWh)"}, inplace=True)
    wind_output.rename(columns={"Generation (MWh)": "Wind Generation (MWh)"}, inplace=True)

    # Plot marginal emissions impact.
    wind_output['Percent Change in MER (%)'] = (wind_output['Marginal Emissions Rate (lbs CO2/MWh) - After'] - wind_output['Marginal Emissions Rate (lbs CO2/MWh) - Before'])/wind_output['Marginal Emissions Rate (lbs CO2/MWh) - Before']
    wind_output.plot(x='Date', y='Percent Change in MER (%)')
    plt.show()

    # Group grid generation by date.
    daily_grid_output = grid_output.groupby('Date', as_index=False).agg({'Grid Generation (MWh)': 'sum', 'Emissions (lbs CO2)': 'sum'})
    daily_wind_output = wind_output.groupby('Date', as_index=False).agg({'Wind Generation (MWh)': 'sum', 'Avoided Emissions (lbs CO2)': 'sum'})

    # Construct load duration curve. 
    load_duration_curve = daily_wind_output.sort_values(by='Wind Generation (MWh)', ascending=False)
    load_duration_curve['Interval'] = 1
    load_duration_curve['Duration'] = load_duration_curve['Interval'].cumsum()
    load_duration_curve['Percentage'] = (load_duration_curve['Duration'] / 8760) * 100

    # Plot load duration curve. 
    load_duration_curve.plot(x='Percentage', y='Wind Generation (MWh)')
    plt.show()

    # Combine dataframes. 
    gen = daily_grid_output.merge(daily_wind_output, on='Date')

    # Calculate net generation and net emissions.
    gen['Net Generation (MWh)'] = gen['Grid Generation (MWh)'] - gen['Wind Generation (MWh)']
    gen['Net Emissions (lbs CO2)'] = gen['Emissions (lbs CO2)'] - gen['Avoided Emissions (lbs CO2)']

    # Plot grid and wind generation.
    gen.plot(x='Date', y=['Grid Generation (MWh)', 'Wind Generation (MWh)', 'Net Generation (MWh)'])
    plt.show()

    # Plot emissions and avoided emissions. 
    gen.plot(x='Date', y=['Emissions (lbs CO2)', 'Avoided Emissions (lbs CO2)', 'Net Emissions (lbs CO2)'])
    plt.show()