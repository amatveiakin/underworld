from beaker.middleware import SessionMiddleware
from pprint import pformat
from cgi import parse_qs, escape
from hashlib import sha1
from sqlalchemy import *

def simple_app(environ, start_response):
    output = []
    head_html = """ <head>
        <link rel="stylesheet" type="text/css" href="style.css" />
        </head> """
    output.append(head_html)

    if ( environ['REMOTE_ADDR'] != "89.249.165.187"):
        start_response('403 FORBIDDEN', [('Content-type', 'text/html')])
        return []
    db = create_engine("mysql+pymysql://underworld:underworld@localhost/underworld")
    db.echo = False  # Try changing this to True and see what happens

    metadata = MetaData(db)

    users = Table('players', metadata, autoload=True)
    # Get the session object from the environ
    session = environ['beaker.session']

    if environ['REQUEST_METHOD'] == 'POST':
        d = parse_qs(environ['wsgi.input'].read().decode('utf-8'))
        #output.append(pformat(d))  
        if not 'username' in d or not 'password' in d or not 'password_repeat' in d:
            output.append("<p>You have to enter username and password.</p>")
        else:
            if d['password'][0] != d['password_repeat'][0]:
                output.append("<p>Passwords don't match<p>")
            else: 
                i = users.insert( )
                i.execute(name=d['username'][0], passwd_hash=passwd_hash(d['password'][0]))
    output.append('<form method="post" action=register.wsgi>')
    output.append('<label>username: </label>')
    output.append('<input type="text" name="username"><br>')
    output.append('<label>password: </label>')
    output.append('<input type="password" name="password"><br>')
    output.append('<label>repeat password: </label>')
    output.append('<input type="password" name="password_repeat"><br>')
    output.append('<input type="submit" value="Register!">')
    output.append('<input type="hidden" name="is_login" value="True">')
    output.append('</form>')
    session.save( )

    # Check to see if a value is in the session

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
