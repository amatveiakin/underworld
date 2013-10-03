from beaker.middleware import SessionMiddleware
from pprint import pformat
from cgi import parse_qs, escape
from hashlib import sha1
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from wheezy.captcha.image import *
from io import BytesIO
import random
import string
import re

def gen_captcha( ):
    generator = captcha([text(fonts=['/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono.ttf'],
              drawings = [warp(), rotate(15), offset( )]), smooth(), noise(number=100), curve(), curve( ) ])
     
    answer = "".join( [random.choice(string.ascii_letters[:26]) for i in range(6)] )
    captcha_image = generator(answer)
    bytesIO = BytesIO()
    captcha_image.save(bytesIO, 'JPEG')
    captcha_data = bytesIO.getvalue() 
    bytesIO.close( )
    return (answer, captcha_data)

def simple_app(environ, start_response):
    #if ( environ['REMOTE_ADDR'] != "89.249.165.187"):
        #start_response('403 FORBIDDEN', [('Content-type', 'text/jpeg')])
        #return []
    output = []
    # Get the session object from the environ
    session = environ['beaker.session']
    if environ['REQUEST_METHOD']  == 'GET':
        d = parse_qs(environ['QUERY_STRING'])
        if 'captcha' in d:
            if not 'captcha_data' in session:
                start_response('404 NOT FOUND', [('Content-type', 'plain/text')])
                return ["Don't do this, please"]
            start_response('200 OK', [('Content-type', 'image/png')])
            session.pop("captcha_answer")
            return [session.pop("captcha_data")]
            
    head_html = """ <head>
        <link rel="stylesheet" type="text/css" href="style.css" />
        </head> """
    output.append(head_html)

    db = create_engine("mysql+pymysql://underworld:underworld@localhost/underworld")
    db.echo = False  # Try changing this to True and see what happens

    metadata = MetaData(db)

    users = Table('players', metadata, autoload=True)

    if environ['REQUEST_METHOD'] == 'POST':
        d = parse_qs(environ['wsgi.input'].read().decode('utf-8'))
        #output.append(pformat(d))  
        if not 'username' in d or not 'password' in d or not 'password_repeat' or \
           not 'captcha_answer_user' in d:
            output.append("<p>All fields are required.</p>")
        else:
            username = d['username'][0]
            username_regex = r"[A-Za-z0-9_\-]+$"
            if len(username) > users.c.name.type.length:
                output.append("<p>Username must not be longer than %d characters</p>" % users.c.name.type.length)
            elif not re.match(username_regex, username):
                output.append("<p>Bad characters in the username</p>")
            elif d['password'][0] != d['password_repeat'][0]:
                output.append("<p>Passwords don't match.<p>")
            elif not 'captcha_answer' in session or d['captcha_answer_user'][0] != session['captcha_answer']:
                output.append("<p>The text is incorrect - try again.</p>")
            else: 
                i = users.insert().values( name=d['username'][0], passwd_hash=passwd_hash(d['password'][0]))
                try:
                    i.execute()
                    output.append("<p>%s successfully registered</p>" % d['username'][0])
                except IntegrityError as e:
                    if e.orig.args[0].args[0] == 1062:
                        output.append("User with name %s already exists" % e.params[0])
    output.append('<form method="post" action=register.wsgi>')
    output.append('<label>username: </label>')
    output.append('<input type="text" name="username"><br>')
    output.append('<label>password: </label>')
    output.append('<input type="password" name="password"><br>')
    output.append('<label>repeat password: </label>')
    output.append('<input type="password" name="password_repeat"><br>')
    output.append('<label>text on the picture:</label>')
    output.append('<input type="text" name="captcha_answer_user"><br>')
    output.append('<img src="register.wsgi?captcha=1" method="get"><br>')
    output.append('<input type="submit" value="Register!">')
    output.append('</form>')
    output.append('<a href="/">Home</a>')

    # Check to see if a value is in the session

    (answer, data) = gen_captcha( )
    session['captcha_answer'] = answer
    session['captcha_data'] = data
    session.save( )
    start_response('200 OK', [('Content-type', 'text/html')])
    return output

# Configure the SessionMiddleware
session_opts = {
    'session.type': 'file',
    'session.data_dir' : "/tmp/sessions",
    'session.timeout' : 30
}
application = SessionMiddleware(simple_app, session_opts)

def passwd_hash(password):
    return sha1((password + "pepper").encode('utf-8')).hexdigest( )
def passwd_check(password, stored_hash):
    return passwd_hash(password) == stored_hash
