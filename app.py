from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import random
from yelpUserProfile import YelpUserProfile
import os

app = Flask(__name__)

CREDENTIALS = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

app.secret_key = 'welcome'
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

app.config['TRAP_BAD_REQUEST_ERRORS'] = True  # gets better error messages for certain common request errors

@app.route('/')
def welcome():
    """
    Renders the welcome page.
    """
    return render_template('welcome.html')

@app.route('/search.html', methods=['GET', 'POST'])
def search():
    """
    Renders the search page and obtains userID
    """
    return render_template('search.html')

@app.route('/query', methods=['GET', 'POST'])
def query():
    user_id = request.args.get('query')

    obj = YelpUserProfile(user_id)
    obj.scrape_all_info()   
    
    name = obj.get_name()
    hometown = obj.get_hometown()
    total_reviews = obj.get_total_reviews()
    total_friends = obj.get_total_friends()
    profile_pic = '"' + obj.get_profile_pic() + '"'

    most_visited_places = obj.get_most_visited_places()
    most_visited_cities = obj.get_most_visited_cities()
    average_rating = obj.get_avg_rating()
    recent_reviews = obj.get_recent_reviews()
    enthusiasm_score = obj.get_enthusiasm_score()
    most_enthusiastic_places = obj.get_most_enthusiastic_places()

    friend_visited_places = obj.get_most_visited_places(False)
    friend_visited_cities = obj.get_most_visited_cities(False)
    friend_average_rating = obj.get_avg_rating(False)
    friend_enthusiasm_score = obj.get_enthusiasm_score(False)
    friend_enthusiastic_places = obj.get_most_enthusiastic_places(False)

    data = {'name': name, 'hometown': hometown, 'totalReviews': total_reviews, 'totalFriends': total_friends, 
        'profilePic': profile_pic, 'mostVisitedPlaces': most_visited_places, 'mostVisitedCities': most_visited_cities, 
        'averageRating': average_rating, 'recentReviews': recent_reviews, 'enthusiasmScore': enthusiasm_score, 
        'mostEnthusiasticPlaces': most_enthusiastic_places, 'friendVisitedPlaces': friend_visited_places, 
        'friendVisitedCities': friend_visited_cities, 'friendAverageRating': friend_average_rating,
        'friendEnthusiasmScore': friend_enthusiasm_score, 'friendEnthusiasticPlaces': friend_enthusiastic_places
    }
    session['data'] = data
    
    return jsonify(data)

@app.route('/profile.html')
def profile():
    """
    Renders the profile page.
    """
    data = session.pop('data')
    print(data)
    
    return render_template('profile.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)