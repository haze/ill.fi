# uncompyle6 version 2.11.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Apr  4 2017, 08:47:57) 
# [GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.38)]
# Embedded file name: /Users/haze/Projects/Websites/ill.fi/illload/illload.py
# Compiled at: 2017-06-24 15:18:54
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher
from werkzeug.utils import secure_filename
from PIL import Image
from validate_email import validate_email
import random
import string
import flask
import requests
import flask_login
import collections
import json
import os
import math
app = flask.Flask(__name__)
app.secret_key = 'as;ldkfjasl;dkfjas;dlfkj'
app.debug = True
ph = PasswordHasher()
db = SQLAlchemy(app)
app.config['MAX_CONTENT_LENGTH'] = 524288000
app.config['UPLOAD_FOLDER'] = os.getcwd() + '/illload/uploads/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/illload.db'

class User(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(80), primary_key=True, nullable=False)
    upload_key = db.Column(db.String(26), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.authenticated = False
        self.upload_key = rand_str(26)

    def __repr__(self):
        return '<User e:{0}, u:{1}>'.format(self.email, self.username)

    def is_active(self):
        return True

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.String(4), primary_key=True)
    user_email = db.Column(db.String(80))
    deletion_key = db.Column(db.String(43), nullable=False)
    original_name = db.Column(db.String(128), nullable=False)

    def __init__(self, filename, email, original_name, del_key):
        self.id = filename
        self.user_email = email
        self.original_name = original_name
        self.deletion_key = del_key

    def __repr__(self):
        return '<File %r>' % self.id


class Invite(db.Model):
    __tablename__ = 'invites'
    key = db.Column(db.String(24), primary_key=True)
    user_email = db.Column(db.String(80))

    def __init__(self, key, email):
        self.key = key
        self.user_email = email

    def __repr__(self):
        return '<Invite [{0}] from {1}>'.format(self.key, self.user_email)


login_manager = flask_login.LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
blocked_extensions = [
 'js',
 'php',
 'php4',
 'php3',
 'phtml',
 'rhtml',
 'html',
 'xhtml',
 'jhtml',
 'css',
 'swf',
 'exe']

def convert_size(size_bytes):
    if size_bytes == 0:
        return '0B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '%s %s' % (s, size_name[i])


def generate_filename():
    gen = rand_str(4)
    while does_filename_exist(gen):
        gen = rand_str(4)

    return gen


def generate_deletion_key():
    gen = rand_str(43)
    while does_filename_exist(gen):
        gen = rand_str(43)

    return gen


def does_deletion_key_exist(key):
    return File.query.filter_by(deletion_key=key).first() is not None


def does_filename_exist(filen):
    return File.query.filter_by(id=filen).first() is not None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() not in blocked_extensions


def rand_str(length):
    return ''.join((random.choice(string.lowercase) for i in range(length)))


def crypt_password(passx):
    return ph.hash(passx)


def verify_password(hash, passx):
    try:
        return ph.verify(hash, passx)
    except:
        return False


def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    return total_size


def strip_exif(image):
    dat = list(image.getdata())
    final = Image.new(image.mode, image.size)
    final.putdata(dat)
    return final


def invite_exists(invite):
    allInvites = Invite.query.all()
    for inv in allInvites:
        if inv.key == invite:
            return True

    return False


def key_matches_find(key):
    allUsers = User.query.all()
    for user in allUsers:
        if user.upload_key == key:
            return (user.email, True)

    return (
     None, False)


def get_files(email):
    return File.query.filter_by(user_email=email).all()


def key_matches(email, key):
    if email_exists(email):
        user = Users.query.filter_by(email=email).first()
        if user.upload_key == key:
            return (Some(email), True)
    return (
     None, False)


def email_exists(email):
    allUsers = User.query.all()
    for user in allUsers:
        if user.email == email:
            return True

    return False


def user_exists(username):
    allUsers = User.query.all()
    for user in allUsers:
        if user.username == username:
            return True

    return False


