from http.server import SimpleHTTPRequestHandler,HTTPServer
import cgi
import mysql.connector
import time
import requests
import json
from mysql.connector import errorcode
import math
import threading
import sys
import datetime
import urllib.parse
import os
import email.utils
from http import HTTPStatus
dict_requests_patterns ={}
last_fids = {}

#todo словить исключения сбрасывания соединения

TABLES = {"table2": 'CREATE TABLE table2 (id INT AUTO_INCREMENT PRIMARY KEY, district CHAR(50), amount int(10), x DOUBLE(20,15), y DOUBLE(20,15))',
"table4": 'CREATE TABLE table4 (id INT AUTO_INCREMENT PRIMARY KEY, date CHAR(10), num CHAR(15), x DOUBLE(25,15), y DOUBLE(25,15))',
"table5": 'CREATE TABLE table5 (id INT AUTO_INCREMENT PRIMARY KEY, date CHAR(10),  x DOUBLE(25,15), y DOUBLE(25,15))'
          }

get_all_table2 = ('SELECT district FROM table2')
get_all_table4  = ('SELECT *FROM table4')


add_data_table2 =("INSERT INTO  table2"
        "(district, amount, x, y) "
        "VALUES (%s, %s, %s, %s)")
add_data_table4 =("INSERT INTO  table4"
        "(date, num, x, y) "
        "VALUES (%s, %s, %s, %s)")

update_data_table2 = ('UPDATE table2 SET amount = %s WHERE district = %s')
update_data_table4 = ('UPDATE infected SET amount = %s WHERE district = %s')

current_disrict_in_base = []
test_config = {
    'user': 'user1',
    'password': 'Eteben_22',
    'host': 'rc1a-5whcu97g27evsocc.mdb.yandexcloud.net',
    'ssl_ca' : 'C:/Users/kuzin/.mysql/root.crt',
    'database': 'db1',
    'raise_on_warnings': True
}
#подключение к базе mysql
try:
    cnx = mysql.connector.connect(**test_config)
    print("mysql connected")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
'''
cursor = cnx.cursor(buffered=True)
cursor.execute("DROP TABLE table4")
cursor.execute("DROP TABLE table2")
# создание  таблиц

for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

'''

class Server(SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            print("isdir true")
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            for index in "page.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break

        ctype = self.guess_type(path)
        # check for trailing "/" which should return 404. See Issue17324
        # The test for this was added in test_httpserver.py
        # However, some OS platforms accept a trailingSlash as a filename
        # See discussion on python-dev and Issue34711 regarding
        # parseing and rejection of filenames with a trailing slash
        if path.endswith("/"):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        try:
            fs = os.fstat(f.fileno())
            # Use browser cache if possible
            if ("If-Modified-Since" in self.headers
                    and "If-None-Match" not in self.headers):
                # compare If-Modified-Since and time of last file modification
                try:
                    ims = email.utils.parsedate_to_datetime(
                        self.headers["If-Modified-Since"])
                except (TypeError, IndexError, OverflowError, ValueError):
                    # ignore ill-formed values
                    pass
                else:
                    if ims.tzinfo is None:
                        # obsolete format with no timezone, cf.
                        # https://tools.ietf.org/html/rfc7231#section-7.1.1.1
                        ims = ims.replace(tzinfo=datetime.timezone.utc)
                    if ims.tzinfo is datetime.timezone.utc:
                        # compare to UTC datetime of last modification
                        last_modif = datetime.datetime.fromtimestamp(
                            fs.st_mtime, datetime.timezone.utc)
                        # remove microseconds, like in If-Modified-Since
                        last_modif = last_modif.replace(microsecond=0)

                        if last_modif <= ims:
                            self.send_response(HTTPStatus.NOT_MODIFIED)
                            self.end_headers()
                            f.close()
                            return None

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified",
                             self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f
        except:
            f.close()
            raise
    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        print("Request from:{}".format(self.client_address))
        print(self.requestline)
        print(self.command)
        print(self.path)
        print(self.headers)
        lock.acquire()
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()
        lock.release()

    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))

        # add a property to the object, just to mess with data
        message['received'] = 'ok'

        # send the message back
        self._set_headers()
        self.wfile.write(get_database_in_bytes())

