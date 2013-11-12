from beaker.middleware import SessionMiddleware
from pprint import pformat
from cgi import FieldStorage
from hashlib import sha1
from sqlalchemy import Table,MetaData,create_engine, select
from sqlalchemy.exc import IntegrityError
import os 
import re
import sys
import traceback
botsDir = '/home/kost/prog/underworld/bots'

head_html = [ '<head>',
    '<link rel="stylesheet" type="text/css" href="style.css" />',
    '</head>' ]

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
'<label>Bot name:</label>',
'<input type="text" name="bot_name"><br>',
'<label>Programing language:</label>',
'<select name="language">',
    '<option selected value="cpp">C++</option>',
    '<option value="python">Python 3.3</option>',
'</select><br>',
'<input type="submit" value="Upload">', '</form>' ]

def getValues(dbResult):
    return [ r.values() for r in dbResult ]
def getKeys(dbResult):
    return dbResult[0].keys()

def get_client_address(environ):
    try:
        return environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
    except KeyError:
        return environ['REMOTE_ADDR']

def htmlTable(keys, values):
    rowTemplate = '<tr>\n{0}\n</tr>\n'
    elemTemplate = '<td>{0}</td>'
    headTemplate = '<th>{0}</th>'
    elemToHtml = lambda elem: elemTemplate.format(elem)
    rowToHtml = lambda row: rowTemplate.format(" ".join(map(elemToHtml, row)))
    keyToHtml = lambda key: headTemplate.format(key)
    return ['<table>', rowTemplate.format(" ".join(map(keyToHtml, keys)))] +\
        list(map(rowToHtml, values)) + ['</table>']
def simple_app(environ, start_response):
    output = []
    output += head_html
    db = create_engine("mysql+pymysql://underworld:underworld@localhost/underworld")
    dbConnection = db.connect( )
    db.echo = False

    metadata = MetaData(db)
    # Get the session object from the environ
    session = environ['beaker.session']

    if environ['REQUEST_METHOD'] == 'POST':
        d = FieldStorage(fp=environ['wsgi.input'], environ=environ)
        if not 'form_id' in d:
            start_response('400 BAD REQUEST', [('Content-type', 'text/html')])
            return []
        if d['form_id'].value == "login":
            if not 'username' in d or not 'password' in d:
                output.append("<p>You have to enter username and password.</p>")
            else:
                users = Table('players', metadata, autoload = True)
                s = users.select( users.c.name==d['username'].value )
                users_found = s.execute( )
                user = users_found.fetchone( )
                if ( user and user['passwd_hash'] and passwd_check(d['password'].value, user['passwd_hash']) ):
                    session['logged_in'] = True
                    session['user'] = user
                    session.save( )
                    start_response('303 SEE OTHER', [('Content-type', 'text/html'), ('Location', '/')])
                    return []
                else:
                    session.pop("logged_in", "")
                    output.append('<p>Username or password is incorrect.</p>')
        elif d['form_id'].value == 'logout':
            session.invalidate( )
            start_response('303 SEE OTHER', [('Content-type', 'text/html'), ('Location', '/')])
            return []
        elif d['form_id'].value == 'upload_bot':
            if not 'logged_in' in session:
                output.append("<p>You are not logged in</p>")
            elif not 'bot_name' in d:
                output.append("<p>Please specify the bot name</p>")
            else:
                botName = d['bot_name'].value
                botNameRegex = "^[0-9a-zA-Z_]+$"
                if len(botName) > 20:
                    output.append("<p>Bot name too long</p>")
                elif not re.match(botNameRegex, botName):
                    output.append("<p>Bot name contains invalid characters</p>")
                else:
                    bots = Table('bots', metadata, autoload = True)
                    transaction = dbConnection.begin( )
                    try:
                        botFileName = os.path.join(botsDir, botName + ".tar")
                        insertRequest = bots.insert( ).values( name=botName, 
                            owner=session['user']['id'], 
                            tarfile=botFileName,
                            language=d['language'].value)
                        users = Table('players', metadata, autoload = True)
                        updateRequest = users.update( ).\
                            where(users.c.id==session['user']['id']).\
                            values(bots_no=users.c.bots_no + 1)
                        dbConnection.execute(updateRequest)
                        dbConnection.execute(insertRequest)
                        fileData = d['file'].file.read( )
                        outputFile = open(botFileName, "xb")
                        outputFile.write(fileData)
                        output.append("<p>Bot successfully uploaded</p>") 
                        transaction.commit()
                    except IntegrityError as e:
                        if e.orig.args[0] == 1062:
                            output.append("<p>The bot with name %s already exists</p>" % e.params[0])
                        transaction.rollback()
                    except Exception as e:
                        raise
                        transaction.rollback()
        else:
            start_response('400 BAD REQUEST', [('Content-type', 'text/plain')])
            return ["400 BAD REQUEST"]
    if 'logged_in' in session:
        output.append('<h2>Upload a bot</h2>')
        output += upload_bot_form
        output += logout_form
        bots = Table('bots', metadata, autoload = True)
        selectRequest = select( [bots.c.id, bots.c.name, bots.c.compile_status]).\
            where(bots.c.owner == session['user']['id'] )
        db_result = selectRequest.execute().fetchall()
        values = getValues(db_result)
        keys = getKeys(db_result)
        for i in values:
            i.append('<input type="checkbox" name=select{0}/>'.format(i[0]))
        keys.append("select")
        output.append('<h2>Your bots</h2>')
        output += htmlTable(getKeys(db_result), values)
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
            return map(lambda x: x + "\n", f(environ, start_response))
        except Exception as e:
            start_response('500 INTERNAL SERVER ERROR', [('Content-type', 'text/plain')])
            return traceback.format_tb(e.__traceback__) + [repr(e)]
    return ff

def passwd_hash(password):
    return sha1((password + "pepper").encode("utf-8")).hexdigest( )
def passwd_check(password, stored_hash):
    return passwd_hash(password) == stored_hash

application = SessionMiddleware(debug_wrapper(simple_app), session_opts)
