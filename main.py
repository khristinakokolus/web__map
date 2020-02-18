from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from geopy.extra.rate_limiter import RateLimiter
import copy
import string
import folium


def get_location_of_user(latitude, longitude):
    '''
    (str, str) -> list
    Function returns the location of the user.

    >>> get_location_of_user("32.8246758", "-117.1559805")[:2]
    ['4646,', 'Convoy']
    '''
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    s = ''
    s += latitude + ', ' + longitude
    location = geolocator.reverse(s, language='en')
    loc = location.address.split()
    if loc[-1] == 'America':
        loc.append('USA')
    if loc[-1] == 'Kingdom':
        loc.append('UK')
    return loc


def locations(file, year, loc_lst):
    '''
    (NoneType, str, list) -> list

    Function that reads the file with film locations.
    '''
    locations = []
    with open(file, 'r') as f:
        for row in f:
            row = row.strip().split()
            j = 0
            new_lst = []
            for i in row:
                if '(' in i:
                    row[:j] = [' '.join(new_lst[:j])]
                    break
                else:
                    new_lst.append(i)
                    j += 1
            if len(row) > 1:
                row[1] = row[1].replace('(', '').replace(')', '')
                if row[1] == year and loc_lst[-1] in row:
                    locations.append(row)
            if 'USA' or 'Canada' in loc_lst:
                if len(locations) == 240:
                    break
        locations = locations[14:]
        return locations


def get_location(location_lst, loc_lst):
    '''
    (list, list) -> dict

    Function that returns the dictionary where
    keys are locations and values are films.

    >>> get_location([['Ty pomnish?', '2002', 'Kiev', 'Ukraine']], ['Ukraine'])
    {'Kiev Ukraine': ['Ty pomnish?']}
    '''
    new_dct = {}
    for sublist in location_lst:
        new_lst = []
        i = 1
        index = sublist.index(loc_lst[-1])
        if ')' in sublist[index - 1] or '(' in sublist[index - 1]:
            new_lst.append(loc_lst[-1])
            new2 = copy.copy(new_lst)
            new2 = ' '.join(new2)
            if new2 not in new_dct.keys():
                new_dct[new2] = [sublist[0]]
            else:
                new_dct[new2].append(sublist[0])
        else:
            while not sublist[index - i].isdigit():
                new_lst.append(sublist[index - i])
                i += 1
            new_lst.append(loc_lst[-1])
            new1 = copy.copy(new_lst)
            new1 = ' '.join(new1)
            if new1 not in new_dct.keys():
                new_dct[new1] = [sublist[0]]
            else:
                new_dct[new1].append(sublist[0])
    return new_dct


def location_identifier(locations_dct):
    '''
    (dict) -> dict

    Function to find the latitude and the
    longitude of the specific places and returns
    the dictionary where keys are coordinates and
    values films

    >>> location_identifier({'Kiev, Ukraine': ['Ty pomnish?']})
    {(50.4500336, 30.5241361): ['Ty pomnish?']}
    >>>
    '''
    geo_dct = {}
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    for key, value in locations_dct.items():
        try:
            location = geolocator.geocode(key)
            lst_loc = (location.latitude, location.longitude)
            geo_dct[lst_loc] = value
        except Exception:
            continue
    return geo_dct


def find_distance(geo_dct, latitude, longitude):
    '''
    (dict, str, str) -> dict

    Function that returns the distance between the inputted
    place and film locations

    >>> n = ['Ty pomnish?']
    >>> find_distance({(50.4500336, 30.5241361): n}, '49.841952', '24.0315921')
    {'467.401892504032': ['Ty pomnish?']}
    '''
    distance_dct = {}
    my_geo_lst = (latitude, longitude)
    for key, value in geo_dct.items():
        dist = great_circle(my_geo_lst, key)
        dist1 = str(dist).replace('Distance(', '').replace(')', '')
        dist1 = dist1.replace(' km', '')
        if dist1 == '0.0':
            distance_dct['0'] = value
        else:
            distance_dct[dist1] = value
    return distance_dct


