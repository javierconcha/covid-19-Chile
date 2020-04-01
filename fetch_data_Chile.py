#!/Users/javier.concha/opt/anaconda3/bin/python
# coding: utf-8
"""
Created on Thu Mar 26 11:58:01 2020

@author: javier.concha
"""
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import csv
import json
import datetime
import glob
import os
import subprocess

import fetch_data_minsal
#%%
geodata_json = 'geodata.json' # name for json data output
data_csv = 'data.csv' # name to output csv

data = [] 
coors_json = 'coors_Chile.json'
has_duplicate_data = 'Chile'

def geocode(country, province, latitude=None, longitude=None):
    # read existing data
    if os.path.exists(coors_json):
        with open(coors_json) as f:
            coors = json.load(f)
    else:
        coors = {}

    if province == '':
        location = country
    else:
    	location = f'{province}, {country}'

    latitude = coors[location]['latitude']
    longitude = coors[location]['longitude']

    return latitude, longitude

def merge_data():
    global total_days
    
    with open('data/Chile.csv') as file:
        total_days = len(file.readlines()) - 1
    print('TOTAL DAYS: '+str(total_days))    

    for filename in glob.glob('data/*.csv'):
        name = filename.replace('data/', '').replace('.csv', '')
        if ',' in name:
            x = name.split(',')
            province = x[0].strip()
            country = x[1].strip()
        else:
            province = ''
            country = name

        found = False
        for rec in data:
            if country == rec['country'] and province == rec['province']:
                found = True
                break

        if found:
            confirmed = rec['confirmed']
            recovered = rec['recovered']
            deaths = rec['deaths']
            index = len(confirmed) - 1
            time_str = confirmed[index]['time']

            with open(filename) as f:
                reader = csv.reader(f)
                for row in reader:
                    pass
                last_updated = datetime.datetime.fromisoformat(row[0]).\
                        astimezone(datetime.timezone.utc)
                last_updated_str = f'{last_updated.strftime("%Y/%m/%d %H:%M:%S UTC")}'
                if time_str > last_updated_str:
                    last_updated_str = time_str
                c = int(row[1])
                r = int(row[2])
                d = int(row[3])
                if c > confirmed[index]['count']:
                    print(f'data confirmed: {province}, {country}, {confirmed[index]["count"]} => {c}')
                    confirmed[index] = {
                        'time': last_updated_str,
                        'count': c
                    }
                if r > recovered[index]['count']:
                    print(f'data recovered: {province}, {country}, {recovered[index]["count"]} => {r}')
                    recovered[index] = {
                        'time': last_updated_str,
                        'count': r
                    }
                if d > deaths[index]['count']:
                    print(f'data deaths   : {province}, {country}, {deaths[index]["count"]} => {d}')
                    deaths[index] = {
                        'time': last_updated_str,
                        'count': d
                    }
        else:

            latitude, longitude = geocode(country, province)
            latitude = round(latitude, 4)
            longitude = round(longitude, 4)

            confirmed = []
            recovered = []
            deaths = []

            with open(filename) as f:
                reader = csv.reader(f)
                reader.__next__()
                for row in reader:
                    time = datetime.datetime.fromisoformat(row[0]).\
                            astimezone(datetime.timezone.utc)
                    time_str = f'{time.strftime("%Y/%m/%d %H:%M:%S UTC")}'
                    c = int(row[1])
                    r = int(row[2])
                    d = int(row[3])
                    confirmed.append({
                        'time': time_str,
                        'count': c
                    })
                    recovered.append({
                        'time': time_str,
                        'count': r
                    })
                    deaths.append({
                        'time': time_str,
                        'count': d
                    })

                print(f'data confirmed: {province}, {country}, {c}')
                print(f'data recovered: {province}, {country}, {r}')
                print(f'data deaths   : {province}, {country}, {d}')

            data.append({
                'country': country,
                'province': province,
                'latitude': latitude,
                'longitude': longitude,
                'confirmed': confirmed,
                'recovered': recovered,
                'deaths': deaths
            })


def sort_data():
    global data

    # sort records by confirmed, country, and province
    data = sorted(data, key=lambda x: (
        -x['confirmed'][len(x['confirmed'])-1]['count'],
        x['country'],
        x['province']))