@login_manager.user_loader
def user_loader(email):
    if email_exists(email):
        usr = User.query.filter_by(email=email).first()
        usr.email = email
        return usr
    else:
        return


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    passw = request.form.get('password')
    if email_exists(email):
        user = User.query.get(email)
        if verify_password(user.password, passw):
            return user


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.username


@app.route('/', defaults={'xfile': ''})
@app.route('/<xfile>')
def root(xfile):
    if xfile == '':
        DIR = app.config['UPLOAD_FOLDER']
        return flask.render_template('home.html', users=User.query.count(), fsize=convert_size(get_size(DIR)), files=len([ name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name)) ]))
    else:
        if os.path.isfile('/{0}/{1}'.format(app.config['UPLOAD_FOLDER'], xfile)):
            return flask.send_from_directory('uploads', xfile)
        return (
         flask.render_template('404.html'), 404)


@app.errorhandler(404)
def page_not_found(e):
    return (
     flask.render_template('404.html'), 404)


@app.route('/faq')
def faq():
    return flask.render_template('faq.html')


@app.route('/join', methods=['GET', 'POST'])
def join():
    if flask.request.method == 'GET':
        return (flask.render_template('join.html'),)
    invite = flask.request.form['invite']
    email = flask.request.form['email']
    username = flask.request.form['username']
    passw = flask.request.form['password']
    if not invite:
        flask.flash('Invite not provided.')
    elif not email:
        flask.flash('Email not provided.')
    elif not username:
        flask.flash('Username not provided.')
    elif not passw:
        flask.flash('Password not provided.')
    elif not validate_email(email, verify=True):
        flask.flash('Invalid Email.')
    else:
        if invite_exists(invite):
            user = User(username, email, ph.hash(passw))
            user.authenticated = True
            with db.session.no_autoflush:
                db.session.add(user)
                db.session.delete(Invite.query.filter_by(key=invite).first())
                db.session.commit()
                flask_login.login_user(user, remember=True)
            return flask.redirect(flask.url_for('root'))
        flask.flash('Invalid Invite.')
    return flask.render_template('join.html')


@app.route('/api/invite/list')
def list_invite():
    response = {}
    if 'email' in flask.request.args:
        email = flask.request.args.get('email')
        response = {'error': False,
           'invites': '{0}'.format(Invite.query.all())
           }
    else:
        response = {'error': True,'message': 'email not provided'
           }
    return flask.jsonify(**response)


@app.route('/api/invite/generate')
def generate_invite():
    response = {}
    if 'email' in flask.request.args:
        email = flask.request.args.get('email')
        if email is not None:
            invite = rand_str(24)
            response = {'error': False,
               'invite': invite
               }
            db.session.add(Invite(invite, email))
            db.session.commit()
            return flask.redirect(flask.url_for('root'))
    response = {'error': True,
       'message': 'email not provided'
       }
    return flask.jsonify(**response)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html')
    email = flask.request.form['email']
    passw = flask.request.form['password']
    pUser = User.query.get(email)
    if pUser:
        if verify_password(pUser.password, passw):
            pUser.authenticated = True
            db.session.add(pUser)
            db.session.commit()
            flask_login.login_user(pUser, remember=True)
        else:
            flask.flash('Incorrect password.')
    else:
        flask.flash('Email not found.')
    return flask.redirect(flask.url_for('root'))


@app.route('/profile')
@flask_login.login_required
def profile():
    return flask.render_template('profile.html', files=get_files(flask_login.current_user.email))


@app.route('/logout')
@flask_login.login_required
def logout():
    user = flask_login.current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    flask_login.logout_user()
    return flask.redirect(flask.url_for('root'))


@app.route('/docs')
def docs():
    return flask.render_template('docs.html')


