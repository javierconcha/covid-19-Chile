#!/usr/bin/env python3
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
import fetch_data_Chile
#%%
def main():
    # def fetch_data_from_minsal():
    minsal_url = 'https://www.minsal.cl/nuevo-coronavirus-2019-ncov/casos-confirmados-en-chile-covid-19/'
    minsal_re = '<tr[^<]*>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<\/tr>'
    recovered_re = 'Casos recuperados a nivel nacional*<\/strong><\/td>[^<]*<td[^<]*><strong>(.*?)<\/strong>'
    date_last_update_re = 'Informe corresponde al (.*?)[^>]*\.'
    res = requests.get(minsal_url)
    
    #%% get last update date
    match_last_update = re.finditer(date_last_update_re, res.text) 
    if not match_last_update:
        print('Fetching Last Update from Minsal failed')
    else:    
        print('Fetching Last Update from Minsal matched')
    
    for m0 in match_last_update:
        last_year = m0[0].split(' ')[7][:-1]
        last_month = m0[0].split(' ')[5]
        last_day = m0[0].split(' ')[3]
        
        if last_month == 'marzo':
            last_month = '03'
        elif last_month == 'abril':
            last_month = '04'
        elif last_month == 'mayo':
            last_month = '05'
        last_date_str = last_year+'-'+last_month+'-'+ last_day
        print(last_date_str)
    
    #%% today's date
    now = datetime.datetime.now()
    str_year = str(now.year)
    str_month = str(now.month)
    str_day = str(now.day)
    if len(str_month) == 1:
        str_month = '0'+str_month
    if len(str_day)==1:
        str_day = '0'+str_day
    now_str =str_year+'-'+str_month+'-'+str_day
    
    if now_str == last_date_str:
        # fetch table with data
        matches = re.finditer(minsal_re, res.text) 
        if not matches:
            print('Fetching Data from Minsal failed')
        else:    
            print('Fetching Data from Minsal matched')
        
        flag_first = 1 # for the first element of the table from minsal, which is not useful
        
        country = 'Chile'
        
        for m in matches:
            print('---------------')
            if flag_first == 1:
                flag_first = 0
            else:
                if not m[1][0:8] == '<strong>':
                    province = m[1]
                    confirmed = int(m[3].replace('.', ''))
                    deaths = int(m[5].replace('.', ''))
                    recovered = 0
                    # change special characters to write csv data
                    if province == 'Tarapacá':
                        province = 'Tarapaca'
                    elif province == 'Valparaíso':
                        province = 'Valparaiso'
                    elif province == 'O&#8217;Higgins':
                        province = 'OHiggins' 
                    elif province == 'Ñuble':
                        province = 'Nuble'
                    elif province == 'Biobío':
                        province = 'Bio Bio'
                    elif province == 'Araucanía':
                        province = 'Araucania'
                    elif province == 'Los Ríos':
                        province = 'Los Rios'                
                    elif province == 'Aysén':
                        province = 'Aysen'                  
                else:
                    province = ''
                    confirmed = int(m[3].replace('.', '').split('>')[1].split('<')[0])
                    deaths = int(m[5].replace('.', '').split('>')[1].split('<')[0])
        
                    match_recovered = re.finditer(recovered_re, res.text)
                    if not match_recovered:
                        print('Fetching Recovered from Minsal failed')
                    else:    
                        print('Fetching Recovered from Minsal matched')
                        for match in match_recovered:
                            recovered = int(match[1].replace('.', ''))
                
                print('country :' +country)
                print('province: '+province)
                print('confirmed: '+str(confirmed))
                print('recovered: '+str(recovered))
                print('deaths: '+str(deaths))
                new_line = str_year+'-'+str_month+'-'+str_day+' 11:00:00-03:00,'+str(confirmed)\
                    +','+str(recovered)+','+str(deaths)+'\n'
                print(new_line)        
                if not province == '':
                    scv_file = province+', '+country+'.csv'
                else:
                    scv_file = country+'.csv' 
                path2csv = 'data/'+scv_file   
                with open(path2csv, 'r+') as f:
                    lines = f.read().splitlines()
                    last_line = lines[-1]
                    print(last_line)
                    if now_str == last_line[:10]:
                        print('Same dates: '+now_str)
                        print('File NOT updated.')
                    else:
                        f.write(new_line)
                        print('File updated.')
                        
    else:
        print('Last date in website is yesterday!')                    
    
#%%     
if __name__ == '__main__':
   main()  

            
