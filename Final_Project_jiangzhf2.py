import os
import json
import requests
import sqlite3
import moviekeys as secrets
from datetime import datetime
import plotly.graph_objects as go

os.chdir('/Users/jiangzhoufu/Desktop/SI507/HW/FinalProject')

baseurl = "https://api.themoviedb.org/3/movie/popular?"
api_key = secrets.API_KEY
CACHE_FILENAME = "tmbd_cache.json"
CACHE_DICT = {}
DataBase = 'popular_moive.sqlite'


# Part 1 Accessing Data via The Movie Database (TMDb) API

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
    fw = open(CACHE_FILENAME, "w")
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


def make_request_with_cache(baseurl, api_key, page):
    params = {'api_key': api_key, 'page': page}
    uniq_key = construct_unique_key(baseurl, params)

    if uniq_key in CACHE_DICT.keys():
        print('Using Cache')
        res = CACHE_DICT[uniq_key]

    else:
        print('Fetching Caching Data')
        res = make_request(baseurl, params)
        CACHE_DICT[uniq_key] = res
        save_cache(CACHE_DICT)

    return res


class Movie:

    def __init__(self, adult=None, backdrop_path='No path', id='No id',
                 original_language='No language', original_title='No title',
                 overview='No overview', popularity='No popularity',
                 poster_path='No path', title='No title', video=None,
                 vote_average="No score", vote_count='No count', json=None):
        self.json = json
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
            # self.release_date = release_date

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
            try:
                self.release_date = json['release_date']
            except KeyError:
                self.release_date = 'Release date unknown'

    def info(self):
        return f"{self.title}"


# #Part 2 Database Building

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
        "release_date" TEXT NOT NULL,
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
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        movie.release_date,
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


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# Part 3 Data Visualization


