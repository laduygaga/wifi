#!/usr/bin/env python
# api_key = "50afdb8906f5b437142bdbf3decc04fce7556b5c"
# api_key2 = c0a53e8ef08f596285b085008175bf19e7f39235
import requests
from flask import Flask, request, jsonify, redirect
from flask_pymongo import PyMongo
from user import User
from router import Router
from config import Config
from unifi import Unifi
from meraki import Meraki
from unificontrol import UnifiClient
from aruba import Aruba
import urllib3

urllib3.disable_warnings()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hello'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/wifi'
base_url = 'https://api.meraki.com/api/v1'
mongo = PyMongo(app)

# colsList = ['users', 'user_organizations', 'organizations',
#		'router_organizations', 'routers', 'router_brands',
#		'router_configurations', 'configurations']

@app.route('/v1/users', methods=['GET', 'POST'])
def user_add():
	client = User(
			user_id = request.json.get('user_id')
			)._add()
	return jsonify(client[0]), client[-1]


@app.route('/v1/users/<int:user_id>', methods=['DELETE'])
def user_del(user_id):
	client = User(
			user_id = user_id
			)._del()
	return jsonify(client[0]), client[-1]


@app.route('/v1/users/<int:user_id>/routers', methods = ['POST']) # set router brand
def router_add(user_id):
	client = Router(
			user_id = user_id,
			brandname = request.json.get('brand_short_name')
			)._add()
	return jsonify(client[0]), client[-1]
	

@app.route('/v1/routers/<router_id>', methods=['DELETE'])
def router_del(router_id):
	client = Router(
			router_id = router_id
			)._del()
	return jsonify(client[0]), client[-1]
	

@app.route('/v1/users/<int:user_id>/routers', methods = ['GET'])
def router_list(user_id):
	client = Router(
			user_id = user_id
			)._list()
	return jsonify(client[0]), client[-1]


@app.route('/v1/meraki/organizations', methods = ['GET']) # list orgs
def list_orgs():
	client = Meraki(api_key = request.json.get('api_key'))
	data = client.list_orgs()
	return jsonify(data[0]),data[-1]


@app.route('/v1/meraki/networks', methods = ['GET']) # list netoworks
def list_networks():
	client = Meraki(
			api_key = request.json.get('api_key'),
			org_id = request.json.get('org_id')
			)
	data = client.list_networks()
	return jsonify(data[0]),data[-1]


@app.route('/v1/meraki/ssids')	# get ssid_data
def list_ssids():
	client = Meraki(
			api_key = request.json.get('api_key'),
			network_id = request.json.get('network_id')
			)
	data = client.list_ssids()
	return jsonify(data[0]),data[-1]


@app.route('/v1/meraki/limits', methods = ['GET'])
def get_limit():
	client = Meraki(
			api_key = request.json.get('api_key'),
			network_id = request.json.get('network_id'),
			ssid_number = request.json.get('ssid_number')
			)
	data = client.get_limit()
	return {'a':data}
	return jsonify(data[0]),data[-1]


@app.route('/v1/meraki/splash_timeout', methods = ['GET'])
def get_splash_timeout():
	client = Meraki(
			api_key = request.json.get('api_key'),
			network_id = request.json.get('network_id'),
			ssid_number = request.json.get('ssid_number')
			)
	data = client.get_splash_timeout()
	return jsonify(data[0]),data[-1]


@app.route('/v1/routers/<router_id>/configurations', methods = ['POST', 'PUT']) # set orgs
def config(router_id):
	client = Config(
			router_id = router_id,
			configuration_id = request.json.get('configuration_id'),
			value = request.json.get('value')
			)
	data = client.config()
	return jsonify(data[0]),data[-1]


@app.route('/v1/routers/<router_id>/api_key/del', methods= ['DELETE'])
def api_key_del(router_id):
	payload = None
	router_configurations_cols = mongo.db.router_configurations
	api_key = router_configurations_cols.find_one({"configuration_id":1,
		"router_id":router_id})['value']
	router_configurations_cols.delete_many({"configuration_id":1,
		"router_id": router_id})
	return jsonify({
			'msg': f"deleted api_key: {api_key}"
			}),204


@app.route('/v1/unifi/sites', methods=['GET']) # list site for unifi
def list_sites():
	client = Unifi(
			host = request.json.get('host'),
			port = request.json.get('port'),
			username = request.json.get('username'),
			password = request.json.get('password')
			)
	data = client._list()
	return jsonify(data[0]),data[-1]

