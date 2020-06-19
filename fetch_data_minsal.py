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
import argparse
parser = argparse.ArgumentParser(description="To force execute without checking date in minsal website.")
parser.add_argument('-f2','--force2',action='store_true' ,help='The action to take (e.g. install, remove, etc.)')
args = parser.parse_args()

# parser = argparse.ArgumentParser(description='Pull data from website of the "Ministerio de Salud de Chile" (Minsal).')


def replace_sym(str_to_replace):
    str_to_replace = str_to_replace.replace('.','')
    str_to_replace = str_to_replace.replace('*','')
    return str_to_replace
#%%
def main():
    # def fetch_data_from_minsal():
    minsal_url = 'https://www.minsal.cl/nuevo-coronavirus-2019-ncov/casos-confirmados-en-chile-covid-19/'
    minsal_re = '<tr[^<]*>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>'
    # actives_minsal_re = 'Casos recuperados a nivel nacional [\w-]*<\/strong><\/td>[^<]*<td[^<]*><strong>(.*?)<\/strong><\/td>'
    actives_minsal_re = 'px;"><strong>(.*\d)</strong></td>'
    date_last_update_re = 'Informe corresponde al (.*?)[^>]*\.'
    res = requests.get(minsal_url)

    # paths depending of the OS. Local or server.
    if sys.platform == 'darwin':
        path_main = '/Users/javier.concha/Desktop/Javier/2020_COVID-19_CHILE/covid-19-Chile'
    elif sys.platform == 'linux':
        path_main = '/home/bfbrzn0q0yvx/projects/covid-19-Chile'
    
    
    #%% get last update date
    print('--------------')
    if not re.search(date_last_update_re, res.text):
        print('Match NOT found for last date from Minsal website.')
    else:    
        print('Match FOUND for last update from Minsal website.')    
        match_last_update = re.finditer(date_last_update_re, res.text)     
        for m0 in match_last_update:
            last_year = m0[0].split(' ')[7][:-1]
            last_month = m0[0].split(' ')[5]
            last_day = m0[0].split(' ')[3]

            if len(last_day) == 1:
                last_day = '0'+last_day
            
            if last_month == 'enero':
                last_month = '01'
            elif last_month == 'febrero':
                last_month = '02'
            elif last_month == 'marzo':
                last_month = '03'
            elif last_month == 'abril':
                last_month = '04'
            elif last_month == 'mayo':
                last_month = '05'
            elif last_month == 'junio':
                last_month = '06'
            elif last_month == 'julio':
                last_month = '07'
            elif last_month == 'agosto':
                last_month = '08'
            elif (last_month == 'septiembre' or last_month == 'setiembre'):
                last_month = '09'
            elif last_month == 'octubre':
                last_month = '10'
            elif last_month == 'noviembre':
                last_month = '11'
            elif last_month == 'diciembre':
                last_month = '12'
            last_date_str = last_year+'-'+last_month+'-'+ last_day
    
    #%% today's date
    now = datetime.datetime.now()
    print('Today is: '+str(now))
    now_str = now.strftime("%Y-%m-%d")
    print(f"Today's date is: {now_str}")
    
    if now_str == last_date_str or args.force2: # if date in Minsal website is equal to today
        #%% fetch table with data
        if not re.search(minsal_re, res.text):
            print('Match NOT found for table from Minsal website')
        else:    
            print('Match FOUND for table from Minsal website')
            matches = re.finditer(minsal_re, res.text)
            country = 'Chile'
            # time in Chile
            chile_now = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone("America/Santiago"))
            chile_now_str = chile_now.strftime("%Y-%m-%d %H:%M:%S")

            for m in matches:
                print('---------------')
                if not m[1][0:8] == '<strong>':
                    province = m[1]
                    confirmed = int(replace_sym(m[2]))
                    deaths = int(replace_sym(m[7]))
                    actives_minsal = 0
                    # change special characters to write csv data
                    if province[0:3] == 'Ari':
                        province = 'Arica y Parinacota'
                    elif province[0:3] == 'Tar':
                        province = 'Tarapaca'
                    elif province[0:3] == 'Val':
                        province = 'Valparaiso'
                    elif province[0] == 'O':
                        province = 'OHiggins' 
                    elif province[1:] == 'uble':
                        province = 'Nuble'
                    elif province[0:3] == 'Bio':
                        province = 'Bio Bio'
                    elif province[0:3] == 'Ara':
                        province = 'Araucania'
                    elif (province[0:3] == 'Los' and province[4] == 'R'):
                        province = 'Los Rios'  
                    elif (province[0:3] == 'Los' and province[4] == 'L'):
                        province = 'Los Lagos'    
                    elif province == 'Aysén':
                        province = 'Aysen'                  
                else:
                    province = '' # for Chile.csv
                    confirmed = int(m[2].replace('.', '').split('>')[1].split('<')[0])
                    deaths = int(m[7].replace('.', '').split('>')[1].split('<')[0])
        
                    # fetch total actives_minsal from minsal website
                    if not re.search(actives_minsal_re, res.text):
                        print('Match NOT found for actives_minsal from Minsal website!')
                    else:
                        print('Match FOUND for actives_minsal from Minsal website!')
                        match_actives_minsal = re.finditer(actives_minsal_re, res.text)
                        for match in match_actives_minsal:
                            actives_minsal = int(match[1].replace('.', ''))         

                print('country :' +country)
                print('province: '+province)
                print('confirmed: '+str(confirmed))
                print('actives_minsal: '+str(actives_minsal))
                print('deaths: '+str(deaths))
                if not province == '':#Chile
                    new_line = chile_now_str+'-03:00,'+str(confirmed)+',0,'+str(deaths)+'\n'
                    csv_file = province+', '+country+'.csv'
                else:
                    new_line = chile_now_str+'-03:00,'+str(confirmed)+','+str(confirmed-deaths-actives_minsal)+','+str(deaths)+'\n'
                    csv_file = country+'.csv' 
                path2csv = os.path.join(path_main,'data',csv_file)
                # write csv file
                with open(path2csv, 'r+') as f:
                    lines = f.read().splitlines()
                    last_line = lines[-1]
                    print(last_line)
                    if now_str == last_line[:10]:
                        print('Same dates: '+now_str)
                        print('File NOT updated.')
                        if not province == '':
                            return False
                    else:   
                        f.write(new_line)
                        print('File updated.')
        flag_updated = True                
    else:
        print('Last date in website is yesterday ('+last_date_str+')!')  
        flag_updated = False      

    return flag_updated                
    
#%%     
if __name__ == '__main__':
   main()  

            
