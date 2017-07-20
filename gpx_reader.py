"""
Code to process .gpx files downloaded from strava.
"""

# ------------------ Packages -------------------- #

import re

import os.path

import datetime

import pandas as pd

from bs4 import BeautifulSoup

# ----------------- Functions -------------------- #

def extract_values (xml_values):
    """Extract values from vector containing xml subheaders."""
    values = []
    for val in xml_values:
        values.append(int(re.findall('\d+', str(val))[0]))
    return values


def extract_date_times (xml_values):
    """Extract date & time values from vector containing xml subheaders."""
    date_times = []
    for i in xml_values:
        date_time = list(map(int, re.findall('\d+', str(i))))
        date_time = datetime.datetime(date_time[0],
                                      date_time[1],
                                      date_time[2],
                                      date_time[3],
                                      date_time[4],
                                      date_time[5])
        date_times.append(date_time)
    return date_times


def extract_data (points):
    """Code to..."""
    latitudes, longitudes, elevations, times, heart_rates = [], [], [], [], []
    heart_rate_data = True
    for pt in activity_points:
        latitudes.append(pt['lat'])
        longitudes.append(pt['lon'])
        elevations.append(pt.ele)
        times.append(pt.time)
        try:
            heart_rates.append(pt.find_all('gpxtpx:hr')[0])
        except:
            heart_rates.append('No HR data')
            heart_rate_data = False

    elevations = extract_values(elevations)
    times = extract_date_times(times)
    if heart_rate_data:
        heart_rates = extract_values(heart_rates)

    activity_dict = {'Latitude': latitudes,
                     'Longitude': longitudes,
                     'Elevation': elevations,
                     'Time_Stamp': times,
                     'HR': heart_rates}

    activity_df = pd.DataFrame(activity_dict)

    return activity_df


def calculate_hr_zones (df):
    """Function actegories HR data into zones."""
    df['HR_Zone'] = 'Recovery'
    df.loc[df['HR'] > 118, 'HR_Zone'] = 'Z1'
    df.loc[df['HR'] > 128, 'HR_Zone'] = 'Z2'
    df.loc[df['HR'] > 147, 'HR_Zone'] = 'Z3'
    df.loc[df['HR'] > 161, 'HR_Zone'] = 'Z4'
    df.loc[df['HR'] > 175, 'HR_Zone'] = 'Z5'
    df.loc[df['HR'] > 183, 'HR_Zone'] = 'Z6'
    return df


path = './Activities/'
gpx_filenames = [path + x for x in os.listdir(path) if '.DS_Store' not in x]

col_names = ['Ride_ID', 'Time_Stamp', 'Latitude',
             'Longitude', 'Elevation', 'HR', 'HR_Zone']
df = pd.DataFrame(columns = col_names)

for filename in gpx_filenames:
    print(filename)

    with open(filename, 'r') as f:
        file = BeautifulSoup(f, 'lxml')

    activity_points = file.find_all('trkpt')

    activity_df = extract_data(activity_points)
    activity_df['Ride_ID'] = filename
    activity_df = calculate_hr_zones(activity_df)

    print(activity_df.shape)
    df = df.append(activity_df)
    print(df.shape)

df.to_csv('all_activities.csv', index = False)
