from beaker.middleware import SessionMiddleware
from pprint import pformat
from cgi import parse_qs, escape
from hashlib import sha1
from sqlalchemy import *

def get_client_address(environ):
    try:
        return environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
    except KeyError:
        return environ['REMOTE_ADDR']

def simple_app(environ, start_response):
    output = []
    head_html = """ <head>
        <link rel="stylesheet" type="text/css" href="style.css" />
        </head> """
    output.append(head_html)
    db = create_engine("mysql+pymysql://underworld:underworld@localhost/underworld")
    db.echo = False  # Try changing this to True and see what happens

    metadata = MetaData(db)
    users = Table('players', metadata, autoload = True)
    # Get the session object from the environ
    session = environ['beaker.session']

    if environ['REQUEST_METHOD'] == 'POST':
        d = parse_qs(environ['wsgi.input'].read().decode('utf-8'))
        if not 'is_login' in d:
            output.append("<p>ERROR</p>")
        if d['is_login'][0] == "True":
            if not 'username' in d or not 'password' in d:
                output.append("<p>You have to enter username and password.</p>")
            else:
                s = users.select( users.c.name==d['username'][0] )
                users_found = s.execute( )
                user = users_found.fetchone( )
                if ( user and passwd_check(d['password'][0], user['passwd_hash']) ):
                    session['logged_in'] = True
                else:
                    session.pop("logged_in", "")
                    output.append("<p>Username or password is incorrect.</p>")
        else:
            session.invalidate( )

    if 'logged_in' in session:
        output.append(pformat("logged in"))
        output.append('<form method="post" action=index.wsgi>')
        output.append('<input type="hidden" name="is_login" value=False>')
        output.append('<input type="submit" value="Logout">')
        output.append('</form>')
    else:
        output.append('<form method="post" action=index.wsgi>')
        output.append('<label>username: </label>')
        output.append('<input type="text" name="username"><br>')
        output.append('<label>password: </label>')
        output.append('<input type="password" name="password"><br>')
        output.append('<input type="submit" value="Log in">')
        output.append('<input type="hidden" name="is_login" value="True">')
        output.append('</form>')
    session.save( )


    start_response('200 OK', [('Content-type', 'text/html')])
    # Check to see if a value is in the session
    return output

# Configure the SessionMiddleware
session_opts = {
    'session.type' : 'file',
    'session.data_dir' : "/tmp/sessions",
    'session.timeout' : 1200
}
application = SessionMiddleware(simple_app, session_opts)

def passwd_hash(password):
    return sha1((password + "pepper").encode("utf-8")).hexdigest( )
def passwd_check(password, stored_hash):
    return passwd_hash(password) == stored_hash.decode("utf-8")

