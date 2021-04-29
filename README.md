## SI507 Final Project Intro

###1. Preparation

Database web: https://www.themoviedb.org/?language=en-US

Data API: in the 'moviekeys.py' (submitted on Canvas)

Packages need installing before running the APP: `request`, `json`, `sqlite3`, `datetime`, `plotly`



###2. Code Structure

####Part 1: Accessing Data via The Movie Database (TMDb) API 

Cashing, request link building, API request, data stored as json format

####Part 2: Database Building

Building SQL tables by python code, populate SQL tables with cached data 

####Part 3: Data Visualization with `Plotly` 
Embedded in interactive interface, results showing in a browser

####Part 4 Interactive Interface Building

1. Search keywords: three sorts of keywords: movie rating (e.g 8, 7.8); 
   movie release year (e.g 2019); movie keywords (e.g harry potter, case-insensitive) 


2. Visualization: plotting the movie rating vs. movie popularity


3. Search Results sorting: sort by movie release date or by total vote count


4. Choose the searched movie to see detailed info: enter the index of the searched results


###3. Main Movie Database Features

`title`: movie name in English

`release_date `: the date when the movie published, ranging from 1921-2021

`original_title`: movie name in original language

`original_language`: movie language

`vote_average`: the average rating score (0-10), voted by users who use this movie database web

`vote_count`: how many users voted this movie

`popularity`: a synthetic metric measuring to what degree the movie is popular, including number of people 
who marked as 'favorite', number of people who marked as 'watchlist', number of views of the day etc.

`overview`: overview summarizes the story of the movie