def run(server_class= HTTPServer, handler_class=Server, port=8008,address = '127.0.0.1'):
    global httpd
    server_address = (address, port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd on port {} and address {}'.format(port,address))
    httpd.serve_forever()

def projected_coords_to_sphere(x,y):
    a = 6378137.0
    lat = 0.5 * (4 * math.atan(math.pow(math.e,float(y/a))) - math.pi)
    long = x/a
    return math.degrees(long),math.degrees(lat)

def check(district_name):
    for element in current_disrict_in_base:
        if district_name.strip() == element[0].strip():
            return True
    return False

def print_headers(headers: dict):
    """
    Печатает заголовки запроса в окно вывода
    :param headers: словарь с заголовками
    :return:
    """
    for item in headers:
        print(item + ":" + headers[item])

def create_session():
    session = requests.session()
    home_page = send_request(dict_requests_patterns["Home_req"], session)
    if home_page.status_code == 200:
        print("home done")
    return session

def send_request(req: dict, session):
    """
    Отправляет все виды http запросов

    :param req: заголовки запроса
    :param session: объект сессии
    :return: возвращает ответ веб-ресурса
    """
    response = None
    if req["Request"] == "post":
        response = session.post(url=req["Url"], data=json.dumps(req["Data"]), headers=req["Headers"], verify=False)
    elif req["Request"] == "get":
        response = session.get(url=req["Url"], headers=req["Headers"], params=req["Payloads"], verify=False)
    elif req["Request"] == "head":
        response = session.head(url=req["Url"], headers=req["Headers"], params=req["Payloads"], verify=False)
  # self.print_info_request(response)
  # self.print_info_response(response)
    return response

def read_json(filename, lastfidsfile):
    with open(filename, 'r', encoding='utf-8') as file:
        global dict_requests_patterns
        dict_requests_patterns = json.loads(file.read())
    with open(lastfidsfile, 'r', encoding='utf-8') as fil:
        global last_fids
        last_fids =  json.loads(fil.read())

def safe_last_fids(file:str, data):
    with open(file, "w", encoding="utf-8") as file:
        json.dump(data, file)

def print_base(table_name):
    cursor.execute("SELECT * FROM {}".format(table_name))
    for id in cursor:
        print(id)

def get_database_in_bytes():
    response ={"base1":[], "base2": None}
    cursor.execute("SELECT * FROM table2")
    for row in cursor:
        row_json = {"district": row[1], "amount": row[2],"lon":row[3], "lat":row[4]}
        response["base1"].append(row_json)
    cursor.execute("SELECT * FROM table4")
    for row in cursor:
        row_json = {"date": row[1], "case": row[2], "lon": row[3], "lat": row[4]}
        response["base1"].append(row_json)
    return bytes(json.dumps(response),encoding="utf-8")

def update_bases(session):
    lock.acquire()
    '''
    while flag_base==True:
        
        cursor.execute(get_all_table2)
        global current_disrict_in_base
        current_disrict_in_base = cursor.fetchall()
        resp2 = send_request(dict_requests_patterns["2"], session).json()
        for data in resp2["features"]:
            print(data)
            district_name = ""
            namename_list = data["attributes"]["name"].split()
            x, y = projected_coords_to_sphere(data['geometry']['x'], data['geometry']['y'])
            for part in namename_list[0:-4]:
                district_name += part + " "
            amount_infected = int(namename_list[-1])
            data_for_base = (district_name, amount_infected, x, y)
            print(data_for_base)
            if check(district_name) == True:
                cursor.execute(
                    'UPDATE table2 SET amount = {} , x = {} , y = {} WHERE district = "{}"'.format(amount_infected, x,
                                                                                                   y,
                                                                                                   district_name.strip()))
            else:
                print("NEW DISTRICT")
                cursor.execute(add_data_table2, data_for_base)
            cnx.commit()
        # обновление базы 4
        resp4 = send_request(dict_requests_patterns["4"], session).json()


        current_last_index = last_fids["table4"]
        for data in resp4["features"][0:]:
            name_list = data["attributes"]["name"].split(" ")
            fid = data["attributes"]["FID"]
            data_for_base = ()
            date = "00:00:00";
            num = ""
            x, y = projected_coords_to_sphere(data['geometry']['x'], data['geometry']['y'])
            if fid != 170 and fid != 131 and fid != 770:
                num = name_list[0]
                date = name_list[-1]
            elif fid == 170:
                num = name_list[0] + name_list[1] + name_list[2]
            elif fid == 131:
                num = name_list[0]
            else:
                num = name_list[0]
                date = name_list[-2]
            data_for_base = (date, num, x, y)
            print(data_for_base)
            cursor.execute(add_data_table4, data_for_base)
            cnx.commit()
            last_fids["table4"] += 1
        print_base("table4")
        print_base("table2")
        print("Base has benn updated , time:{}".format(datetime.datetime.now()))
    '''
    lock.release()
    time.sleep(3600)

read_json("geogovrb.txt", "lastfids.txt")
session = create_session()
lock = threading.Lock()
update_base_thread = None
listening_thread = None
httpd = HTTPServer
flag_base = True
flag_program = True

if __name__ == "__main__":
    from sys import argv
    update_base_thread = threading.Thread(target=update_bases, args= (session,),daemon=True)
    update_base_thread.start()
    if len(argv) == 2:
        listening_thread =  threading.Thread(target=run, args= (int(argv[1])))
    if len(argv) == 3:
        listening_thread = threading.Thread(target=run, args=(int(argv[1]), str(argv[2])))
    else:
        listening_thread = threading.Thread(target=run)
    listening_thread.start()
    while  flag_program==True:
        print("1.Close server\n2.Restart server\n3.Stop update bases\n4.")
        variant = input()
        if  variant=="1":
            lock.acquire()
            flag_program = False;
            flag_base = False;
            httpd.shutdown()
            cnx.close()
            safe_last_fids("lastfids.txt", last_fids)
            lock.release()
            sys.exit()