if __name__ == "__main__":

    # #caching data by 300 pages and data cleaning
    CACHE_DICT = open_cache()
    by_page = []
    movie6000 = []
    movie_ls = []

    for i in range(1, 301):
        page = i
        movie = make_request_with_cache(baseurl, api_key, page)
        by_page.append(movie)

    for i in range(0, 300):
        for j in range(0, 20):
            movie6000.append(by_page[i]['results'][j])

    for movie in movie6000:
        movie_ls.append(Movie(json=movie))

    ##average populairty in the database
    # avg_popularity = []
    # for i in movie_ls:
    #     if i.popularity > 0:
    #         avg_popularity.append(i.popularity)
    # avg = sum(avg_popularity)/len(avg_popularity)
    # print(avg)

    # populate SQL tables
    build_db()
    populate_movie_background_table()
    populate_movie_content_table()
    populate_movie_rating_table()

    # Part 4 Interactive Interface buidling
    flag = True
    while flag:
        state = input(
            "1. [Search Movies] Enter a movie name, movie rating (e.g 7 or 8.5), or year (e.g 2019) to find out movies you desire (Enter 'exit' to quit): ")

        if state == 'exit':
            print('you exit.')
            flag = False

        elif (state != 'exit') & (is_number(state) == False):
            print("-------------------------------\n")
            print(f'Search Results in Movie Database: \n')
            res = []
            titles = []
            avg_score = []
            popularity = []
            count = 1
            for movie in movie_ls:
                if state.lower() in movie.title.lower():
                    res.append(movie)
                    titles.append(movie.title)
                    popularity.append(movie.popularity)
                    avg_score.append(movie.vote_average)
                    print(
                        f"{[res.index(movie) + 1]} {movie.title} (released on {movie.release_date}) rating is {movie.vote_average}, voted by {movie.vote_count} people.")
            print("-------------------------------\n")

            vis = input(
                "2. [Visualization] Would you want to see relationship between the movie average score (>4) and its popularity? Enter 'yes' to show graph or enter anything to move on: ")
            if (vis == 'yes') or (vis == 'Yes'):
                avg_score = list(filter(lambda x: x >= 4, avg_score))
                bar_data = go.Scatter(x=avg_score, y=popularity, text=titles, mode='markers')
                basic_layout = go.Layout(title=f"Average Movie Ratings by Key Words ({state}) vs. Their Movie Popularity (Red line is average popularity in TMDb)")
                fig = go.Figure(data=bar_data, layout=basic_layout)
                fig.add_shape(type='line', x0=4, y0=38.97, x1=10, y1=38.97, line=dict(color='Red', dash="dot"), xref='x', yref='y')
                fig.update_layout(yaxis_title="Movie Popularity")
                fig.show()

            sort = input(
                "3. [Sort Movies] Enter 'date' to sort searched results by release date; Enter 'count' to sort searched results by total vote counts; Enter anything to move on: ")
            print("-------------------------------\n")
            if sort == 'count':
                res = sorted(res, key=lambda x: x.vote_count, reverse=True)
                print('The results are sorted by total vote counts descendingly: \n')
            elif sort == 'date':
                print('The results are sorted by released date chronologically: \n')
                res = sorted(res, key=lambda x: x.release_date, reverse=True)
            else:
                res = res

            for i in range(len(res)):
                print(
                    f'[{count}] {res[i].title} (released on {res[i].release_date}) rating is {res[i].vote_average}, voted by {res[i].vote_count} people.')
                count += 1
            print("-------------------------------\n")

            while flag:
                index = input("3. [Movie Info] Choose the index of movies to see movie overview or 'exit' or 'back': ")
                if index == 'back':
                    break
                elif index == 'exit':
                    print('you exit.')
                    flag = False
                elif index.isnumeric():
                    if 0 < int(index) <= len(res):
                        print("-------------------------------\n")
                        print('Original Title:')
                        print(f"{res[int(index) - 1].original_title} \n")
                        print('Original Language:')
                        print(f"{res[int(index) - 1].original_language.upper()} \n")
                        print('Popularity in The Movie Database (TMDb):')
                        print(
                            f"{res[int(index) - 1].popularity} (The average popularity in the movie database is 38.97) \n")
                        print('Overview:')
                        print(f'[{res[int(index) - 1].title}]: {res[int(index) - 1].overview} \n')
                        print("-------------------------------\n")
                        break
                    else:
                        print("[Error] Invalid input")
                        print("-------------------------------\n")

        elif is_number(state):
            if float(state) <= 10:
                print("-------------------------------\n")
                print(f'Search Results in Movie Database: ')
                res = []
                titles = []
                popularity = []
                count = 1
                for movie in movie_ls:
                    if float(state) == float(movie.vote_average):
                        res.append(movie)
                        titles.append(movie.title)
                        popularity.append(movie.popularity)
                        print(
                            f"{[res.index(movie) + 1]} {movie.title} (released on {movie.release_date}) rating is {movie.vote_average}, voted by {movie.vote_count} people.")
                print("-------------------------------\n")

                vis = input(
                    "2. [Visualization] Would you want to see relationship between the movie average score and its popularity? Enter 'yes' to show graph or enter anything to move on: ")
                if (vis == 'yes') or (vis == 'Yes'):
                    bar_data = go.Scatter(x=titles, y=popularity, mode='markers')
                    basic_layout = go.Layout(
                        title=f"Average Movie Ratings at ({state}) vs. Their Movie Popularity (Red line is average popularity in TMDb)")
                    fig = go.Figure(data=bar_data, layout=basic_layout)
                    fig.add_shape(type='line', x0=0, y0=38.97, x1=100, y1=38.97, line=dict(color='Red', dash="dot"),
                                  xref='x', yref='y')
                    fig.update_layout(yaxis_title="Movie Popularity")
                    fig.show()

                sort = input(
                    "3. [Sort Movies] Enter 'date' to sort searched results by release date; Enter 'count' to sort searched results by total vote counts; Enter anything to move on: ")
                print("-------------------------------\n")
                if sort == 'count':
                    res = sorted(res, key=lambda x: x.vote_count, reverse=True)
                    print('The results are sorted by total vote counts descendingly: \n')
                elif sort == 'date':
                    res = sorted(res, key=lambda x: x.release_date, reverse=True)
                    print('The results are sorted by released date chronologically: \n')
                else:
                    res = res

                for i in range(len(res)):
                    print(
                        f'[{count}] {res[i].title} (released on {res[i].release_date}) rating is {res[i].vote_average}, voted by {res[i].vote_count} people.')
                    count += 1
                print("-------------------------------\n")

                while flag:
                    index = input(
                        "4. [Movie Info] Choose the index of movies to see movie overview or 'exit' or 'back': ")
                    if index == 'back':
                        break
                    elif index == 'exit':
                        print('you exit.')
                        flag = False
                    elif index.isnumeric():
                        if 0 < int(index) <= len(res):
                            print("-------------------------------\n")
                            print('Original Title:')
                            print(f"{res[int(index) - 1].original_title} \n")
                            print('Original Language:')
                            print(f"{res[int(index) - 1].original_language.upper()} \n")
                            print('Popularity in The Movie Database (TMDb):')
                            print(
                                f"{res[int(index) - 1].popularity} (The average popularity in the movie database is 38.97)\n")
                            print('Overview:')
                            print(f'[{res[int(index) - 1].title}]: {res[int(index) - 1].overview} \n')
                            print("-------------------------------\n")
                            break
                        else:
                            print("[Error] Invalid input")
                            print("-------------------------------\n")

            elif 1900 < float(state) <= 2021:
                print("-------------------------------\n")
                print(f'Search Results in Movie Database: ')
                res = []
                titles = []
                popularity = []
                avg_score = []
                count = 1
                for movie in movie_ls:
                    if state in movie.release_date:
                        res.append(movie)
                        titles.append(movie.title)
                        popularity.append(movie.popularity)
                        avg_score.append(movie.vote_average)
                        print(f"{[res.index(movie) + 1]} {movie.title} (released on {movie.release_date}) rating is {movie.vote_average}, voted by {movie.vote_count} people.")
                print("-------------------------------\n")

                vis = input("2. [Visualization] Would you want to see relationship between the movie average score (>=4) and its popularity? Enter 'yes' to show graph or enter anything to move on: ")
                if (vis == 'yes') or (vis == 'Yes'):
                    avg_score = list(filter(lambda x: x >= 4, avg_score))
                    bar_data = go.Scatter(x=avg_score, y=popularity, text=titles, mode='markers')
                    basic_layout = go.Layout(
                        title=f"Average Movie Ratings in {state} vs. Their Movie Popularity (Red line is average popularity in TMDb)")
                    fig = go.Figure(data=bar_data, layout=basic_layout)
                    fig.add_shape(type='line', x0=4, y0=38.97, x1=10, y1=38.97, line=dict(color='Red', dash="dot"),
                                  xref='x', yref='y')
                    fig.update_layout(xaxis_title = "Average Ratings", yaxis_title="Movie Popularity")
                    fig.show()

                sort = input("3. Enter 'date' to sort searched results by release date; Enter 'count' to sort searched results by total vote counts; Enter anything to move on: ")
                print("-------------------------------\n")

                if sort == 'count':
                    count = 1
                    res = sorted(res, key=lambda x: x.vote_count, reverse=True)
                    print('The results are sorted by total vote counts descendingly: \n')
                    for i in range(len(res)):
                        print(f'[{count}] {res[i].title} (released on {res[i].release_date}) rating is {res[i].vote_average}, voted by {res[i].vote_count} people.')
                        count += 1

                if sort == 'date':
                    res = sorted(res, key=lambda x: x.vote_count, reverse=True)
                    res1 = list(filter(lambda x: (datetime.strptime(x.release_date, '%Y-%m-%d') <= datetime.now()), res))
                    res2 = list(filter(lambda x: (datetime.strptime(x.release_date, '%Y-%m-%d') > datetime.now()), res))
                    res1 = sorted(res1, key=lambda x: x.release_date, reverse=True)
                    res2 = sorted(res2, key=lambda x: x.release_date, reverse=True)

                    print('The results are sorted by released date chronologically: \n')
                    for i in range(len(res1)):
                        print(f'[{count}] {res1[i].title} (released on {res1[i].release_date}) rating is {res1[i].vote_average}, voted by {res1[i].vote_count} people.')
                        count += 1
                    if len(res2) >= 0:
                        print('Incoming movies this year: \n')
                        for i in range(len(res2)):
                            print(f'[{count}] {res2[i].title} (released on {res2[i].release_date}) rating is {res2[i].vote_average}, voted by {res1[i].vote_count} people.')
                            count += 1
                    else:
                        print('')
                print("-------------------------------\n")

                # Enter number to explore movie intro
                while flag:
                    index = input("Choose the index of movies to see movie overview or 'exit' or 'back': ")
                    if index == 'back':
                        break
                    elif index == 'exit':
                        print('you exit.')
                        flag = False
                    elif index.isnumeric():
                        if 0 < int(index) <= len(res):
                            print("-------------------------------\n")
                            print('Original Title:')
                            print(f"{res[int(index) - 1].original_title} \n")
                            print('Original Language:')
                            print(f"{res[int(index) - 1].original_language.upper()} \n")
                            print('Popularity in The Movie Database (TMDb):')
                            print(
                                f"{res[int(index) - 1].popularity} (The average popularity in the movie database is 38.97)\n")
                            print('Overview:')
                            print(f'[{res[int(index) - 1].title}]: {res[int(index) - 1].overview} \n')
                            print("-------------------------------\n")
                            break
                        else:
                            print("[Error] Invalid input")
                            print("-------------------------------\n")
            elif (float(state) < 1921) & (float(state) >= 2022):
                print('Please enter year between 1921~2021.')
        else:
            print("[Error] Invalid input")
