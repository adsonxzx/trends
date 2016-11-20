"""Visualizing Twitter Sentiment Across America"""

from data import word_sentiments, load_tweets
from datetime import datetime
from doctest import run_docstring_examples
from geo import us_states, geo_distance, make_position, longitude, latitude
from maps import draw_state, draw_name, draw_dot, wait, message
from string import ascii_letters
from ucb import main, trace, interact, log_current_line



# Phase 1: The Feelings in Tweets

def make_tweet(text, time, lat, lon):
    """Return a tweet, represented as a python dictionary.

    text      -- A string; the text of the tweet, all in lowercase
    time      -- A datetime object; the time that the tweet was posted
    latitude  -- A number; the latitude of the tweet's location
    longitude -- A number; the longitude of the tweet's location

    >>> t = make_tweet("just ate lunch", datetime(2012, 9, 24, 13), 38, 74)
    >>> tweet_words(t)
    ['just', 'ate', 'lunch']
    >>> tweet_time(t)
    datetime.datetime(2012, 9, 24, 13, 0)
    >>> p = tweet_location(t)
    >>> latitude(p)
    38
    """
    return {'text': text, 'time': time, 'latitude': lat, 'longitude': lon}
    #cria um dicionario a partir da string de um tweet

def tweet_words(tweet):
    """Return a list of the words in the text of a tweet."""
    
    return extract_words(tweet["text"])    
    #retornar do dicionario de make_tweet o texto filtrado por extract_words
   
def tweet_time(tweet):
    """Return the datetime that represents when the tweet was posted."""
    
    return tweet["time"]
    #retornar do dicionario de make_tweet o tempo

def tweet_location(tweet):
    """Return a position (see geo.py) that represents the tweet's location."""
    
    return tweet["latitude"], tweet["longitude"]    
    #retornar do dicionario de make_tweet a latitude e a longitude

def tweet_string(tweet):
    """Return a string representing the tweet."""
    return '"{0}" @ {1}'.format(tweet['text'], tweet_location(tweet))
    #tranformar o tweet em uma string

def extract_words(text):
    """Return the words in a tweet, not including punctuation.

    >>> extract_words('anything else.....not my job')
    ['anything', 'else', 'not', 'my', 'job']
    >>> extract_words('i love my job. #winning')
    ['i', 'love', 'my', 'job', 'winning']
    >>> extract_words('make justin # 1 by tweeting #vma #justinbieber :)')
    ['make', 'justin', 'by', 'tweeting', 'vma', 'justinbieber']
    >>> extract_words("paperclips! they're so awesome, cool, & useful!")
    ['paperclips', 'they', 're', 'so', 'awesome', 'cool', 'useful']
    """
    
    temp_string = ""
    words_list = []
    for caractere in text:
        if caractere in ascii_letters:
            temp_string = temp_string + caractere
        else:
            if temp_string != "":
                words_list.append(temp_string)
            temp_string = ""
    if temp_string != "":
        words_list.append(temp_string)
    return words_list    
    #metodo split criado para extrair somente caracteres validos e transformar em palavras numa lista

def make_sentiment(value):
    """Return a sentiment, which represents a value that may not exist.

    >>> s = make_sentiment(0.2)
    >>> t = make_sentiment(None)
    >>> has_sentiment(s)
    True
    >>> has_sentiment(t)
    False
    >>> sentiment_value(s)
    0.2
    """
    assert value is None or (value >= -1 and value <= 1), 'Illegal value'
    
    return value    
    #cria um sentimento e atribui um valor

def has_sentiment(s):
    """Return whether sentiment s has a value."""
    
    if s != None:
        return True
    else:
        return False
    
    #checa se existe sentimento na palavra ou nao
    
def sentiment_value(s):
    """Return the value of a sentiment s."""
    assert has_sentiment(s), 'No sentiment value'
    
    return s    
    #checa no arquivo de data o valor do sentimento, se existir

def get_word_sentiment(word):
    """Return a sentiment representing the degree of positive or negative
    feeling in the given word, if word is not in the sentiment dictionary.

    >>> sentiment_value(get_word_sentiment('good'))
    0.875
    >>> sentiment_value(get_word_sentiment('bad'))
    -0.625
    >>> sentiment_value(get_word_sentiment('winning'))
    0.5
    >>> has_sentiment(get_word_sentiment('Berkeley'))
    False
    """
    return make_sentiment(word_sentiments.get(word, None))
    #checa no arquivo de data o valor do sentimento, se n existir retorna False

