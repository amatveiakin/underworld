from beaker.middleware import SessionMiddleware
from pprint import pformat
from cgi import parse_qs, escape
from hashlib import sha1
from sqlalchemy import *

def simple_app(environ, start_response):
    output = []
    output.append('<form method="post">')
    output.append('<input type="text" name="username">')
    output.append('<input type="text" name="password">')
    output.append('<input type="submit">')
    output.append('</form>')
    engine = create_engine("mysql+mysqlconnector://localhost")

    # Get the session object from the environ
    session = environ['beaker.session']
    if environ['REQUEST_METHOD'] == 'POST':
        # show form data as received by POST:
        d = parse_qs(environ['wsgi.input'].read().decode('utf-8'))
        if ( d['username'][0] == 'user' and d['password'][0] == 'pass' ):
            session['logged_in'] = True
        else:
            session.pop("logged_in", "")
    if 'logged_in' in session:
        output.append(pformat("logged in"))
    else:
        output.append(pformat("not logged in"))


    session.save( )

    # Check to see if a value is in the session

    start_response('200 OK', [('Content-type', 'text/html')])
    return output

# Configure the SessionMiddleware
session_opts = {
    'session.type': 'file',
    'session.data_dir' : "/tmp"
}
application = SessionMiddleware(simple_app, session_opts)

def passwd_hash(password):
    return sha1(password + "pepper")
def passwd_check(password, stored_hash):
    return passwd_hash(password) == stored_hash

