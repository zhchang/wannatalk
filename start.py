from flask import (
	Flask,
	request,
)
from pygeocoder import Geocoder
import redis
import json
import time


r = redis.StrictRedis(host='localhost', port=6379, db=0)

app = Flask(__name__)
app.debug = True


def get_location_by_latlng(lat, lng):
        try:
            result = Geocoder.reverse_geocode(float(lat), float(lng))
            locations = map(lambda x: x.replace(" ", ""), 
                    result.formatted_address.split(","))
            return locations[::-1]
        except:
            return None

@app.route("/request", methods=['GET'])
def get():
        ts = str(time.time())
        lat = request.args.get('lat', '')
        lng = request.args.get('lng', '')
        msg = request.args.get('msg', '')
        lvl = request.args.get('lvl', '0')
        lst = request.args.get('lst', '')
        if len(lst) == 0:
            return '{}'

	locations = get_location_by_latlng(lat, lng)

        if locations is None:
            return '{}'
        if len(msg)>0:
            for i in range(0,len(locations)):
                keys = ":".join(locations[:len(locations)-i])
                print keys
                r.lpush(keys, ts)
                r.lpush(keys, msg)
        level = 0
        try:
            level = int(lvl)
        except:
            pass
        keys = ":".join(locations[0:len(locations)-level])
        
        messages = r.lrange(keys, 0, -1)
        messages = [messages[x-1] for x in range(0,len(messages))[1::2] if messages[x] > lst ]
        result = {}
        result['lst']=ts
        result['msgs'] = messages
        return json.dumps(result)

@app.route("/")
def hello():
    return "Hello World!"


if __name__ == "__main__":
    app.run()
