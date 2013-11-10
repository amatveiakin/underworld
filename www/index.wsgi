from beaker.middleware import SessionMiddleware
from pprint import pformat
from cgi import parse_qs
from hashlib import sha1
from sqlalchemy import Table,MetaData,create_engine
import os 
import re
bots_dir = '/home/kost/prog/underworld/bots'

login_form = [
'<form method="post" action=index.wsgi>',
'<label>username: </label>',
'<input type="text" name="username"><br>',
'<label>password: </label>',
'<input type="password" name="password"><br>',
'<input type="submit" value="Log in">',
'<input type="hidden" name="form_id" value="login">',
'</form>' ]

logout_form = [
'<form method="post" action=index.wsgi>',
'<input type="hidden" name="form_id" value="logout">',
'<input type="submit" value="Logout">',
'</form>' ]

upload_bot_form = [
'<form method="post" action=index.wsgi enctype="multipart/form-data">',
'<input type="hidden" name="form_id" value="upload_bot">',
'<div class="fileinputs">',
    '<input type="file" name="file" class="file"/>',
    '<div class="fakefile" align="right">',
        '<input type="button" value="Select file" />',
    '</div>',
'</div>',
'<label style="width:auto">Bot name:</label>',
'<input type="text" name="bot_name"></br>',
'<input type="submit" value="Upload">',
'</form>' ]

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
    db.echo = False

    metadata = MetaData(db)
    # Get the session object from the environ
    session = environ['beaker.session']

    if environ['REQUEST_METHOD'] == 'POST':
        d = parse_qs(environ['wsgi.input'].read().decode('utf-8'))
        if not 'form_id' in d:
            start_response('400 BAD REQUEST', [('Content-type', 'text/html')])
            return []
        if d['form_id'][0] == "login":
            if not 'username' in d or not 'password' in d:
                output.append("<p>You have to enter username and password.</p>")
            else:
                users = Table('players', metadata, autoload = True)
                s = users.select( users.c.name==d['username'][0] )
                users_found = s.execute( )
                user = users_found.fetchone( )
                if ( user and user['passwd_hash'] and passwd_check(d['password'][0], user['passwd_hash']) ):
                    session['logged_in'] = True
                    session['user'] = user
                    session.save( )
                    start_response('303 SEE OTHER', [('Content-type', 'text/html'), ('Location', '/')])
                    return []
                else:
                    session.pop("logged_in", "")
                    output.append('<p>Username or password is incorrect.</p>')
        elif d['form_id'][0] == 'logout':
            session.invalidate( )
            start_response('303 SEE OTHER', [('Content-type', 'text/html'), ('Location', '/')])
            return []
        elif d['form_id'][0] == 'upload_bot':
            bots = Table('bots', metadata, autoload = True)
            botNameRegex = "^[0-9a-zA-Z_]+$"
            if not re.match(botNameRegex, d['name']):
                output.append("<p>The bot name contains incorrect characters</p>")
            else:
                pass
                
                

            #fileData = d['file'].file.read( ))
            
        else:
            start_response('400 BAD REQUEST', [('Content-type', 'text/html')])
            return ["400 BAD REQUEST"]
    if 'logged_in' in session:
        output += upload_bot_form
        output += logout_form
    else:
        output += login_form
    output.append('<p><a href=register.wsgi>Registration page</a></p>')
    session.save( )

    start_response('200 OK', [('Content-type', 'text/html')])
    return output

# Configure the SessionMiddleware
session_opts = {
    'session.type' : 'file',
    'session.data_dir' : "/tmp/sessions",
    'session.timeout' : 1200
}

def debug_wrapper(f):
    def ff(environ, start_response):
        try:
            return f( environ, start_response)
        except Exception as e:
            start_response('500 INTERNAL SERVER ERROR', [('Context-type', 'text/plain')])
            return [repr(e)]
    return ff
def passwd_hash(password):
    return sha1((password + "pepper").encode("utf-8")).hexdigest( )
def passwd_check(password, stored_hash):
    return passwd_hash(password) == stored_hash

application = SessionMiddleware(debug_wrapper(simple_app), session_opts)