def analyze_tweet_sentiment(tweet):
    """ Return a sentiment representing the degree of positive or negative
    sentiment in the given tweet, averaging over all the words in the tweet
    that have a sentiment value.
    If no words in the tweet have a sentiment value, return
    make_sentiment(None).
    >>> positive = make_tweet('i love my job. #winning', None, 0, 0)
    >>> round(sentiment_value(analyze_tweet_sentiment(positive)), 5)
    0.29167
    >>> negative = make_tweet("Thinking, 'I hate my job'", None, 0, 0)
    >>> sentiment_value(analyze_tweet_sentiment(negative))
    -0.25
    >>> no_sentiment = make_tweet("Go bears!", None, 0, 0)
    >>> has_sentiment(analyze_tweet_sentiment(no_sentiment))
    False
    """   
    average_of_sentiments = 0
    sentiments_count = 0
    for word in tweet_words(tweet):
        value = get_word_sentiment(word)
        if has_sentiment(value) != False:
            average_of_sentiments += value
            sentiments_count += 1
    if sentiments_count == 0:
        return make_sentiment(None)  
    return (average_of_sentiments / sentiments_count)
    #analisa todo as palavras de um tweet e tira uma media dos sentimentos

# Phase 2: The Geometry of Maps

def find_centroid(polygon):
    """Find the centroid of a polygon.

    http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon

    polygon -- A list of positions, in which the first and last are the same

    Returns: 3 numbers; centroid latitude, centroid longitude, and polygon area

    Hint: If a polygon has 0 area, return its first position as its centroid

    >>> p1, p2, p3 = make_position(1, 2), make_position(3, 4), make_position(5, 0)
    >>> triangle = [p1, p2, p3, p1]  # First vertex is also the last vertex
    >>> find_centroid(triangle)
    (3.0, 2.0, 6.0)
    >>> find_centroid([p1, p3, p2, p1])
    (3.0, 2.0, 6.0)
    >>> find_centroid([p1, p2, p1])
    (1, 2, 0)
    """
    
    cx = 0; cy = 0; area = 0
    
    for i in range(0,(len(polygon)-1),1): #somatorio area
        xi = (polygon[i])[0]; yi = (polygon[i])[1]
        x2 = (polygon[i+1])[0]; y2 = (polygon[i+1])[1]
        area = area + ((xi*y2) - (x2*yi))
    area = area * (1/2)
    
    if area == 0: area = 0; cx = (polygon[0])[0]; cy = (polygon[0])[1]
    else:
        for i in range(0,(len(polygon)-1),1):
            xi = (polygon[i])[0]; yi = (polygon[i])[1]
            x2 = (polygon[i+1])[0]; y2 = (polygon[i+1])[1]
            cx = cx + ((xi + x2) * ((xi * y2) - (x2*yi)))
        cx = cx * 1/(6*area)
        
        for i in range(0,(len(polygon)-1),1):
            xi = (polygon[i])[0]; yi = (polygon[i])[1]
            x2 = (polygon[i+1])[0]; y2 = (polygon[i+1])[1]
            cy = cy + ((yi + y2) * ((xi * y2) - (x2*yi)))
        cy = cy * 1/(6*area)
        area = abs(area)
        
    return cx, cy, area
    

def find_center(polygons):
    """Compute the geographic center of a state, averaged over its polygons.

    The center is the average position of centroids of the polygons in polygons,
    weighted by the area of those polygons.

    Arguments:
    polygons -- a list of polygons

    >>> ca = find_center(us_states['CA'])  # California
    >>> round(latitude(ca), 5)
    37.25389
    >>> round(longitude(ca), 5)
    -119.61439

    >>> hi = find_center(us_states['HI'])  # Hawaii
    >>> round(latitude(hi), 5)
    20.1489
    >>> round(longitude(hi), 5)
    -156.21763
    """
    
    cx = 0; cy = 0; areai = 0
    for polygon in polygons:#somatorios do centroid e da area de todos os poligonos
        cx = cx + (find_centroid(polygon)[0]) * (find_centroid(polygon)[2])
        cy = cy + (find_centroid(polygon)[1]) * (find_centroid(polygon)[2])
        areai = areai + (find_centroid(polygon)[2])
    cx = cx/areai; cy = cy/areai
    return cx, cy
    

# Phase 3: The Mood of the Nation

