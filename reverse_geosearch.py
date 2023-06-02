import json
import requests

"""
Usage:
CSV file must have headers with 'latitude' and 'longitude', 
and use ';' as value separator

Will produce a CVS file with ';' as separator, and headers:
Lat, Lon, Address, Zip4, Municipality, District
"""

# Unmutable variables ======================================================== 
base_uri = 'http://nominatim.openstreetmap.org/reverse?format=jsonv2'
base_lat = '&lat='
base_lon = '&lon='


# File manipulators ==========================================================
def get_input_data(filename):
    """
	filename - name of the file or the complete path if not in
			   the same directory has the file
	"""
    try:
        with open(filename, 'r') as file:
            data = file.readlines()
        return data
    except Exception as ex:
        print('Error opening file to read')
        print(ex)


def write_output_data(filename, lines):
    try:
        with open(filename, 'w') as file:
            for line in lines:
                file.write(line[0])
        return True
    except Exception as ex:
        print('Error opening file to write')
        print(ex)


# Fetch data and format data from nominatim ==================================
def fetch(lat, lon):
    try:
        r = requests.get(url=base_uri + base_lat + lat + base_lon + lon)
        return r.text
    except Exception as ex:
        print('Erros fetching data from nominatin')
        print(ex)


def format_output_line(lat_orig, lon_orig, json_data):
    """
	fetched_data - raw response from nominatim API
	LatOriginal, LonOriginal, Lat, Lon, Address, Zip4, Municipality, Country
	"""
    fetched_data = json.loads(json_data)

    lat = fetched_data['lat']  # latitude
    lon = fetched_data['lon']  # longitude
    address = fetched_data['address']  # other dict with remaining values

    # the remaining values could not exist............................
    cou = ''
    try:
        cou = address['county']
    except KeyError:
        print(f'coords: {lat}, {lon} get no county')

    mun = ''  # municipality
    try:
        mun = address['municipality']
    except KeyError:
        print(f'coords: {lat}, {lon} get no municipality')

    num = ''  # house number
    try:
        num = address['house_number']
    except KeyError:
        print(f'coords: {lat}, {lon} get no house number')

    street = ''  # street / road
    try:
        street = address['street']
    except KeyError:
        try:
            street = address['road']
        except KeyError:
            print(f'coords: {lat}, {lon} get no street')

    zp4 = ''  # postal code
    try:
        zp4 = address['postcode']
    except KeyError:
        print(f'coords: {lat}, {lon} get no postal code')

    return [f'{lat_orig};{lon_orig};{lat};{lon};{street}, {num};{zp4};{cou};{mun}\n']


# main loop ==================================================================
def let_magic_happen(filename):
    # open and manipulate input data ---------------------------------
    in_data = get_input_data(filename)
    headers = []
    values = []
    for line in in_data:
        if not headers:
            headers = line.strip().lower().split(';')
        else:
            values.append(line.strip().replace(',', '.').split(';'))

    # prepare and get output data ------------------------------------
    idx = {'lat': headers.index('latitude'), 'lon': headers.index('longitude')}
    output_data = [['Latitude_Original;Longitude_Original;Latitude;Longitude;Address;Zip4;Concelho;Distrito\n']]
    previous_coords = []
    previous_line = []
    for value in values:
        # if we already have fetch the data, don't fetch again
        lat = value[idx['lat']]
        lon = value[idx['lon']]
        if [lat, lon] != previous_coords:
            previous_line = format_output_line(lat, lon, fetch(lat, lon))
            previous_coords = [lat, lon]
        output_data.append(previous_line)

    # write output file ----------------------------------------------
    done = write_output_data(f'moradas_{filename}', output_data)

    # job done -------------------------------------------------------
    if done:
        print('File saved with success. All done.')


# start the script automaticaly ==============================================
if __name__ == '__main__':
    filename = 'NOVO.csv'
    let_magic_happen(filename)
