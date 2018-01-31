# # An example of embedding CEF browser in a PyQt4 application.
# # Tested with PyQt 4.10.3 (Qt 4.8.5).

import sys
import subprocess
import psycopg2, psycopg2.extras
import os, sys
import subprocess,time,socket

from datetime import *
import base64
from License import Generator as GetLicense

dbname = 'saleor'
con = None
proc = None
initial_width = 800
initial_height = 600
max_width = 0
max_height = 0
min_width = 800
min_height = 600
window_title = "Ideal POS"
icon_name = "icon.png"
fullscreen_allowed = True
project_dir_name="app"
project_dir_path="../app/"
dev_tools_menu_enabled = True
libcef_dll = os.path.join(os.path.dirname(os.path.abspath(__file__)),
        'libcef.dll')


def format_machine(new_id):
    formatted = str(new_id)
    bb = base64.b64encode(bytes(formatted))
    bkey322 = bb.ljust(32)[:32]
    return bkey322

def windows():
    machine_id = subprocess.check_output('wmic csproduct get UUID').split('\n')[1].strip()
    machine_model_number = subprocess.check_output('wmic csproduct get IdentifyingNumber').split('\n')[1].strip()
    new_id = '{0}@/{1}*'.format(machine_id, machine_model_number)
    mid = format_machine(new_id)
    return mid

def generate_license():
    mac = windows()
    end_date = (datetime.today() + timedelta(days=30)).date().isoformat()
    gl = GetLicense(mac, end_date)
    return gl.license()


def dbmigrate():
    try:
        keyfiles = generate_license()
        keyfile, check = keyfiles.split('###')
        keyfile = keyfile.replace('\r', '').replace('\n', '')
        check = check.replace('\r', '').replace('\n', '')

        subprocess.call(['python','..\\' + project_dir_name + '\manage.pyc','makemigrations'], shell=True)
        subprocess.call(['python','..\\' + project_dir_name + '\manage.pyc','migrate',], shell=True)
        conn2 = psycopg2.connect("dbname='saleor' user='saleor' host='127.0.0.1' password='saleor'")
        conn2.autocommit = True
        cur3 = conn2.cursor()
        cur3.execute("""INSERT INTO userprofile_user(name, email, is_superuser, is_active, is_staff, password, image, send_mail, date_joined) values('admin', 'admin@example.com', True, True, True, 'pbkdf2_sha256$30000$28uVy3qLTKlJ$npN/SiLkufzhREcOyYQFmWmzh1s/ZIo5qXk9/qSWSmE=','', True, now())""")
        cur3.execute("""INSERT INTO site_files(file, "check", created, modified) values('"""+keyfile+"""', '"""+check+"""', now(), now())""")
        conn2.commit()
        conn2.close()
    except Exception, e:
        print (e)

def createdb_resource(cur, con):
    try:
        cur.execute("CREATE ROLE saleor WITH SUPERUSER CREATEDB CREATEROLE LOGIN PASSWORD 'saleor'")
        cur.execute('CREATE DATABASE {} OWNER saleor;'.format('saleor'))
        con.close()
        conn = psycopg2.connect("dbname='saleor' user='saleor' host='127.0.0.1' password='saleor'")
        conn.autocommit = True
        cur2 =conn.cursor()
        cur2.execute('CREATE EXTENSION {};'.format('hstore'))
        cur2.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
        conn.commit()
        conn.close()
        dbmigrate()
    except Exception, e:
        print (e)

def create_resources():
    try:
        con = psycopg2.connect(dbname='postgres',user='postgres', host='127.0.0.1',password='root')
        con.autocommit = True
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("select * from pg_database where datname = %(dname)s", {'dname': dbname })
        answer = cur.fetchall()
        if len(answer) > 0:
            print "Database {} exists".format(dbname)
            cur.execute("DROP DATABASE saleor")
            cur.execute("DROP ROLE saleor")
            createdb_resource(cur, con)
        else:
            print "Database {} does NOT exist".format(dbname)
            createdb_resource(cur, con)
    except Exception, e:
        print "Error %s" %e
        sys.exit(1)
    finally:
        if con:
            con.close()



