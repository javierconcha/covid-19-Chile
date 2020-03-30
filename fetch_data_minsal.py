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
#%%

# def fetch_data_from_minsal():
minsal_url = 'https://www.minsal.cl/nuevo-coronavirus-2019-ncov/casos-confirmados-en-chile-covid-19/'
minsal_re = '<tr[^<]*>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<td[^<]*>(.*?)<\/td>[^<]*<\/tr>'

# res = requests.get(minsal_url).content.decode()
# matches = re.search(minsal_re, res, re.DOTALL)

res = requests.get(minsal_url)
matches = re.finditer(minsal_re, res.text) 

if not matches:
    print('Fetching Data from Minsal failed')
else:    
    print('Fetching Data from Minsal matched')
    
flag_first = 1    

country = 'Chile'

for m in matches:
    if flag_first == 1:
        flag_first = 0
    else:
        if not m[1][0:8] == '<strong>':
            province = m[1]
            confirmed = int(m[3].replace('.', ''))
            deaths = int(m[5].replace('.', ''))
            
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
                province = 'Biobio'
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
        
        recovered = 0
        print('---------------')
        print('country :' +country)
        print('province: '+province)
        print('confirmed: '+str(confirmed))
        print('recovered: '+str(recovered))
        print('deaths: '+str(deaths))
            
