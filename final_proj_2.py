# -*- coding: UTF-8 -*-
#################################
##### Name: Ziyun Wang ##########
##### Uniqname: ziyun ###########
#################################
from bs4 import BeautifulSoup
import json
import time
import sqlite3
import final_proj_1
DB = 'check.sqlite'
CACHE_FILENAME = "cache.json"


def create_tables():
    ''' Create tables in database

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''

    pragma_1 = '''
    PRAGMA foreign_keys=ON;
    '''
    pragma_2 = '''
    PRAGMA encoding = "UTF-8";
    '''
    create_brand = '''
        CREATE TABLE IF NOT EXISTS "Brand"(
            "BrandId"       INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Name"          TEXT NOT NULL UNIQUE
        );
    '''
    create_designer = '''
        CREATE TABLE IF NOT EXISTS "Designer"(
            "DesignerId"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Name"          TEXT NOT NULL UNIQUE
        );
    '''
    create_scent = '''
        CREATE TABLE IF NOT EXISTS "Scent"(
            "ScentId"       INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Name"          TEXT NOT NULL UNIQUE
        );
    '''
    create_perfume = '''
        CREATE TABLE IF NOT EXISTS "Perfume"(
            "PerfumeId"     INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Name"          TEXT NOT NULL,
            "Rating"        REAL,
            "RatingCount"   INTEGER,
            "DesignerId"    INTEGER,
            "BrandId"       INTEGER,
            CONSTRAINT fk_Designer FOREIGN KEY (DesignerId)
            REFERENCES Designer(DesignerId),
            CONSTRAINT fk_Brand FOREIGN KEY (BrandId)
            REFERENCES Brand(BrandId)
        );
    '''
    create_perfume_scent = '''
        CREATE TABLE IF NOT EXISTS "Perfume_Scent"(
            PerfumeId   INTEGER, 
            ScentId     INTEGER, 
            FOREIGN KEY(PerfumeId) REFERENCES Perfume(PerfumeId) ON DELETE CASCADE, 
            FOREIGN KEY(ScentId) REFERENCES Scent(ScentId) ON DELETE CASCADE 
        ); 
    '''
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    cursor.execute(pragma_1)
    cursor.execute(pragma_2)
    cursor.execute(create_brand)
    cursor.execute(create_designer)
    cursor.execute(create_scent)
    cursor.execute(create_perfume)
    cursor.execute(create_perfume_scent)
    connection.commit()
    connection.close()


def perfume_info(cache_response):
    ''' Get records of perfume names, ratings, rating counts, brands and designers 
    from perfume pages, and then insert them into database

    Parameters
    ----------
    cache_response: str

    Returns
    -------
    None
    '''
    # Get records from perfume pages
    scents_list =[]
    soup = BeautifulSoup(cache_response, "html.parser")
    try:
        rating = float(soup.find('span',itemprop="ratingValue").get_text().strip('\n'))
    except:
        rating = 0.0
    try:
        rating_count = int(soup.find('span',itemprop="ratingCount").get_text().strip('\n'))
    except:
        rating_count = 0
    try:
        name = soup.find('h1').get_text().strip('\n')
    except:
        name = 'N/A'
    try:
        designer = soup.find('img', class_="perfumer-avatar").find_next_sibling().get_text().strip('\n')
    except:
        designer = 'N/A'
    try:
        brand = soup.find('span', class_="vote-button-name").get_text().strip('\n')
    except:
        brand = 'N/A'
    try:
        scents = soup.find_all('div', class_="accord-bar")
        for s in scents:
            scents_list.append(s.get_text().strip('\n'))
    except:
        scents_list = ['N/A']
    
    # Insert record to database

    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    
    cursor.execute(f'INSERT OR IGNORE INTO Brand ("Name") VALUES ("{brand}");')
    brand_id = cursor.execute(f'SELECT BrandId FROM Brand WHERE Name = "{brand}"').fetchall()[0][0]
    
    cursor.execute(f'INSERT OR IGNORE INTO Designer ("Name") VALUES ("{designer}");')
    designer_id = cursor.execute(f"SELECT DesignerId FROM Designer WHERE Name = '{designer}'").fetchall()[0][0]
    
    scent_id_list = []
    for scent in scents_list:
        cursor.execute(f'INSERT OR IGNORE INTO Scent ("Name") VALUES ("{scent}");')
        scent_id_list.append(cursor.execute(f'SELECT ScentId FROM Scent WHERE Name = "{scent}"').fetchall()[0][0])
    
    perfume_query = f'INSERT OR IGNORE INTO Perfume ("Name","Rating","RatingCount","DesignerId", "BrandId") \
                    VALUES ("{name}", "{rating}", "{rating_count}","{designer_id}", "{brand_id}");'
    cursor.execute(perfume_query)
    perfume_id = cursor.execute(f'SELECT PerfumeId FROM Perfume WHERE Name = "{name}"').fetchall()[0][0]
    
    for scent_id in scent_id_list:
        cursor.execute(f'INSERT OR IGNORE INTO Perfume_Scent ("PerfumeId", "ScentId") \
            VALUES ("{perfume_id}","{scent_id}");')

    connection.commit()
    connection.close()

if __name__ == "__main__":
    create_tables()
    cache_dict = final_proj_1.open_cache()
    key_list = list(cache_dict.keys())
    
    for key in key_list:
        # search for all perfume pages
        if '/perfume/' in key:
            perfume_info(cache_dict[key])


    connection = sqlite3.connect(DB)
    cursor = connection.cursor()

    print(cursor.execute(f"SELECT * FROM Designer").fetchall())
    print(cursor.execute(f"SELECT * FROM Brand").fetchall())
    print(cursor.execute(f"SELECT * FROM Scent").fetchall())
    print(cursor.execute(f"SELECT * FROM Perfume").fetchall())
    print(cursor.execute(f"SELECT * FROM Perfume_Scent").fetchall())
    connection.close()
    
    
    

    