def handle_splash_url(router_brandname=None, params=None):
	"""
	Get domain name
	Neu dang wifi.paas.vn thi return rong, 204
	Neu la dang router_id.wifi.paas.vn thi get splash url cua router_id.
	Xu ly cac log map lai query param tuy theo brand cua router da khai bao
	Redirect den splash url nay kem query param da map
	"""

	# Get HOST tu header
	domain = request.headers['Host']
	if domain == "wifi.paas.vn":
		return jsonify({}), 204
	# Get router id tu HOST
	# Bang cach split theo . lay phan tu 0
	router_id = domain.split('.')[0]

	# find router, account theo router id vua get

	# Neu khong tim thay thi return 404
	router = mongo.db.routers.find_one({"id":router_id})
	if router is None:
		return jsonify({"error": "Not Found"}) , 404

	# Neu tim duoc router, account
	# Get config router de lay splash url
	router_brand_id = int(router['router_brand_id'])

	if router_brand_id == 1: # Meraki
		router_config = mongo.db.router_configurations.find_one({"router_id":router_id, "configuration_id":5})
		if router_config:
			splash_url = router_config['value']
			host = request.host_url
			base_grant_url = request.args.get('base_grant_url')
			user_continue_url = request.args.get('user_continue_url')
			node_mac = request.args.get('node_mac')
			client_ip = request.args.get('client_ip')
			client_mac = request.args.get('client_mac')
			return redirect(f"{splash_url}?router_id={router_id}&base_grant_url={base_grant_url}&continue_url={user_continue_url}")
		else:
			return jsonify({"error": "Not Found splash_url"}) , 404

	if router_brand_id == 2: # Unifi
		router_config = mongo.db.router_configurations.find_one({"router_id":router_id, "configuration_id":5})
		if router_config:
			splash_url = router_config['value']
			device_mac = params.get('ap')
			client_mac = params.get('id')
			return redirect(f"{splash_url}?router_id={router_id}&client_mac={client_mac}")
		else:
			return jsonify({"error": "Not Found splash_url"}) , 404

	if router_brand_id == 3: # TP-link
		router_config = mongo.db.router_configurations.find_one({"router_id":router_id, "configuration_id":5})
		if router_config:
			splash_url = router_config['value']
			token = params.get('token')
			redir = params.get('redir')
			client_ip = params.get('ip')
			return redirect(f"{splash_url}?router_id={router_id}&token={token}&client_ip={client_ip}=&redir={redir}")
		else:
			return jsonify({"error": "Not Found splash_url"}) , 404
		
	if router_brand_id == 4: # Mikrotik
		router_config = mongo.db.router_configurations.find_one({"router_id":router_id, "configuration_id":5})
		if router_config:
			splash_url = router_config['value']
			login_url = params.get('login_url')
			username = params.get('username')
			password = params.get('password')
			return redirect(f"{splash_url}?router_id={router_id}&login_url={login_url}&username={username}&password={password}")
		else:
			return jsonify({"error": "Not Found splash_url"}) , 404

	if router_brand_id == 5: # Aruba
		router_config = mongo.db.router_configurations.find_one({"router_id":router_id, "configuration_id":5})
		if router_config:
			splash_url = router_config['value']
			login_url = params.get('login_url')
			username = params.get('username')
			password = params.get('password')
			return redirect(f"{splash_url}?router_id={router_id}&login_url={login_url}&username={username}&password={password}")
		else:
			return jsonify({"error": "Not Found splash_url"}) , 404

@app.route('/v1/auth/credentials', methods = ['POST'])
def get_auth():

	router_id = request.json.get('router_id')
	if router_id is None:
		return jsonify({"error": "Bad Auth"}), 400

	# Meraki
	base_grant_url = request.json.get('base_grant_url')
	user_continue_url = request.json.get('user_continue_url') if request.json.get('user_continue_url') else "https://google.com"
	if base_grant_url and user_continue_url:
		return jsonify({
			'login_url': f"{base_grant_url}?continue_url={user_continue_url}",
			'method': 'GET',
			'headers':"Content-Type: application/json",
			'payload':{}
			}), 201

	# Unifi
	client_mac = request.json.get('client_mac')
	if client_mac:
		controller = mongo.db.router_configurations.find_one({"router_id":router_id, "configuration_id":8},{"_id":0})
		username = controller["value"]["username"]
		password = controller["value"]["password"]
		host = controller["value"]["host"]
		port = int(controller["value"]["port"])
		login_url = f"https://{host}:{port}/api/login"
		headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
		json = {"username": username, "password": password}
		login  = requests.post(url=login_url, headers=headers, json=json, verify=False)
		cookies = {"unifises": dict(login.cookies)['unifises']}
		return jsonify({
			'login_url': f"https://{host}:{port}/api/s/default/cmd/stamgr",
			'method': 'GET',
			'headers':"Content-Type: application/json",
			'cookies': cookies,
			'payload':{
				"cmd":"authorize-guest",
				"mac":client_mac
				}
			}), 201


	# TP-link
	token = request.json.get('token')
	redir = request.json.get('redir') if request.json.get('redir') else "https://google.com"
	client_ip = request.json.get('client_ip') if request.json.get('client_ip') else "192.168.1.1"
	host = '.'.join(client_ip.split('.')[:-1]) + '.1'
	port = 2050
	if token:
		return jsonify({
			'login_url': f"http://{host}:{port}/nodogsplash_auth/?tok={token}&redir={redir}",
			'method': 'GET',
			'headers':"Content-Type: application/json",
			'payload':{}
			}), 201

	# Mikrotik
	login_url = request.json.get('login_url')
	username = request.json.get('username')
	password = request.json.get('password')
	if login_url and username and password:
		return jsonify({
			'login_url': f"{login_url}",
			'method': 'POST',
			'headers':[
				"Content-Type: application/x-www-form-urlencoded",
				"Accept: text/html"
				],
			'payload':f"dst={redir}&popup=true&username={username}&password={password}"
			}), 201

	if not base_grant_url and not token and not login_url and not client_mac:
			return jsonify({"error": "Bad Auth"}), 400




