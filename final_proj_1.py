# -*- coding: UTF-8 -*-
#################################
##### Name: Ziyun Wang ##########
##### Uniqname: ziyun ###########
#################################

from bs4 import BeautifulSoup
import requests
import json
import time
import numpy as np
import sqlite3

DB = 'check.sqlite'
CACHE_FILENAME = "cache.json"
base_url = "https://www.fragrantica.com"
parent_company_url = "https://www.fragrantica.com/parent-company/"
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',}



def open_cache(filename=CACHE_FILENAME):
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    cache_dict: dict
        The opened cache
    '''
    try:
        cache_file = open(filename, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def company_url_dict(url):
    ''' Make a dictionary that maps subsidiary or parent company names to page urls from pages like
    "https://www.fragrantica.com/parent-company/" (providing a list of links for parent company) and 
    "https://www.fragrantica.com/parent-company/Lalique+Group+SA.html" (providing a list of links for 
    subsidiary)

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'Lalique Group SA':'https://www.fragrantica.com/parent-company/Lalique+Group+SA.html', ...}
    '''
    company_url = {}
    
    soup = get_soup_helper(url)
    if soup is not None:
        spans = soup.find_all('span',class_="clickcatcher")
        for s in spans:
            a = s.find_parent('a')
            company_url[a.get_text().strip('\n')] = base_url + a['href']

    return company_url

def perfume_url_list(url):
    ''' Make a dictionary that maps parent company names to page urls from 
    "https://www.fragrantica.com/parent-company/"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'Lalique Group SA':'https://www.fragrantica.com/parent-company/Lalique+Group+SA.html', ...}
    '''
    perfume_url = []
    
    soup = get_soup_helper(url)
    if soup is not None:
        spans = soup.find_all('span',class_="link-span")
        for s in spans:
            a = s.find_parent('a')
            tags = a.find_all('br')
            if tags == [] and a['href'][:4] == '/per':
                perfume_url.append(base_url + a['href'])
                # print(a.get_text().strip('\n'))
            
    return perfume_url



def get_soup_helper(url):
    ''' Get soup from web pages or cache.json

    Parameters
    ----------
    url

    Returns
    -------
    BeautifulSoup
        Web page content of url in BeautifulSoup format
    '''
    cache_dict = open_cache()
    if url in cache_dict.keys():
        print("Using Cache")
        soup = BeautifulSoup(cache_dict[url], "html.parser")
        return soup
    else:
        print("Fetching")
        response = requests.get(url, headers=headers)
        delays = [17, 14, 26, 27, 20, 19]
        delay = np.random.choice(delays)
        if response.status_code  == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            cache_dict[url] = response.text
            save_cache(cache_dict)
            time.sleep(delay)
            return soup
        else:
            print(f'{response.status_code} Error!')
            time.sleep(4000)
            return None



if __name__ == "__main__":
    
    # Scrape and crawl web pages and save info to cache file cache.json
    parent_dict = company_url_dict(parent_company_url)
    parent_num = min(40, len(parent_dict))
    parent_company_list = list(parent_dict.values())[:parent_num]
    parent_company_dict = {}
    for url in parent_company_list:
        parent_company_dict[url] = company_url_dict(url)
    for parent_company in parent_company_dict.values():
        for company in parent_company.values():
            perfumes_list = perfume_url_list(company)
            for url in perfumes_list:
                get_soup_helper(url)
    



    