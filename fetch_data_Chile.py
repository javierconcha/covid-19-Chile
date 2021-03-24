#!/home/bfbrzn0q0yvx/.local/bin/python3
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
from git import Repo
import sys
import argparse
parser = argparse.ArgumentParser(description="Create data to plot to in the index.html")
parser.add_argument('-v','--verbose',action='store_true' ,help='Verbose mode')
parser.add_argument('-f','--force',action='store_true' ,help='To force execute without checking Minsal website')
parser.add_argument('-n','--noupload',action='store_true' ,help='No uploading to the server')

args = parser.parse_args()


import fetch_data_minsal

if sys.platform == 'darwin':
    path_main = '/Users/javier.concha/Desktop/Javier/2020_COVID-19_CHILE/covid-19-Chile'
elif sys.platform == 'linux':
    path_main = '/home/bfbrzn0q0yvx/projects/covid-19-Chile'

#%%
geodata_json = os.path.join(path_main,'geodata.json') # name for json data output
data_csv = os.path.join(path_main,'data.csv') # name to output csv

data = [] 
coors_json = os.path.join(path_main,'coors_Chile.json')
has_duplicate_data = 'Chile'

def geocode(country, province, latitude=None, longitude=None):
    # read existing data
    if os.path.exists(coors_json):
        with open(coors_json) as f:
            coors = json.load(f)
    else:
        print('coors_json NOT found!')
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
    
    with open(os.path.join(path_main,'data/Chile.csv')) as file:
        total_days = len(file.readlines()) - 1
    print('TOTAL DAYS: '+str(total_days))    


    for filename in glob.glob(path_main+'/data/*.csv'):
        # print(filename)
        name = filename.split('/')[-1].replace('.csv', '')
        # print(name)
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
            time = confirmed[index]['time']

            path_file = os.path.join(path_main,filename[2:])
            print(path_file)
            with open(path_file) as f:
                reader = csv.reader(f)
                for row in reader:
                    pass
                last_updated = datetime.datetime.fromisoformat(row[0]).\
                        astimezone(datetime.timezone.utc)
                if time > last_updated:
                    last_updated = time
                c = int(row[1])
                r = int(row[2])
                d = int(row[3])
                if c > confirmed[index]['count']:
                    print(f'data confirmed: {province}, {country}, {confirmed[index]["count"]} => {c}')
                    confirmed[index] = {
                        'time': last_updated,
                        'count': c
                    }
                if r > recovered[index]['count']:
                    print(f'data recovered: {province}, {country}, {recovered[index]["count"]} => {r}')
                    recovered[index] = {
                        'time': last_updated,
                        'count': r
                    }
                if d > deaths[index]['count']:
                    print(f'data deaths   : {province}, {country}, {deaths[index]["count"]} => {d}')
                    deaths[index] = {
                        'time': last_updated,
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
                        'time': time,
                        'count': c
                    })
                    recovered.append({
                        'time': time,
                        'count': r
                    })
                    deaths.append({
                        'time': time,
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
            print('-------------------')
            print('From Chile.csv:')
            print(f'Total confirmed: {c}')
            print(f'Total recovered: {r}')
            print(f'Total deaths   : {d}')
            continue
        print(f'final: {province}; {country}; {latitude}; {longitude}; {c}; {r}; {d}')
        total_confirmed += c
        total_recovered += r
        total_deaths += d
    print('Calculated from the provinces:')
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

    def convert_time(x):
        if isinstance(x, datetime.datetime):
            return int(x.timestamp())

    with open(geodata_json, 'w') as f:
        f.write(json.dumps(geodata, default=convert_time))
        if args.verbose:
            print('geodata.json created.')

def write_csv():
    with open(data_csv, 'w') as f:
        f.write('province,country,latitude,longitude,category')
        for x in data[0]['confirmed']:
            date = x['time'].strftime("%Y%m%d")
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

    if sys.platform == 'darwin': # for Mac
        cmd1 = 'scp '+path_main+'/data.csv bfbrzn0q0yvx@www.sci-solve.com:/home/bfbrzn0q0yvx/public_html/covid-19-Chile'
        print(cmd1)
        prog = subprocess.Popen(cmd1, shell=True,stderr=subprocess.PIPE)
        out, err = prog.communicate()
        if err:
            print(err)
        else:
            print('data.csv uploaded to server!')

        cmd2 = 'scp '+path_main+'/geodata.json bfbrzn0q0yvx@www.sci-solve.com:/home/bfbrzn0q0yvx/public_html/covid-19-Chile'                
        print(cmd2)
        prog = subprocess.Popen(cmd2, shell=True,stderr=subprocess.PIPE)
        out, err = prog.communicate()
        if err:
            print(err)
        else:
            print('geodata.json uploaded to server!')

        cmd3 = 'scp '+path_main+'/*.html bfbrzn0q0yvx@www.sci-solve.com:/home/bfbrzn0q0yvx/public_html/covid-19-Chile'                
        print(cmd3)
        prog = subprocess.Popen(cmd3, shell=True,stderr=subprocess.PIPE)
        out, err = prog.communicate()
        if err:
            print(err)
        else:
            print('/*.html uploaded to server!')

    elif sys.platform == 'linux': # in the server
        cmd1 = 'cp '+path_main+'/data.csv /home/bfbrzn0q0yvx/public_html/covid-19-Chile'
        print(cmd1)
        prog = subprocess.Popen(cmd1, shell=True,stderr=subprocess.PIPE)
        out, err = prog.communicate()
        if err:
            print(err)
        else:
            print('data.csv uploaded to server!')

        cmd2 = 'cp '+path_main+'/geodata.json /home/bfbrzn0q0yvx/public_html/covid-19-Chile'                
        print(cmd2)
        prog = subprocess.Popen(cmd2, shell=True,stderr=subprocess.PIPE)
        out, err = prog.communicate()
        if err:
            print(err)
        else:
            print('geodata.json uploaded to server!')

        cmd3 = 'cp '+path_main+'/*.html /home/bfbrzn0q0yvx/public_html/covid-19-Chile'                
        print(cmd3)
        prog = subprocess.Popen(cmd3, shell=True,stderr=subprocess.PIPE)
        out, err = prog.communicate()
        if err:
            print(err)
        else:
            print('*.html uploaded to server!')


def git_push():
    PATH_OF_GIT_REPO = os.path.join(path_main,'.git')  # make sure .git folder is properly configured
    COMMIT_MESSAGE = 'Last update from Minsal.'
    try:
        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.add(path_main+'/data/')
        repo.git.add(path_main+'/data.csv')
        repo.git.add(path_main+'/geodata.json')
        repo.index.commit(COMMIT_MESSAGE)
        origin = repo.remote(name='origin')
        origin.push()
    except:
        print('Some error occured while pushing the code using GitPython')
        cmd1 = 'git -C '+path_main+' push origin master'
        print('Trying: '+cmd1)
        prog = subprocess.Popen(cmd1, shell=True,stderr=subprocess.PIPE)
        out, err = prog.communicate()
        if err:
            print(err)
        else:
            print(out)


#%%	MAIN
if __name__ == '__main__':

    if fetch_data_minsal.main() or args.force:
#    if True: 	
        merge_data()
    
        sort_data()
        report_data()
    
        write_geojson()
        write_csv()    
        if not args.noupload:
            send_to_server()
        
            git_push()
    else:
    	print('Data not updated!')


