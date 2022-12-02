from email import message
from os import name
import flask
from flask import jsonify
import pickle
import pandas as pd
import requests

# geting movies list
movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_dict, columns=['movie_id', 'title', 'tags'])
data = {
    "title": pd.Series(movies['title'].values).to_list()
}
similarity = pickle.load(open('similarity.pkl', 'rb'))

#######################

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    dis = similarity[movie_index]
    movie_list = sorted(list(enumerate(dis)), reverse=True, key=lambda x:x[1])[1:11]
    recommended_movies = []
    for i in movie_list:
        recommended_movies.append(movies.iloc[i[0]].movie_id)
    return getRecommend(recommended_movies)

# https://api.themoviedb.org/3/movie/550?api_key=18ba36a47e17d0f327912bc098a1bb60


def getRecommend(recommended_movies):
    load = {"api_key": "18ba36a47e17d0f327912bc098a1bb60"}
    list = []
    for index, item in enumerate(recommended_movies, start=0):    
        current_item = requests.get("https://api.themoviedb.org/3/movie/{}".format(item), params=load).json()
        # Removing item
        current_item.pop("adult", None)
        current_item.pop("backdrop_path", None)
        current_item.pop("belongs_to_collection", None)
        current_item.pop("genres", None)
        current_item.pop("revenue", None)
        current_item.pop("video", None)
        current_item.pop("production_companies", None)
        current_item.pop("production_countries", None)
        current_item.pop("spoken_languages", None)
        current_item["poster_path"] = "https://image.tmdb.org/t/p/w500{}".format(current_item["poster_path"])
        list.append(current_item)
    return list



# This is just init the flask
app = flask.Flask(__name__)

@app.route('/get_titles')
def get_movie_titles():
    try:
        return jsonify(data)
    except KeyError:
        return 'Error at get_movie_titles'


@app.route('/get_recommendation/<string:name>')
def get_recommendation(name):
    try:
        print(recommend(name))
        return jsonify(recommend(name))
    except KeyError:
        return 'Error at get_recommendation'

 
@app.route('/')
def welcome():
    return "Welcome to recommender system api"


@app.errorhandler(404)
def not_found(e):
  return jsonify({"code": 404, "message": "There is no such URL in recommender system api"})

# this gonna start app,
# debug=True only use in development enviroment 
if __name__ == "__main__":
    app.run()