import requests

class Aruba(object):


	def __init__(
			self,
			username:str='',
			password:str='',
			customer_id:str='',
			client_id:str='',
			client_secret:str='',
			access_token:str='',
			refresh_token:str='',
			base_url:str='',
			login_data:dict={},
			auth_code:str='',
			):
		self.username = username
		self.password = password
		self.customer_id = customer_id
		self.client_id = client_id
		self.client_secret = client_secret
		self.access_token = access_token
		self.refresh_token = refresh_token
		self.base_url = base_url
		self.login_data = login_data
		self.auth_code = login_data


	def _login(self):
		login_url = self.base_url + "/oauth2/authorize/central/api/login"
		params = {"client_id": self.client_id}
		creds = {
				"username" : self.username,
				"password": self.password
				}
		resp = requests.post(login_url, params=params, json=creds, timeout=10)
		if resp.json()["status"] == True:
			self.login_data = {
					"csrf": resp.cookies["csrftoken"],
					"ses": resp.cookies["session"]
					}
			return self.login_data,201
		else:
			return {"error": "Unauthorized"},401


	def _authorize(self):
		auth_url = self.base_url + "/oauth2/authorize/central/api"
		ses = "session=" + self.login_data["ses"]
		headers = {
			"X-CSRF-TOKEN": self.login_data["csrf"],
			"Content-type": "application/json",
			"Cookie": ses,
		}
		params = {
			"client_id": self.client_id,
			"response_type": "code",
			"scope": "all",
		}
		payload = {"customer_id": self.customer_id}
		resp = requests.post(auth_url, params=params, json=payload, headers=headers)
		self.auth_code = resp.json()["auth_code"]
		return {"auth_code": self.auth_code}


	def _tokens(self):
		token_url = self.base_url + "/oauth2/token"
		data = {
			"grant_type": "authorization_code",
			"code": str(self.auth_code)
		}
		resp = requests.post(
			url = token_url,
			data=data,
			auth=(self.client_id, self.client_secret)
		)
		self.refresh_token = resp.json()["refresh_token"]
		self.access_token = resp.json()["access_token"]
		return {"access_token": self.access_token}
				# "refresh_token": self.refresh_token}


	def _get_aps(self):
		url = "/monitoring/v1/aps"
		headers = {'Content-Type':'application/json', "Authorization": f"Bearer {self.access_token}"}
		resp = requests.get(url= self.base_url + url, headers=headers)
		return resp.json()


	def _get_bssids(self):
		url = "/monitoring/v1/bssids"
		headers = {'Content-Type':'application/json', "Authorization": f"Bearer {self.access_token}"}
		resp = requests.get(url= self.base_url + url, headers=headers)
		return resp.json()


	def _get_radius_config(self):
		url = "/platform/extauth_api/v1/config/radius"
		# headers = {'Accept': 'application/json','Content-Type':'application/json', "Authorization": f"Bearer {self.access_token}"}
		headers = {'Accept': 'application/json'}

		resp = requests.get(url= self.base_url + url, headers=headers)
		return resp.json()











