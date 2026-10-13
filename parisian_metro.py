"""
parisian_metro.py, Tuesday, October 13th 2026
Gives some functions to compute expected route time between two stations on a given line and transfer time between two given lines in a hub.
"""

import pandas as pd

###
### Data recovery and useless attributes removal
###

## stops.txt
# stops.txt is a database where each row represents a track
# eg. Metro 14, Châtelet, track to Aéroport d'Orly.
stops = pd.read_csv("stops.txt")
stops.drop(labels = ['stop_code', 'stop_desc', 'zone_id', 'stop_url', 'location_type', 'stop_timezone', 'stop_lon', 'stop_lat', 'level_id', 'wheelchair_boarding', 'platform_code', 'stop_access'], axis= 1, inplace=True)

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

###
### Fuctions section
###

def stop_id(station:str, route:str, direction:int=0)->str:
    """
    Takes as input short names of a station and a route and gives
    --------------------------
    Parameters :
        station:str
            Station short name
        route:str
            Route short name
        direction:int (defaut 0)
            Direction id, 0 or 1
    --------------------------
        /!\ Accents, spaces and so on. eg. "Châtelet" and "Châtelet - Les Halles" are not considered as the same station.
    """
    m1 = pd.merge(routes[routes['route_short_name']==route], trips[trips['direction_id']==direction], on='route_id', how='left')
    m2 = pd.merge(stops[stops['stop_name']==station], stop_times, on='stop_id', how='left')
    m3 = pd.merge(m1, m2, on='trip_id', how='left')
    return m3.dropna().head(1)['stop_id'].values[0]

def route_time(route:str, from_name:str, to_name:str)->float:
    """
    Takes as input short names of a route and two stations and gives
    --------------------------
    Parameters :
        route:str
            Route short name
        from_station:str
            Station short name we are coming from
        to_station:str
            Station short name we are going to
    --------------------------
        /!\ Accents, spaces and so on. eg. "Châtelet" and "Châtelet - Les Halles" are not considered as the same station.
    """
    m = pd.merge(left=pd.merge(left=pd.merge(left=routes[routes['route_short_name']==route], right=trips, how='left', on='route_id'), right=stop_times, on='trip_id'), right=stops[(stops['stop_name']==from_name)|(stops['stop_name']==to_name)], how='left', on='stop_id').dropna()
    m['arr_sec'] = pd.to_timedelta(m['arrival_time']).dt.total_seconds()
    m['route_time'] = m.groupby('trip_id')['arr_sec'].diff().dropna()
    return m['route_time'].mean()

def transfert_time(from_name:str, to_name:str, station:str)->float:
    """
    Takes as input short names of a route and two stations and gives
    --------------------------
    Parameters :
        route:str
            Route short name
        from_station:str
            Station short name we are coming from
        to_station:str
            Station short name we are going to
    --------------------------
        /!\ Accents, spaces and so on. eg. "Châtelet" and "Châtelet - Les Halles" are not considered as the same station.

        We make no difference between both tracks of a given stop, we assume that the transfer time does not depend on the direction, which is almost true practically. Most of parisian corridors have two branchs, each of them has stairs to descempt on the track. Transfert times depend mostly on the line.
    """
    return transfers[(transfers['from_stop_id']==stop_id(station, from_name))&(transfers['to_stop_id']==stop_id(station, to_name))]['min_transfer_time'].values[0]