def find_closest_state(tweet, state_centers):
    """Return the name of the state closest to the given tweet's location.

    Use the geo_distance function (already provided) to calculate distance
    in miles between two latitude-longitude positions.

    Arguments:
    tweet -- a tweet abstract data type
    state_centers -- a dictionary from state names to positions.

    >>> us_centers = {n: find_center(s) for n, s in us_states.items()}
    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> find_closest_state(sf, us_centers)
    'CA'
    >>> find_closest_state(ny, us_centers)
    'NJ'
    """
      
    distancias = []
    for x in state_centers:        
        dist = geo_distance(make_position(tweet["latitude"],tweet["longitude"]), make_position(state_centers[x][0],state_centers[x][1]))
        distancias.append(dist)
    for x in state_centers:
        if geo_distance(make_position(tweet["latitude"],tweet["longitude"]), make_position(state_centers[x][0],state_centers[x][1])) == min(distancias):
            estado = x
    
    return estado    
    # Calcula a distancia do tweet dado e retorna a sigla do estado mais proximo.
    
def group_tweets_by_state(tweets):
    """Return a dictionary that aggregates tweets by their nearest state center.

    The keys of the returned dictionary are state names, and the values are
    lists of tweets that appear closer to that state center than any other.

    tweets -- a sequence of tweet abstract data types

    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> ca_tweets = group_tweets_by_state([sf, ny])['CA']
    >>> tweet_string(ca_tweets[0])
    '"Welcome to San Francisco" @ (38, -122)'
    """
       
    tweets_by_state = {}
    us_centers = {n: find_center(s) for n, s in us_states.items()}
    for x in tweets:
        estado = find_closest_state(x, us_centers)        
        tweets_by_state[estado] = []    
    for x in tweets_by_state.keys():
        for y in tweets:
            estado = find_closest_state(y, us_centers)   
            if estado == x:
                tweets_by_state[estado].append(y)
    
                       
    return tweets_by_state    
    #retorna um dicionario com a sigla do estado como chave e os tweets mais proximo desse estado como valor.

def most_talkative_state(term):
    """Return the state that has the largest number of tweets containing term.

    >>> most_talkative_state('texas')
    'TX'
    >>> most_talkative_state('sandwich')
    'NJ'
    """
    tweets = load_tweets(make_tweet, term)  # A list of tweets containing term
    estados = {}
    us_centers = {n: find_center(s) for n, s in us_states.items()}
    for tw in tweets:
        estado = find_closest_state(tw, us_centers)        
        if estado not in estados:
            estados[estado] = 0
        palavras = extract_words(tw['text'])
        for p in palavras:
            if term == p:
                estados[estado] += 1  
          
    #maior
    maior = ""
    for x in estados:  #pega um elemento      
        maior = x
        break
    for tw in estados: #pega o maior valor 
        if estados[tw] > estados[maior]:
            maior = tw
    
    
    return maior
    #retorna o estado com o maior numero de termos 
def average_sentiments(tweets_by_state): 
    """Calculate the average sentiment of the states by averaging over all
    the tweets from each state. Return the result as a dictionary from state
    names to average sentiment values (numbers).

    If a state has no tweets with sentiment values, leave it out of the
    dictionary entirely.  Do NOT include states with no tweets, or with tweets
    that have no sentiment, as 0.  0 represents neutral sentiment, not unknown
    sentiment.

    tweets_by_state -- A dictionary from state names to lists of tweets
    """
    averaged_state_sentiments = {}
    
       
    for tw in tweets_by_state:        
        sentimentos = 0
        count = 0
        for valor in tweets_by_state[tw]:           
           sent = analyze_tweet_sentiment(valor)
           if sent != None:
               sentimentos += sent
               count += 1
        if count != 0:    
            averaged_state_sentiments[tw] = (sentimentos / count)    
    return averaged_state_sentiments

    # retorna a media de sentimentos de vários tweets em relação a um estado
    
# Phase 4: Into the Fourth Dimension

