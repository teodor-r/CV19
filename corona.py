import mysql.connector
import requests
import json
from mysql.connector import errorcode
import math

dict_requests_patterns ={}
last_fids = {}


current_disrict_in_base = []

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






read_json("geogovrb.txt", "lastfids.txt")
session = create_session()


sum = 0
#обновление базы2
resp2 = send_request(dict_requests_patterns["2"],session).json()
for data in resp2["features"]:
    #print(data)
    district_name = ""
    namename_list = data["attributes"]["name"].split()
    x, y = projected_coords_to_sphere(data['geometry']['x'], data['geometry']['y'])
    for part in namename_list[0:-5]:
        district_name+= part + " "
    amount_infected = int(namename_list[-1])
    data_for_base = (district_name, amount_infected, x, y)
    sum+= amount_infected
    print(data_for_base)
    if check(district_name) == True:
        print(data_for_base)
        #cursor.execute('UPDATE table2 SET amount = {} , x = {} , y = {} WHERE district = "{}"'.format(amount_infected,x,y,district_name.strip()))
    else:
        pass
        #cursor.execute(add_data_table2, data_for_base)
    #cnx.commit()

#обновление базы 4
resp4 = send_request(dict_requests_patterns["4"],session).json()
current_last_index = last_fids["table4"]
for data in resp4["features"][current_last_index:]:
    name_list = data["attributes"]["name"].split(" ")
    fid = data["attributes"]["OBJECTID"]
    data_for_base = ()
    date = "00:00:00";num = ""
    x, y = projected_coords_to_sphere(data['geometry']['x'], data['geometry']['y'])
    if  fid!=170 and fid !=131 and fid!=770:
        num = name_list[0]
        date = name_list[-1]
    elif fid == 170:
        num = name_list[0] +  name_list[1]+ name_list[2]
    elif fid == 131:
        num = name_list[0]
    else:
        num = name_list[0]
        date = name_list[-2]
    data_for_base = (date, num, x, y)
    print(data_for_base)
    last_fids["table4"]+=1
last_fids["table4"]-=1
safe_last_fids("lastfids.txt",last_fids)

print(sum)
# prinение базы 5




'''
  district_name = ""
  namename_list = data["attributes"]["name"].split()
  x = data["attributes"].get("Lon")
  y = data["attributes"].get("Lat")
  for part in namename_list[0:-3]:
    district_name+= part + " "
  amount_infected = int(namename_list[-2:-1][0])
  data_for_base = (district_name, amount_infected, x, y)
  print(data_for_base)
  if check(district_name) == True:
    #cursor.execute('UPDATE infected SET amount = {} , x = {} , y = {} WHERE district = "{}"'.format(amount_infected,x,y,district_name.strip()))
  else:
    #cursor.execute(add_data_table2, data_for_base)
  #cnx.commit()
'''