def top_locations(distance_dct, geo_dct):
    '''
    (dict, dict) -> dict

    Function that returns dictionary with 10 or less locations.

    >>> n = ['Ty pomnish?']
    >>> top_locations({'467.401892504032': n}, {(50.4500336, 30.5241361): n})
    {(50.4500336, 30.5241361): ['Ty pomnish?']}
    '''
    total_dct = {}
    i = 1
    if len(distance_dct) <= 10:
        total_dct = copy.copy(distance_dct)
    else:
        while i != 10:
            key_min = min(distance_dct.keys())
            total_dct[key_min] = distance_dct[key_min]
            del distance_dct[key_min]
            i += 1
    new_dct = {}
    for key, value in geo_dct.items():
        if value in total_dct.values() and value not in new_dct.values():
            new_dct[key] = value
    return new_dct


def make_a_dict(totl):
    '''
    (dict) -> dict

    Function that сonverts the dictionary to another one.

    >>> make_a_dict({(50.4500336, 30.5241361): ['Ty pomnish?']})
    {'lat': [50.4500336], 'lon': [30.5241361], 'films': [['Ty pomnish?']]}
    '''
    new_dct = {'lat': [], 'lon': [], 'films': []}
    for key, value in totl.items():
        key1 = list(key)
        new_dct['lat'].append(key1[0])
        new_dct['lon'].append(key1[1])
        new_dct['films'].append(value)
    return new_dct


def popular_countries():
    '''
    (NoneType) -> dict

    Function that returns top 5 countries of
    cinematograph.
    '''
    con_dct = {'lat': [], 'lon': [], 'country': []}
    popular_countries = ['USA', 'UK', 'China', 'France', 'Japan']
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    for i in popular_countries:
        location = geolocator.geocode(i)
        loc = [location.latitude, location.longitude]
        con_dct['lat'].append(loc[0])
        con_dct['lon'].append(loc[1])
        con_dct['country'].append(i)
    return con_dct


def create_map(total_dct, con_dct, latitude, longitude):
    '''
    Function that creates html file with map.
    '''
    lat = total_dct['lat']
    lon = total_dct['lon']
    films = total_dct['films']

    map = folium.Map(location=[latitude, longitude], zoom_start=8)

    fg_fl = folium.FeatureGroup(name="Films")

    for lt, ln, fl in zip(lat, lon, films):
        fg_fl.add_child(folium.Marker(location=[lt, ln],
                                      radius=10,
                                      popup=', '.join(fl),))
    lat1 = con_dct['lat']
    lon1 = con_dct['lon']
    con = con_dct['country']

    def color(con):
        '''
        Function that returns the color depending
        on the country.
        '''

        if con == 'USA':
            return 'red'
        else:
            return 'orange'

    fg_fl_pop = folium.FeatureGroup(name="Top 5 countries of cinematograph")

    for lt, ln, con in zip(lat1, lon1, con):
        fg_fl_pop.add_child(folium.CircleMarker(location=[lt, ln],
                                                radius=10,
                                                popup=con,
                                                fill_color=color(con),
                                                color='red',
                                                fill_opacity=1))
    map.add_child(fg_fl)
    map.add_child(fg_fl_pop)
    map.add_child(folium.LayerControl())
    map.save('Map_with_films.html')


if __name__ == "__main__":
    year = input('Please enter a year you would like to have a map for: ')
    latitude = input('Please enter your latitude: ')
    longitude = input('Please enter your longitude: ')
    print('The map with markers is generating... ')
    location = get_location_of_user(latitude, longitude)
    films_lst = locations('locations.list', year, location)
    loc_film_dct = get_location(films_lst, location)
    address = location_identifier(loc_film_dct)
    print('Please wait a bit more...')
    distance = find_distance(address, latitude, longitude)
    top_loc = top_locations(distance, address)
    new_lst = make_a_dict(top_loc)
    pop_con = popular_countries()
    create_map(new_lst, pop_con, latitude, longitude)
    print('Finished.The map is saved in file Map_with_films.html.Have a look!')