@app.route('/', methods = ['GET'])
def root_splash():
	return handle_splash_url(params=request.args)

# @app.route('/guest/s/default/')
# def _f():
# 	domain = request.headers['Host']
# 	if domain == "wifi.paas.vn":
# 		return jsonify({}), 204
# 	router_id = domain.split('.')[0]
# 	router = mongo.db.routers.find_one({"id":router_id})
# 	if router is None:
# 		return jsonify({"error": "Not Found"}) , 404
# 
# 	router_brand_id = int(router['router_brand_id'])
# 
# 	if router_brand_id == 2: # Unifi
# 		router_config = mongo.db.router_configurations.find_one({"router_id":router_id, "configuration_id":5})
# 		splash_url = router_config['value']
# 		device_mac = params.get('ap')
# 		client_mac = params.get('id')
# 		return redirect(f"https://{splash_url}?client_mac={client_mac}&router_id={router_id}")

@app.route('/aruba/login', methods=['GET','POST'])
def aruba_login():
	client = Aruba(
			username="nnd58xe1@gmail.com",
			password="nnd020895@123",
			base_url="https://apigw-prod2.central.arubanetworks.com",
			client_id="6FOuG7aJZKU84QQB7IEtcfTXxkVCsQhH",
			client_secret="CZ353NtAfQ4hWjUpDBQMFwEk2lhgK0xP"
			)
	return client._login()


@app.route('/aruba/auth', methods=['GET','POST'])
def aruba_auth():
	client = Aruba(
			username="nnd58xe1@gmail.com",
			password="nnd020895@123",
			base_url="https://apigw-prod2.central.arubanetworks.com",
			client_id="6FOuG7aJZKU84QQB7IEtcfTXxkVCsQhH",
			client_secret="CZ353NtAfQ4hWjUpDBQMFwEk2lhgK0xP"
			)
	login_data = client._login()
	return {"auth_code": client._authorize()}


@app.route('/aruba/token', methods = ['GET', 'POST'])
def get_token():
	client = Aruba(
			username="nnd58xe1@gmail.com",
			password="nnd020895@123",
			base_url="https://apigw-prod2.central.arubanetworks.com",
			client_id="6FOuG7aJZKU84QQB7IEtcfTXxkVCsQhH",
			client_secret="CZ353NtAfQ4hWjUpDBQMFwEk2lhgK0xP"
			)
	login_data = client._login()
	auth_code = client._authorize()
	return {'access_token':client._tokens()}

@app.route('/aruba/get_aps')
def get_aps():
	token_data = get_token()['access_token']
	access_token = token_data['access_token']
	client = Aruba(
			username="nnd58xe1@gmail.com",
			password="nnd020895@123",
			base_url="https://apigw-prod2.central.arubanetworks.com",
			client_id="6FOuG7aJZKU84QQB7IEtcfTXxkVCsQhH",
			client_secret="CZ353NtAfQ4hWjUpDBQMFwEk2lhgK0xP",
			access_token=access_token)

	return client._get_ap()


@app.route('/aruba/get_bssids')
def get_bssids():
	token_data = get_token()['access_token']
	access_token = token_data['access_token']
	client = Aruba(
			username="nnd58xe1@gmail.com",
			password="nnd020895@123",
			base_url="https://apigw-prod2.central.arubanetworks.com",
			client_id="6FOuG7aJZKU84QQB7IEtcfTXxkVCsQhH",
			client_secret="CZ353NtAfQ4hWjUpDBQMFwEk2lhgK0xP",
			access_token=access_token)

	return client._get_bssids()


@app.route('/aruba/get_radius_config')
def get_radius_config():
	token_data = get_token()['access_token']
	access_token = token_data['access_token']
	client = Aruba(
			username="nnd58xe1@gmail.com",
			password="nnd020895@123",
			base_url="https://apigw-prod2.central.arubanetworks.com",
			client_id="6FOuG7aJZKU84QQB7IEtcfTXxkVCsQhH",
			client_secret="CZ353NtAfQ4hWjUpDBQMFwEk2lhgK0xP",
			access_token=access_token)

	return client._get_radius_config()


if __name__ == '__main__':
	mongo.init_app(app)
	app.run(debug=True, host='0.0.0.0', port=5002)
