#!/home/bfbrzn0q0yvx/.local/bin/python3
# coding: utf-8
"""
Created on Sun Mar 29 13:45:50 2020
Pull data from Ministerio de Salud de Chile

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
import requests
import re
import datetime
import pytz
import os
import sys
import pandas as pd
import argparse
parser = argparse.ArgumentParser(description="To force execute without checking date in minsal website.")
parser.add_argument('-f2','--force2',action='store_true' ,help='The action to take (e.g. install, remove, etc.)')
parser.add_argument('-d2','--debug2',action='store_true' ,help='The action to take (e.g. install, remove, etc.)')
args = parser.parse_args()

# parser = argparse.ArgumentParser(description='Pull data from website of the "Ministerio de Salud de Chile" (Minsal).')
#%%
def main():

    url = 'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto3/TotalesPorRegion.csv'
    df = pd.read_csv(url, error_bad_lines=False)

    province_list = ['Arica y Parinacota','Tarapacá','Antofagasta','Atacama','Coquimbo','Valparaíso','Metropolitana'\
        ,'O’Higgins','Maule','Ñuble','Biobío','Araucanía','Los Ríos','Los Lagos','Aysén','Magallanes','Total']
    province_dict = {
        'Antofagasta':'Antofagasta',
        'Araucanía':'Araucania','Araucania':'Araucania',
        'Arica y Parinacota':'Arica y Parinacota',
        'Atacama':'Atacama',
        'Aysén':'Aysen','Aysen':'Aysen',
        'Biobío':'Bio Bio','Biobio':'Bio Bio','Bio Bio':'Bio Bio',
        'Coquimbo':'Coquimbo',
        'Los Lagos':'Los Lagos',
        'Los Ríos':'Los Rios','Los Rios':'Los Rios',
        'Magallanes':'Magallanes',
        'Maule':'Maule',
        'Metropolitana':'Metropolitana',
        'Ñuble':'Nuble','Nuble':'Nuble',
        'O’Higgins':'OHiggins',"O'Higgins":'OHiggins',
        'Tarapacá':'Tarapaca','Tarapaca':'Tarapaca',
        'Valparaíso':'Valparaiso','Valparaiso':'Valparaiso'
    }
    # paths depending of the OS. Local or server.
    if sys.platform == 'darwin':
        path_main = '/Users/javier.concha/Desktop/Javier/2020_COVID-19_CHILE/covid-19-Chile'
    elif sys.platform == 'linux':
        path_main = '/home/bfbrzn0q0yvx/projects/covid-19-Chile'
    
    for province in province_list:

        # Example cvs file;
        # time,confirmed,recovered,deaths
        # 2020-03-01 11:00:00-03:00,0,0,0
        # 2020-03-02 11:00:00-03:00,0,0,0

        print('------------------')
        print(province)
        df_acumulados = df[(df['Region'] == province) & (df['Categoria'] == 'Casos acumulados')]
        df_recuperados = df[((df['Region'] == province )|((df['Region'] == province.replace("’","'")))|((df['Region'] == province.replace("í","i")))) \
            & (df['Categoria'] == 'Casos confirmados recuperados')]
        df_fallecidos = df[(df['Region'] == province) & (df['Categoria'] == 'Fallecidos totales')]
        df_all = pd.concat([df_acumulados,df_recuperados,df_fallecidos]).rename(columns={'Categoria': 'time'}).set_index('time').fillna(0)
        df_all = df_all.T
        df_all = df_all.rename(columns={'Casos acumulados': 'confirmed', 'Casos confirmados recuperados': 'recovered', 'Fallecidos totales': 'deaths'})
        df_all = df_all.drop('Region',axis=0)
        df_all = df_all.reset_index()
        df_all = df_all.rename(columns={'index': 'time'})
        df_all.index = df_all.index.rename('index')
        df_all['confirmed'] = df_all['confirmed'].astype(int)
        df_all['recovered'] = df_all['recovered'].astype(int)
        df_all['deaths'] = df_all['deaths'].astype(int)

        df_all['time'] = df_all['time'].astype(str) + ' 12:00:00-03:00'
        date_github = df_all['time'].iloc[-1][:10]

        if not province == 'Total':
            csv_file = f'{province_dict[province]}, Chile.csv'
            path_to_local = os.path.join(path_main,'data',csv_file)
        else:
            path_to_local = os.path.join(path_main,'data','Chile.csv')

        df_local = pd.read_csv(path_to_local)
        date_local = df_local['time'].iloc[-1][:10]

        if date_github > date_local or args.force2:
            df_all.to_csv(path_to_local,index = False)
            flag_updated = True
        else:
            print(f'Date in github ({date_github}) is the same as local ({date_local}). csv file {province} NOT changed!')
            flag_updated = False

    return flag_updated                
    
#%%     
if __name__ == '__main__':
   main() 