def report_data():
    total_confirmed = total_recovered = total_deaths = 0
    for rec in data:
        country = rec['country']
        province = rec['province']
        latitude = rec['latitude']
        longitude = rec['longitude']
        index = len(rec['confirmed']) - 1
        c = rec['confirmed'][index]['count']
        r = rec['recovered'][index]['count']
        d = rec['deaths'][index]['count']
        if c == 0 or (country in has_duplicate_data and not province):
            continue
        print(f'final: {province}; {country}; {latitude}; {longitude}; {c}; {r}; {d}')
        total_confirmed += c
        total_recovered += r
        total_deaths += d

    print(f'Total confirmed: {total_confirmed}')
    print(f'Total recovered: {total_recovered}')
    print(f'Total deaths   : {total_deaths}')


def write_geojson():
    # create a new list to store all the features
    features = []
    # create a feature collection
    for i in range(0, len(data)):
        rec = data[i]
        country = rec['country']
        province = rec['province']
        index = len(rec['confirmed']) - 1
        if rec['confirmed'][index]['count'] == 0 and \
           rec['recovered'][index]['count'] == 0 and \
           rec['deaths'][index]['count'] == 0:
            continue
        features.append({
            'id': i,
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [rec['longitude'], rec['latitude']]
            },
            'properties': {
                'country': rec['country'],
                'province': rec['province'],
                'confirmed': rec['confirmed'],
                'recovered': rec['recovered'],
                'deaths': rec['deaths']
            }
        })

    # finally, build the output GeoJSON object and save it
    geodata = {
        'type': 'FeatureCollection',
        'features': features
    }

    with open(geodata_json, 'w') as f:
        f.write(json.dumps(geodata))

def write_csv():
    with open(data_csv, 'w') as f:
        f.write('province,country,latitude,longitude,category')
        for x in data[0]['confirmed']:
            date = x['time'].split(' ')[0].replace('/', '')
            f.write(f',utc_{date}')
        f.write('\n')
        for rec in data:
            country = rec['country']
            province = rec['province']
            index = len(rec['confirmed']) - 1
            if rec['confirmed'][index]['count'] == 0 and \
               rec['recovered'][index]['count'] == 0 and \
               rec['deaths'][index]['count'] == 0:
                continue
            if ',' in province:
                province = f'"{province}"'
            if ',' in country:
                country = f'"{country}"'
            latitude = rec['latitude']
            longitude = rec['longitude']
            for category in ('confirmed', 'recovered', 'deaths'):
                f.write(f'{province},{country},{latitude},{longitude},{category}')
                for i in range(len(rec[category]), total_days):
                    f.write(',0')
                for x in rec[category]:
                    f.write(f',{x["count"]}')
                f.write('\n')

def send_to_server():
    cmd1 = 'scp /Users/javier.concha/Desktop/Javier/2020_COVID-19_CHILE/covid-19-Chile/data.csv bfbrzn0q0yvx@www.sci-solve.com:/home/bfbrzn0q0yvx/public_html/covid-19-Chile'
    print(cmd1)
    prog = subprocess.Popen(cmd1, shell=True,stderr=subprocess.PIPE)
    out, err = prog.communicate()
    if err:
        print(err)
    else:
        print('data.csv uploaded to server!')

    cmd2 = 'scp /Users/javier.concha/Desktop/Javier/2020_COVID-19_CHILE/covid-19-Chile/geodata.json bfbrzn0q0yvx@www.sci-solve.com:/home/bfbrzn0q0yvx/public_html/covid-19-Chile'                
    print(cmd2)
    prog = subprocess.Popen(cmd2, shell=True,stderr=subprocess.PIPE)
    out, err = prog.communicate()
    if err:
        print(err)
    else:
        print('geodata.json uploaded to server!')



#%%	MAIN
if __name__ == '__main__':

    if fetch_data_minsal.main():
    # if True:  	
        merge_data()
    
        sort_data()
        report_data()
    
        write_geojson()
        write_csv()    
    
        send_to_server()
    else:
    	print('Data not updated!')


