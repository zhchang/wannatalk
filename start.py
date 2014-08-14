from flask import (
	Flask,
	request,
)
from pygeocoder import Geocoder
import redis
import json


r = redis.StrictRedis(host='localhost', port=6379, db=0)

app = Flask(__name__)
app.debug = True


def get_location_by_latlng(lat, lng):
	result = Geocoder.reverse_geocode(float(lat), float(lng))
	locations = map(lambda x: x.replace(" ", ""), 
		result.formatted_address.split(","))
	return locations[::-1]


@app.route("/push", methods=['POST', 'GET'])
def post():
	if request.method == "POST":
		lat = request.form['lat']
		lng = request.form['lng']
		msg = request.form['msg']
	else:
		lat = request.args.get('lat', '')
		lng = request.args.get('lng', '')
		msg = request.args.get('msg', '')

	locations = get_location_by_latlng(lat, lng)
	r.lpush(":".join(locations), msg)
	return "KEY-----%s<br> MSG-----%s" % (":".join(locations), msg)


@app.route("/pull", methods=['GET'])
def get():
	lat = request.args.get('lat', '')
	lng = request.args.get('lng', '')

	locations = get_location_by_latlng(lat, lng)
	messages = r.lrange(":".join(locations), 0, -1)
	return json.dumps(messages)

@app.route("/")
def hello():
    return "Hello World!"


if __name__ == "__main__":
    app.run()