"""
parisian_network.py, Tuesday, October 13th 2026
Displays the parisian network on a map with tailored colors.
"""

import pandas as pd
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt
import numpy as np

###
### Data recovery and useless attributes removal
###

## stops.txt
# stops.txt is a database where each row represents a track
# eg. Metro 14, Châtelet, track to Aéroport d'Orly.
stops = pd.read_csv("stops.txt")
stops.drop(labels = ['stop_code', 'stop_desc', 'zone_id', 'stop_url', 'location_type', 'stop_timezone', 'level_id', 'wheelchair_boarding', 'platform_code', 'stop_access'], axis= 1, inplace=True)

## trips.txt
# trips.txt is a database where each row represents a train trip from point A to point B
# eg. Train 123456 line 14, from Saint-Denis - Pleyel to Aéroport d'Orly.
trips = pd.read_csv("trips.txt")
trips.drop(labels=['service_id', 'trip_short_name', 'trip_headsign', 'block_id', 'shape_id', 'wheelchair_accessible', 'bikes_allowed'], axis=1, inplace=True)
routes = pd.read_csv("routes.txt")
routes.drop(labels=['agency_id', 'route_desc','route_url', 'route_sort_order'], axis=1, inplace=True)

# We drop buses to avoid collisions with metros whose short name is the same (eg. : Bus 14 and Metro 14)
routes = routes[routes['route_type']!=3]

## stop_times.txt
# stop_times.txt is a database where each row represents a scheduled train stop in a station
# eg. Train number 123456 , trip 123456, line 14 , direction Aéroport d'Orly, scheduled stop in Châtelet, arrival from Pyramides at 8 h 12 min 15 s a.m., depature for Gare de Lyon at 8 h 12 min 37 s.
stop_times = pd.read_csv("stop_times.txt")
stop_times.drop(labels=['start_pickup_drop_off_window', 'end_pickup_drop_off_window', 'pickup_type', 'drop_off_type', 'local_zone_id', 'stop_headsign', 'timepoint', 'pickup_booking_rule_id', 'drop_off_booking_rule_id'], axis=1, inplace=True)

## transfers.txt
# transfers.txt is a database where each row represents a transfert on foot in a hub
# eg. Arrival in Châtelet with line 1 from La Défense, minimum walking time to the track of line 14 to Aéroport d'Orly

transfers = pd.read_csv("transfers.txt")

list_routes = [str(k) for k in range(1, 15)]+['3B', '7B']+ ['A', 'B', 'C', 'D', 'E', 'H', 'J', 'K', 'L', 'N', 'P', 'R', 'U', 'V']

for route in list_routes:
    df = pd.merge(left=routes[(routes['route_long_name']==route)&((routes['route_type']==1)|(routes['route_type']==2))], right=trips, on='route_id', how='left')
    df = pd.merge(left=pd.merge(left=df, right=stop_times, on='trip_id', how='left'), right=stops, on='stop_id', how='left')
    df = df[df.groupby('trip_id')['stop_id'].transform('count')==df.groupby('trip_id')['stop_id'].transform('count').max()]
    df = df[df['trip_id']==df['trip_id'].values[0]]
    df = df.sort_values(by='stop_sequence', ascending=True)
    ## Smooth interpolation
    # To provide a beautiful chart we avoid broken lines and use scipy.interpolate to use splprep and splev built-in methods to create a smooth curve interpolating - AI generated.
    tck, u = splprep([df['stop_lon'], df['stop_lat']], s=0)
    unew = np.linspace(0, 1, 500)
    x_smooth, y_smooth = splev(unew, tck)
    ##
    plt.plot(x_smooth, y_smooth, linewidth=df['route_type'].values[0], c='#'+df['route_color'].values[0], label="Ligne lissée")
    plt.scatter(df['stop_lon'], df['stop_lat'], s=3*df['route_type'].values[0], c='#'+df['route_color'], zorder=3)

plt.gca().set_aspect('equal', adjustable='box')

plt.show()