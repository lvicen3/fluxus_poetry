import requests
import re
import random

from bs4 import BeautifulSoup
from flask import Flask, render_template

app = Flask(__name__)

# Function to split a document into a list of tokens
# Arguments:
# doc: A string containing input document
# Returns: tokens (list)
# Where, tokens (list) is a list of tokens that the document is split into
def get_tokens(doc):
	tokens = re.split(r"[^A-Za-z0-9-']", doc)
	tokens = list(filter(len, tokens))
	return tokens


# Function to split a document into a list of tokens
# Arguments: None
# Returns: stopwords (set)
# Where, stopwords (set) is a list of stopwords to be filtered from the document
def get_stopwords():
    stopwords = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
                    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
                    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
                    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
                    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was',
                    'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
                    'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
                    'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
                    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
                    'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
                    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
                    "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren',
                    "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn',
                    "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
                    'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't",
                    'won', "won't", 'wouldn', "wouldn't"])
    return stopwords

stopwords = get_stopwords()	
bands = ['Vampire_Weekend', 'Radiohead', 'Interpol','MGMT','The_Strokes']
display_bands = ['Vampire Weekend', 'Radiohead', 'Interpol','MGMT','The Strokes']
N_LINES = 3

def get_random_line(band_name='Vampire_Weekend'):
  # # pull discography table from band's wiki
  try:
    url = 'https://en.wikipedia.org/wiki/{0}_discography'.format(band_name)
    page = requests.get('https://en.wikipedia.org/wiki/{0}_discography'.format(band_name))
    discography_soup = BeautifulSoup(page.content,'html.parser')
  except:
    print('Error opening artist link')
    raise
  
  album_list = discography_soup.find(attrs={'id':'Studio_albums'}).findNext('table', attrs={'class': 'wikitable plainrowheaders'}).find_all('th',attrs={'scope':'row'})

  album_urls = []
  for album in album_list:
      album_urls.append('https://en.wikipedia.org/'+album.find('a')['href'])
  album_url = random.choice(album_urls)

  # pull album page -> get a song
  album_page = requests.get(album_url)
  album_soup = BeautifulSoup(album_page.content,'html.parser')
  songs = album_soup.find('table',attrs={'class':'tracklist'}).find_all(attrs={'style':'vertical-align:top'})
  song = random.choice(songs).get_text()
  song = re.sub(r'\([^)]*\)','',song)
  song = song.lower()
  # song = song.replace('"','').lower().replace(' ','-')
  song = get_tokens(song)
  parsed_song = ''
  for word in song[:-1]:
      parsed_song+=word + '-'
  parsed_song+=song[-1]  

  # build url for genius website
  # parsed_song = ((re.search('"(\w[\s\w]*)"', song).group(1)).lower()).replace(' ','-')
  parsed_band = band_name.lower().capitalize().replace('_','-')
  genius_url = 'https://genius.com/' + parsed_band + '-' + parsed_song + '-lyrics'

  # page = requests.get('https://genius.com/Vampire-weekend-hannah-hunt-lyrics')
  page = requests.get(genius_url)
  soup = BeautifulSoup(page.content,'html.parser')
  lyrics = soup.find('p')

  lyrics_str = lyrics.get_text()
  lyrics_str = re.sub(r'\[[^]]*\][\n\r]','',lyrics_str)
  lines = re.split(r'[\n\r]+', lyrics_str)  
  lines = [line for line in lines if re.match(r'^[A-Za-z]+', line)]
  
  return random.choice(lines)

def get_art(words):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = 'https://unsplash.com/s/photos/{0}-{1}-{2}'.format(words[0],words[1],words[2])
    page = requests.get(url, headers = headers)
    soup = BeautifulSoup(page.content,'html.parser')
    figures = soup.findAll('figure')
    img_links = []
    for figure in figures:
        try:
            img_links.append(figure.find('img').get('src'))
        except:
            ()        
    
    img_links = [img_link for img_link in img_links if re.match(r'(.+)photo(.+)', img_link)]

    return random.choice(img_links)

#set route for user navigation
@app.route('/')

def index():
    return render_template("index.html",band_names = display_bands)

@app.route('/first_band', methods=['GET', 'POST'])
def first_band():
    lines = []
    for i in range(N_LINES):
        while True:
            try:
                lines.append(get_random_line(bands[0]))
            except:
                ()
            else:
                break

    word_sets = []
    for line in lines:
        temp = []
        for word in get_tokens(line):
            if not word in stopwords:
                temp.append(word)
        word_sets.append(temp)

    img_words = [random.choice(word_set) for word_set in word_sets]

    img_url = get_art(img_words)
    print(img_url)

    return render_template('first_band.html', band_name=bands[0], lines = lines,image=img_url,band_names=display_bands)

@app.route('/second_band', methods=['GET', 'POST'])
def second_band():
    lines = []
    for i in range(N_LINES):
        while True:
            try:
                lines.append(get_random_line(bands[1]))
            except:
                ()
            else:
                break

    word_sets = []
    for line in lines:
        temp = []
        for word in get_tokens(line):
            if not word in stopwords:
                temp.append(word)
        word_sets.append(temp)

    img_words = [random.choice(word_set) for word_set in word_sets]

    img_url = get_art(img_words)

    return render_template('second_band.html', band_name=bands[1], lines = lines,image=img_url,band_names=display_bands)

@app.route('/third_band', methods=['GET', 'POST'])
def third_band():
    lines = []
    for i in range(N_LINES):
        while True:
            try:
                lines.append(get_random_line(bands[2]))
            except:
                ()
            else:
                break

    word_sets = []
    for line in lines:
        temp = []
        for word in get_tokens(line):
            if not word in stopwords:
                temp.append(word)
        word_sets.append(temp)

    img_words = [random.choice(word_set) for word_set in word_sets]

    img_url = get_art(img_words)

    return render_template('third_band.html', band_name=bands[2], lines = lines,image=img_url,band_names=display_bands)

@app.route('/fourth_band', methods=['GET', 'POST'])
def fourth_band():
    lines = []
    for i in range(N_LINES):
        while True:
            try:
                lines.append(get_random_line(bands[3]))
            except:
                ()
            else:
                break

    word_sets = []
    for line in lines:
        temp = []
        for word in get_tokens(line):
            if not word in stopwords:
                temp.append(word)
        word_sets.append(temp)

    img_words = [random.choice(word_set) for word_set in word_sets]

    img_url = get_art(img_words)

    return render_template('fourth_band.html', band_name=bands[3], lines = lines,image=img_url,band_names=display_bands)

@app.route('/fifth_band', methods=['GET', 'POST'])
def fifth_band():
    lines = []
    for i in range(N_LINES):
        while True:
            try:
                lines.append(get_random_line(bands[4]))
            except:
                ()
            else:
                break

    word_sets = []
    for line in lines:
        temp = []
        for word in get_tokens(line):
            if not word in stopwords:
                temp.append(word)
        word_sets.append(temp)

    img_words = [random.choice(word_set) for word_set in word_sets]

    img_url = get_art(img_words)

    return render_template('fifth_band.html', band_name=bands[4], lines = lines,image=img_url,band_names=display_bands)
    
