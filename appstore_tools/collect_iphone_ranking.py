'''
Created on Jun 12, 2014

This is a tool to collect the current iTunes Appstore rankings for a user-defined list of countries.
Apps can be narrowed down to a ranking type or one or more categories.
Returned is a .csv file with the ranking of each app in each country,
as well as a list of how each of these apps are ranked in the other specified countries.
This provides a quick overview of how apps are ranked across different countries. 

@author: Kristian Slabbekoorn
'''
import json, requests
from datetime import datetime
from collections import OrderedDict
from pprint import pprint

# Country codes and names of country rankings to return.
CODES = OrderedDict((
        ('us', "US"),
        ('jp', "Japan"),
        ('gb', "UK"),
        ('au', "Australia"),
        ('ca', "Canada"),
        ('de', "Germany"),
        ('cn', "China"),
        ('fr', "France"),
        ('kr', "Korea"),
        ('it', "Italy"),
        ('es', "Spain"),
        ('ru', "Russia"),
))

# Type of apps to return.
# Possibilities: topfreeapplications, toppaidapplications, topgrossingapplications,
#                topfreeipadapplications, toppaidipadapplications, topgrossingipadapplications,
#                newapplications, newfreeapplications, newpaidapplications
TYPE = 'topgrossingapplications'

# Number of ranked apps to return (Max: 200).
LIMIT = 200

# Genre of apps. 0 is any app. 6014 is games only. See iTunes category codes for an extensive list:
# https://www.apple.com/itunes/affiliates/resources/documentation/genre-mapping.html
GENRE = 0


def write_to_csv(world_apps):
    csv_header_pre = "Title,Developer,Category,Price,Release date,Appstore link"
    
    for code in CODES:
        other_codes = [c for c in CODES if c != code]
        csv_header = csv_header_pre + "," + CODES.get(code) + " ranking"
        
        for c in other_codes:
            csv_header += "," + CODES.get(c) + " ranking"
        
        csv_body = csv_header + "\n"
        for country_apps in world_apps:
            if country_apps.get('code') == code:
                for app in country_apps.get('apps'):
                    date = app.get('release_date')[:-15]
                    date_str = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
                    
                    csv_body += '"%s","%s",%s,"%s",%s,%s' % (
                                app.get('title'), app.get('developer'), app.get('category'),
                                app.get('price'), date_str, app.get('appstore_link'))
                    
                    csv_body += ",%s" % app.get(code)
                    for c in other_codes:
                        csv_body += ",%s" % app.get(c)
                    csv_body += "\n"
        
        f = open('world.iphone.top.' + str(LIMIT) + '.ranking.' + TYPE + '.' + code + '.csv','w')    
        f.write(csv_body.encode('utf-8'))
        f.close()

if __name__ == '__main__':
    domain = 'https://itunes.apple.com/'
    path = '/rss/' + TYPE + '/genre=' + str(GENRE) + '/limit=' + str(LIMIT) + '/json'
    
    pprint("Collecting the top " + str(LIMIT) + " " + TYPE + " apps from " + domain + "...")

    world_apps = []
    
    for code in CODES:
        url = domain + code + path
        pprint("Retrieving " + url + "...")
        resp = requests.get(url)
        data = json.loads(resp.text)
        rank_counter = 1
        country_apps = { 'code': code,
                         'apps': [] }
        
        for app in data['feed']['entry']:
            country_app = {
                'id': app['id']['attributes']['im:id'],
                'title': app['im:name']['label'],
                'developer': app['im:artist']['label'],
                'category': app['category']['attributes']['term'],
                'price': app['im:price']['label'],
                'release_date': app['im:releaseDate']['label'],
                'appstore_link': app['link']['attributes']['href'],
                 code: rank_counter,
            }
            
            other_codes = [c for c in CODES if c != code]
            for c in other_codes:
                country_app[c] = '>' + str(LIMIT)
                
            rank_counter += 1
            country_apps.get('apps').append(country_app)
        
        world_apps.append(country_apps)
    
    pprint("All apps collected. Combining rankings...")
    
    for i in range(0, len(CODES)):
        domestic_apps = world_apps[i]
        for j in range(0, len(CODES)):
            if i != j:
                foreign_apps = world_apps[j]
                foreign_code = foreign_apps.get('code')
                
                for domestic_app in domestic_apps.get('apps'):
                    for foreign_app in foreign_apps.get('apps'):
                        if foreign_app.get('id') == domestic_app.get('id'):
                            domestic_app[foreign_code] = foreign_app.get(foreign_code)
                            break
    
    pprint("Writing result to .csv files...")
    write_to_csv(world_apps)
    pprint("Done!")
