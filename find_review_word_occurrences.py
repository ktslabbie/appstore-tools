# -*- coding: utf-8 -*-
'''
Created on Jun 12, 2014

This is a tool to find how often certain words are mentioned in the reviews for an app.
It takes a list of Appstore IDs as input and returns a csv file with the occurrence numbers of each word in each app,
as well as their context in the review.

@author: Kristian Slabbekoorn
'''
import json, sys, time, requests, os
from pprint import pprint

# The country to find reviews for.
COUNTRY = 'jp'

# The target words to look for.
TARGET_WORDS     = [ 
        [ u'英語',  ],
        [ u'日本語', ],
]

# The way to sort the reviews. Can also be: mostHelpful, 
SORT_BY = "mostRecent"

class RetryError(Exception):
    pass

def retryloop(attempts, timeout=None, delay=0, backoff=1):
    starttime = time.time()
    success = set()
    for i in range(attempts): 
        success.add(True)
        yield success.clear
        if success:
            return
        duration = time.time() - starttime
        if timeout is not None and duration > timeout:
            break
        if delay:
            time.sleep(delay)
            delay = delay * backoff

    e = sys.exc_info()[1]

    # No pending exception? Make one
    if e is None:
        try: raise RetryError
        except RetryError as e: pass

    # Decorate exception with retry information:
    e.args = e.args + ("on attempt {0} of {1} after {2:.3f} seconds".format(i, attempts + 1, duration),)

    raise

if __name__ == '__main__':
    domain = 'https://itunes.apple.com/'

    out_string = ''
    f = open('apps.txt')
    lines = f.readlines()
    f.close()
    print str(len(lines)) + " app IDs contained."
    
    try:
        os.remove('result.csv')
    except OSError:
        pass
    
    f2 = open('result.csv','a')
    header = 'App ID,Title,Rating (Bayesian),Rating count,Term hits,Reviews\n'
    f2.write(header.encode('utf-8'))
    
    for line in lines:
        split = line.split(',')
        app_id = split[0]
        bayesian_rating = split[1].strip()
        rating_count = split[2].strip()
        
        url = domain + COUNTRY + '/rss/customerreviews/id=' + app_id + '/sortBy=' + SORT_BY + '/json'
        pprint("Retrieving " + url + "...")
        json_exists = True
        
        for retry in retryloop(40, timeout=120, delay=1, backoff=2):
            try:
                resp = requests.get(url)
                data = json.loads(resp.text)
            except ValueError:
                print("ValueError: No JSON object could be decoded. Ignore this app and continue...")
                json_exists = False
                break
            except Exception:
                print("Connection failed. Retrying...")
                retry()
        
        if not json_exists:
            continue
        
        feed = data['feed']
        if 'entry' in feed and len(feed['entry']) > 1:
            hit_cnt = 0
            hit_rev = u''
            try:
                app = feed['entry'][0]
            except KeyError:
                continue
            
            app_title = u'"' + app['im:name']['label'] + '"'
            
            print "Checking reviews for " + app_title + " (" + app_id + ")..."
            
            feed['entry'].pop(0)
            for review in feed['entry']:
                text = u'' + review['title']['label'] + review['content']['label']
                text = text.replace('\n', ' ').strip()
                
                #print "Found review: " + text
    
                for word_group in TARGET_WORDS:
                    group_count = len(word_group)
                    
                    for word in word_group:
                        if word in text:
                            print "Word " + word + " contained!"
                            group_count -= 1
                            if group_count is 0:
                                #print "All words in group contained!"
                                hit_rev += ',"' + text + '"'
                                hit_cnt += 1
            
            if hit_cnt > 0:
                out_string = app_id + ',' + app_title + ',' + bayesian_rating + ',' + rating_count + ',' + str(hit_cnt) + hit_rev + '\n'
                f2.write(out_string.encode('utf-8'))
        
    f2.close()