@app.route('/api/upload', methods=['GET', 'POST'])
def upload():
    if flask.request.method == 'POST':
        if 'key' not in flask.request.form:
            return flask.jsonify({'error': True,
               'message': 'api key not provided'
               })
        uploaded_files = flask.request.files.getlist('file')
        if 'file' not in flask.request.files and len(uploaded_files) == 0:
            return flask.jsonify({'error': True,
               'message': 'file parameter not found'
               })
        result = {'files': {}}
        for file in uploaded_files:
            key = flask.request.form['key']
            email, exists = key_matches_find(key)
            if file.filename == '':
                result['files'][file.filename] = {'error': True,'message': 'empty filename'
                   }
            if file and exists:
                if not allowed_file(file.filename):
                    result['files'][file.filename] = {'filename': file.filename,'error': True,
                       'message': 'bad filetype'
                       }
                xFileName = generate_filename()
                _, file_extension = os.path.splitext(file.filename)
                xFileName = '{0}{1}'.format(xFileName, file_extension)
                del_key = generate_deletion_key()
                uFile = File(xFileName, email, file.filename, del_key)
                path = os.path.join(app.config['UPLOAD_FOLDER'], xFileName)
                file.save(path)
                if file_extension.lower() == '.png':
                    imag = Image.open(path)
                    os.remove(path)
                    strip_exif(imag).save(path, 'PNG', quality=75)
                else:
                    if file_extension.lower() == '.jpg' or file_extension.lower() == '.jpeg':
                        imag = Image.open(path)
                        os.remove(path)
                        strip_exif(imag).save(path, 'JPEG', quality=75)
                    db.session.add(uFile)
                    db.session.commit()
                    if len(uploaded_files) == 1:
                        return flask.jsonify({'original_name': file.filename,
                           'error': False,
                           'deletion_key': del_key,
                           'filename': xFileName
                           })
                result['files'][file.filename] = {'original_name': file.filename,
                   'error': False,
                   'deletion_key': del_key,
                   'filename': xFileName
                   }

        return flask.jsonify(**result)
    else:
        return flask.render_template('upload.html')


@app.route('/api/upload/delete_all', methods=['POST'])
def delete_all():
    if 'key' in flask.request.form:
        if 'email' in flask.request.form:
            email = flask.request.form['email']
            files = get_files(email)
            for file in files:
                sFile = File.query.filter_by(id=file.id).first()
                if sFile == None:
                    continue
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], sFile.id))
                db.session.delete(sFile)
                db.session.commit()

            return flask.jsonify({'error': False,
               'message': 'successfully deleted all files'
               })
        return flask.jsonify({'error': True,
           'message': 'email is not provided'
           })
    else:
        return flask.jsonify({'error': True,
           'message': 'upload key not provided'
           })


@app.route('/api/upload/delete', methods=['POST', 'GET'])
def delete_upload():
    if 'deletion_key' in flask.request.form:
        if 'file' not in flask.request.form:
            return flask.jsonify({'error': True,
               'message': 'file parameter not provided'
               })
        file = flask.request.form['file']
        del_key = flask.request.form['deletion_key']
        sFile = File.query.filter_by(id=file).first()
        if sFile == None:
            return flask.jsonify({'error': True,
               'message': 'file {0} not found'.format(file)
               })
        if sFile.deletion_key == del_key:
            with db.session.no_autoflush:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], sFile.id))
                db.session.delete(sFile)
                db.session.commit()
                return flask.jsonify({'error': False,
                   'message': 'successfully deleted file {0}'.format(sFile.id)
                   })
        else:
            return flask.jsonify({'error': True,
               'message': 'incorrect deletion key for file {0}'.format(file.filename)
               })
    else:
        return flask.jsonify({'error': True,
           'message': 'deletion key parameter not provided'
           })
    return


@app.route('/api/user/exists', methods=['GET', 'POST'])
def user_exists():
    response = {}
    if 'email' in flask.request.args:
        email = flask.request.args.get('email')
        response = {'error': False,
           'exists': email in users
           }
    else:
        response = {'error': True,'message': 'email not provided'
           }
    return flask.jsonify(**response)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.redirect(flask.url_for('login'))
# okay decompiling illload/illload.pyc
