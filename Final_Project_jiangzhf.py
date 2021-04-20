#import os
import json
import requests
import sqlite3
import secrets as secrets

#os.chdir('/Users/jiangzhoufu/Desktop/SI507/HW/Final Project')

baseurl = "https://api.themoviedb.org/3/movie/popular?"
api_key = secrets.API_KEY
CACHE_FILENAME = "tmbd_cache.json"
CACHE_DICT = {}
DataBase = 'popular_moive.sqlite'

#Part 1 Data import via The Movie Database (TMDb) API

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
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


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_") 
    to join your baseurl with the params and all the key-value pairs from params
    E.g., baseurl_key1_value1
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    underscore = '_'
    param_str = []
    for key in params.keys():
        param_str.append(f'{key}_{params[key]}')
    param_str.sort()
    uniq_key = baseurl + underscore.join(param_str)
    return uniq_key


def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    res = requests.get(baseurl, params=params)
    return res.json()


def make_request_with_cache(baseurl, api_key):

    params = {'api_key': api_key, 'page': page}
    uniq_key = construct_unique_key(baseurl, params)
    
    if uniq_key in CACHE_DICT.keys():
        print('fetching cached data')
        res = CACHE_DICT[uniq_key]
    
    else:
        res = make_request(baseurl, params)
        CACHE_DICT[uniq_key] = res
        save_cache(CACHE_DICT)
    
    return res

#Part 2 Cache Data Cleaning
CACHE_DICT = open_cache()
by_page = []
    
for i in range(1, 301):
    page = i
    movie = make_request_with_cache(baseurl, api_key)
    by_page.append(movie)

movie6000 = []

for i in range(0, 300):
    for j in range(0,20):
        movie6000.append(by_page[i]['results'][j])


class Movie:

    def __init__(self, adult=None, backdrop_path='No path', id='No id',
                       original_language='No language', original_title='No title',
                       overview='No overview', popularity='No popularity', 
                       poster_path='No path', title='No title', video=None,
                       vote_average="No score", vote_count='No count', json=None):
        self.json=json
        if self.json == None:
            self.adult = adult
            self.backdrop_path = backdrop_path
            self.id = id
            self.original_language = original_language
            self.original_title = original_title
            self.overview = overview
            self.popularity = popularity
            self.poster_path = poster_path
            self.title = title
            self.video = video
            self.vote_average = vote_average
            self.vote_count = vote_count
        else:
            self.adult = json['adult']
            self.backdrop_path = json['backdrop_path']
            self.id = json['id']
            self.original_language = json['original_language']
            self.original_title = json['original_title']
            self.overview = json['overview']
            self.popularity = json['popularity']
            self.poster_path = json['poster_path']
            self.title = json['title']
            self.video = json['video']
            self.vote_average = json['vote_average']
            self.vote_count = json['vote_count']
    
    def info(self):
        return f"{self.title}"


# #Part 3 Database Building

def build_db():
    conn = sqlite3.connect(DataBase)
    cur = conn.cursor()

    drop_popular_movie_background_sql = 'DROP TABLE IF EXISTS "popular_movie_background" '
    drop_popular_movie_content_sql = 'DROP TABLE IF EXISTS "popular_movie_content"'
    drop_popular_movie_rating_sql = 'DROP TABLE IF EXISTS "popular_movie_rating"'

    build_popular_movie_background_sql = '''
    CREATE TABLE IF NOT EXISTS "popular_movie_background" (
        'id' INTEGER PRIMARY KEY,
        "title" TEXT NOT NULL,
        "original_title" TEXT NOT NULL,
        "adult" TEXT NOT NULL,
        "video" TEXT NOT NULL,
        "original_language" TEXT NOT NULL,
        "poster_path" TEXT,
        "backdrop_path" TEXT
    )
    '''
    build_popular_movie_content_sql = '''
    CREATE TABLE IF NOT EXISTS "popular_movie_content" (
        'id' INTEGER PRIMARY KEY,
        "title" TEXT NOT NULL,
        "overview" TEXT NOT NULL
    )
    '''

    build_popular_movie_rating_sql = '''
    CREATE TABLE IF NOT EXISTS "popular_movie_rating" (
        'id' INTEGER PRIMARY KEY,
        "title" TEXT NOT NULL,
        "popularity" INTEGER,
        "vote_count" INTEGER,
        "vote_average" INTEGER
    )
    '''
    cur.execute(drop_popular_movie_background_sql)
    cur.execute(drop_popular_movie_content_sql)
    cur.execute(drop_popular_movie_rating_sql)
    cur.execute(build_popular_movie_background_sql)
    cur.execute(build_popular_movie_content_sql)
    cur.execute(build_popular_movie_rating_sql)
    conn.commit()
    conn.close()

def populate_movie_background_table():

    insert_title_sql = '''
    INSERT INTO popular_movie_background
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    conn = sqlite3.connect(DataBase)
    cur = conn.cursor()
    
    movie_ls = []
    for movie in movie6000:
        movie_ls.append(Movie(json=movie))
    
    for movie in movie_ls:
        cur.execute(insert_title_sql,
            [
                movie.id,
                movie.title,
                movie.original_title,
                movie.adult,
                movie.title,
                movie.original_language,
                movie.poster_path,
                movie.backdrop_path
            ]
        )
    conn.commit()
    conn.close()

def populate_movie_content_table():

    insert_content_sql = '''
    INSERT INTO popular_movie_content
    VALUES (?, ?, ?)
    '''
    
    conn = sqlite3.connect(DataBase)
    cur = conn.cursor()
    
    movie_ls = []
    for movie in movie6000:
        movie_ls.append(Movie(json=movie))
    
    for movie in movie_ls:
        cur.execute(insert_content_sql,
            [
                movie.id,
                movie.title,
                movie.overview
            ]
        )
    conn.commit()
    conn.close()

def populate_movie_rating_table():

    insert_rating_sql = '''
    INSERT INTO popular_movie_rating
    VALUES (?, ?, ?, ?, ?)
    '''
    
    conn = sqlite3.connect(DataBase)
    cur = conn.cursor()
    
    movie_ls = []
    for movie in movie6000:
        movie_ls.append(Movie(json=movie))
    
    for movie in movie_ls:
        cur.execute(insert_rating_sql,
            [
                movie.id,
                movie.title,
                movie.popularity,
                movie.vote_count,
                movie.vote_average
            ]
        )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_db()
    populate_movie_background_table()
    populate_movie_content_table()
    populate_movie_rating_table()
    print(len(movie6000))