from flasklyrics import db
from flasklyrics.models import User, Rhyme
from nltk.corpus import cmudict
import datetime

phon = {'NA': -1, 'AA': 0, 'AE': 1, 'AH': 2, 'AO': 3, 'AW': 4, 'AY': 5, 'B': 6, 'CH': 7, 'D': 8, 'DH': 9, 'EH': 10, 'ER': 11, 'EY': 12, 'F': 13, 'G': 14, 'HH': 15, 'IH': 16, 'IY': 17, 'JH': 18, 'K': 19, 'L': 20, 'M': 21, 'N': 22, 'NG': 23, 'OW': 24, 'OY': 25, 'P': 26, 'R': 27, 'S': 28, 'SH': 29, 'T': 30, 'TH': 31, 'UH': 32, 'UW': 33, 'V': 34, 'W': 35, 'Y': 36, 'Z': 37, 'ZH': 38}

def pron(w):
    return [pron for (word, pron) in cmudict.entries() if word == w]

d = cmudict.dict()
def nsyl(wordphrase):
    total = 0
    for word in wordphrase.split():
        try:
            total += [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
        except:
            return -1 # keyerror
    return total

def addWord(wordphrase, user=None):
    if (Rhyme.query.filter_by(phrase = wordphrase).first()):
        return
    if (not user):
        userid = 1
    else:
        userid = user.id
    word = wordphrase.split()[-1]
    p = pron(word)
    if (not p):
        return
    p = p[0] # use first pronunciation, change later
    if (len(p) < 3):
        p = ['NA'] * max(0, 3 - len(p)) + p
    rhyme = Rhyme(phrase = wordphrase, nsyl = nsyl(wordphrase), n_one = phon[p[-1].rstrip("012")], n_two = phon[p[-2].rstrip("012")], n_three = phon[p[-3].rstrip("012")], user_id = userid)
    db.session.add(rhyme)

def getRhyme(wordphrase, onlymatch = 3, limit=10):
    word = wordphrase.split()[-1]
    p = pron(word)
    nsylwp = nsyl(wordphrase)
    if (not p or len(p[0]) < 2):
        return
    p = p[0] # use first pronunciation, change later
    p.pop(0) # dont match first
    if (onlymatch == 1 or len(p) == 1):
        return Rhyme.query.filter_by(nsyl = nsylwp, n_one = phon[p[-1].rstrip("012")]).all()
    elif (onlymatch == 2 or len(p) == 2):
        return Rhyme.query.filter_by(nsyl = nsylwp, n_one = phon[p[-1].rstrip("012")], n_two = phon[p[-2].rstrip("012")]).all()
    else:
        return Rhyme.query.filter_by(nsyl = nsylwp, n_one = phon[p[-1].rstrip("012")], n_two = phon[p[-2].rstrip("012")], n_three = phon[p[-3].rstrip("012")]).all()

def lineGetter(filename):
    with open(filename) as fp:
        line = fp.readline()
        while line:
            yield line[0:-1]
            line = fp.readline()

def addFromFile(filename, quiet = 10):
    '''Usage: addFromFile('flasklyrics/sample/partialphrase.txt', 30)
    8 mins for 600 phrases'''
    g = lineGetter(filename)
    i = 0
    while True:
        n = 0
        try:
            n = next(g)
        except Exception as e:
            print(e)
            break
        try:
            addWord(n)
        except Exception as e:
            print(str(n) + " could not be added.")
            print(e)
        if quiet > 0 and i % quiet == 0:
            print(str(datetime.datetime.now()) + "   " + str(i))
        i += 1
    db.session.commit()
    print("All done.")

#from flasklyrics import bcrypt
#u = User(username="Admin", email = "admin@lyrix.com", password = bcrypt.generate_password_hash("password").decode('utf-8'))
#db.session.add(u)
#db.session.commit()