def group_tweets_by_hour(tweets):
    """Return a dictionary that groups tweets by the hour they were posted.

    The keys of the returned dictionary are the integers 0 through 23.

    The values are lists of tweets, where tweets_by_hour[i] is the list of all
    tweets that were posted between hour i and hour i + 1. Hour 0 refers to
    midnight, while hour 23 refers to 11:00PM.

    To get started, read the Python Library documentation for datetime objects:
    http://docs.python.org/py3k/library/datetime.html#datetime.datetime

    tweets -- A list of tweets to be grouped
    """
    
    tweets_by_hour = {}    
    for x in range(0,24):#cria chaves com todas horas
        tweets_by_hour[x] = []    
    
    for x in tweets:#define a hora do tweet
        data = tweet_time(x)        
        if data == None:
            pass
        else:
            hora = data.hour
            for y in tweets_by_hour:#verifica com chave é igual a hora e adiciona o tweet
                if y == hora:
                    tweets_by_hour[y].append(x)
    
    return tweets_by_hour    
    # cria um dicionario com todas as horas do dia, e atribui como valor uma lista de tweets naquela hora. 

# Interaction.  You don't need to read this section of the program.

def print_sentiment(text='Are you virtuous or verminous?'):
    """Print the words in text, annotated by their sentiment scores."""
    words = extract_words(text.lower())
    assert words, 'No words extracted from "' + text + '"'
    layout = '{0:>' + str(len(max(words, key=len))) + '}: {1:+}'
    for word in extract_words(text.lower()):
        s = get_word_sentiment(word)
        if has_sentiment(s):
            print(layout.format(word, sentiment_value(s)))

def draw_centered_map(center_state='TX', n=10):
    """Draw the n states closest to center_state."""
    us_centers = {n: find_center(s) for n, s in us_states.items()}
    center = us_centers[center_state.upper()]
    dist_from_center = lambda name: geo_distance(center, us_centers[name])
    for name in sorted(us_states.keys(), key=dist_from_center)[:int(n)]:
        draw_state(us_states[name])
        draw_name(name, us_centers[name])
    draw_dot(center, 1, 10)  # Mark the center state with a red dot
    wait()

def draw_state_sentiments(state_sentiments={}):
    """Draw all U.S. states in colors corresponding to their sentiment value.

    Unknown state names are ignored; states without values are colored grey.

    state_sentiments -- A dictionary from state strings to sentiment values
    """
    for name, shapes in us_states.items():
        sentiment = state_sentiments.get(name, None)
        draw_state(shapes, sentiment)
    for name, shapes in us_states.items():
        center = find_center(shapes)
        if center is not None:
            draw_name(name, center)

def draw_map_for_term(term='my job'):
    """Draw the sentiment map corresponding to the tweets that contain term.

    Some term suggestions:
    New York, Texas, sandwich, my life, justinbieber
    """
    tweets = load_tweets(make_tweet, term)
    tweets_by_state = group_tweets_by_state(tweets)
    state_sentiments = average_sentiments(tweets_by_state)
    draw_state_sentiments(state_sentiments)
    for tweet in tweets:
        s = analyze_tweet_sentiment(tweet)
        if has_sentiment(s):
            draw_dot(tweet_location(tweet), sentiment_value(s))
    wait()

def draw_map_by_hour(term='my job', pause=0.5):
    """Draw the sentiment map for tweets that match term, for each hour."""
    tweets = load_tweets(make_tweet, term)
    tweets_by_hour = group_tweets_by_hour(tweets)

    for hour in range(24):
        current_tweets = tweets_by_hour.get(hour, [])
        tweets_by_state = group_tweets_by_state(current_tweets)
        state_sentiments = average_sentiments(tweets_by_state)
        draw_state_sentiments(state_sentiments)
        message("{0:02}:00-{0:02}:59".format(hour))
        wait(pause)

def run_doctests(names):
    """Run verbose doctests for all functions in space-separated names."""
    g = globals()
    errors = []
    for name in names.split():
        if name not in g:
            print("No function named " + name)
        else:
            if run_docstring_examples(g[name], g, True) is not None:
                errors.append(name)
    if len(errors) == 0:
        print("Test passed.")
    else:
        print("Error(s) found in: " + ', '.join(errors))

@main
def run(*args):
    """Read command-line arguments and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Run Trends")
    parser.add_argument('--print_sentiment', '-p', action='store_true')
    parser.add_argument('--run_doctests', '-t', action='store_true')
    parser.add_argument('--draw_centered_map', '-d', action='store_true')
    parser.add_argument('--draw_map_for_term', '-m', action='store_true')
    parser.add_argument('--draw_map_by_hour', '-b', action='store_true')
    parser.add_argument('text', metavar='T', type=str, nargs='*',
                        help='Text to process')
    args = parser.parse_args()
    for name, execute in args.__dict__.items():
        if name != 'text' and execute:
            globals()[name](' '.join(args.text))

