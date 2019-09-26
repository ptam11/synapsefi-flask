from flask_bcrypt import Bcrypt
from app.mongo import mongo
from app.models.Client import Client
import requests
from json import dumps
bcrypt = Bcrypt()

BASE_URL, HEADERS, USER_IP, USER, CONTENT_TYPE = Client.BASE_URL, Client.HEADERS, Client.USER_IP, Client.USER, Client.CONTENT_TYPE


class User:
    def __init__(self, username):
        self.username = username
        # query db to instantiate if already created
        user_dict = self.get_from_db()
        self.syn_user_id = "" if user_dict == None else user_dict.get("syn_user_id", "")
        self.syn_oauth_key = "" if user_dict == None else user_dict.get("syn_oauth_key", "")
        self.syn_refresh_token = "" if user_dict == None else user_dict.get("syn_refresh_token", "")
        self.syn_base_doc_id = "" if user_dict == None else user_dict.get("syn_base_doc_id", "")
        self.accounts = list()
        self.transactions = list()

    def __repr__(self):
        return self.username

    def create_user_with_api(self, name, email, phone_number, password):
        """
            Creates new user on Synapse API and local db
            Returns if creation is successful 
        """
        user_data = dumps(self.format_new_user_data(name, email, phone_number))
        resp = requests.post(BASE_URL + "/users",
                                    headers=HEADERS, data=user_data).json()
        is_error = resp.get("error") != None
        if not is_error:
            self.syn_user_id, self.syn_refresh_token, self.syn_base_doc_id = resp["_id"], resp["refresh_token"], resp["documents"][0]["id"]
            self.insert_to_db(password)
        return not is_error
    
    def get_oauth_from_api(self):
        """
            Gets oauth key for user from Synapse API and updates class prop and local db
            Returns if call is successful 
        """
        data = dumps(self.format_oauth_data(self.syn_refresh_token))
        resp = requests.post(BASE_URL + f"/oauth/{self.syn_user_id}",
                                headers=HEADERS, data=data).json()
        is_error = resp.get("error") != None
        if not is_error:
            self.syn_oauth_key = resp["oauth_key"]
            self.update_to_db()
        return not is_error

    def insert_to_db(self, password):
        """inserts user to local db"""
        hashed_pw = self.get_hashed_password(password)
        mongo.db.syn_users.insert({"syn_user_id": self.syn_user_id, "syn_refresh_token": self.syn_refresh_token, "username": self.username, "password": hashed_pw, "syn_base_doc_id": self.syn_base_doc_id})
        return
    
    def update_to_db(self):
        """updates oauth and refresh token on local db"""
        mongo.db.syn_users.update_one({"username": self.username}, {
                                                "$set": {"syn_oauth_key": self.syn_oauth_key, "syn_refresh_token": self.syn_refresh_token}})

    def update_refresh_token_from_api(self):
        """
            Gets new refresh token for oauth key and updates class prop and local db
            Returns if call is successful 
        """
        url = BASE_URL + f'/users/{self.syn_user_id}'
        resp = requests.get(url, headers=HEADERS).json()
        is_error = resp.get("error") != None
        if not is_error:
            self.syn_refresh_token = resp["refresh_token"]
            self.update_to_db()
        return not is_error
    
    def get_from_db(self):
        """ 
            Gets user dict from local db 
            Returns user dict 
        """
        user_dict = mongo.db.syn_users.find_one({"username": self.username})
        return user_dict

    def get_from_api(self):
        """
            Gets entire user object from Synapse API 
            returns user dict 
        """
        url = BASE_URL + f'/users/{self.syn_user_id}'
        user_dict = requests.get(url, headers=HEADERS).json()
        return user_dict

    def get_accounts_from_api(self):
        """
            Gets user accounts from Synapse API and updates class prop
            returns if call is successful 
        """
        url = BASE_URL + f'/users/{self.syn_user_id}/nodes'
        oauth_header = self.format_oauth_header(USER_IP, USER, CONTENT_TYPE, self.syn_oauth_key )
        resp = requests.get(url, headers=oauth_header).json()
        is_error = resp.get("error") != None
        if not is_error:
            self.accounts = resp["nodes"]
        return not is_error
    
    def create_account_from_api(self, data):
        """
            creates user accounts with Synapse API
            returns if creation is successful 
        """
        url = BASE_URL + f'/users/{self.syn_user_id}/nodes'
        oauth_header = self.format_oauth_header(USER_IP, USER, CONTENT_TYPE, self.syn_oauth_key )
        data["info"]["document_id"] = self.syn_base_doc_id
        resp = requests.post(url, headers=oauth_header, data=dumps(data)).json()
        is_error = resp.get("error") != None
        return not is_error

    def create_transaction_from_api(self, data, from_account_ind):
        """
            creates user transaction between 2 accounts with Synapse API
            returns if creation is successful 
        """
        from_account = self.accounts[from_account_ind]
        url = BASE_URL + f'/users/{self.syn_user_id}/nodes/{from_account["_id"]}/trans'
        oauth_header = self.format_oauth_header(USER_IP, USER, CONTENT_TYPE, self.syn_oauth_key)
        resp = requests.post(url, headers=oauth_header, data=dumps(data)).json()
        is_error = resp.get("error") != None
        return not is_error
    
    def get_transactions_from_api(self):
        """
            Gets user transactions from Synapse API and updates class prop
            returns if call is successful 
        """
        url = BASE_URL + f'/users/{self.syn_user_id}/trans'
        oauth_header = self.format_oauth_header(USER_IP, USER, CONTENT_TYPE, self.syn_oauth_key )
        resp = requests.get(url, headers=oauth_header).json()
        is_error = resp.get("error") != None
        if not is_error:
            self.transactions = resp["trans"]
        return not is_error


    @staticmethod
    def is_duplicate_username(username):
        """return if username is existing in local db"""
        user_dict = mongo.db.syn_users.find_one({"username": username})
        return user_dict != None

    @staticmethod
    def format_new_user_data(name, email, phone_number):
        """ format data for create user end point for SynapseFi API """
        data = {
            "logins": [
                {
                    "email": email
                }
            ],
            "phone_numbers": [
                phone_number
            ],
            "legal_names": [
                name
            ],
            "documents": [
                {
                    "email": email,
                    "phone_number": phone_number,
                    "ip": "::1",
                    "name": name,
                    "alias": "",
                    "entity_type": "LLC",
                    "entity_scope": "Arts & Entertainment",
                    "day": 2,
                    "month": 5,
                    "year": 1989,
                    "address_street": "1 Market St.",
                    "address_city": "SF",
                    "address_subdivision": "CA",
                    "address_postal_code": "94105",
                    "address_country_code": "US",
                    "virtual_docs": [],
                    "physical_docs": [],
                    "social_docs": []
                }
            ],
            "extra": {
                "supp_id": "122eddfgbeafrfvbbb",
                "cip_tag": 1,
                "is_business": True
            }
        }
        return data

    @staticmethod
    def format_oauth_data(refresh_token):
        """ format data for get oauth endpoint for SynapseFi API """
        data = {
            "refresh_token": refresh_token,
            "scope": [
                "USER|PATCH",
                "USER|GET",
                "NODES|POST",
                "NODES|GET",
                "NODE|GET",
                "NODE|PATCH",
                "NODE|DELETE",
                "TRANS|POST",
                "TRANS|GET",
                "TRAN|GET",
                "TRAN|PATCH",
                "TRAN|DELETE",
                "SUBNETS|GET",
                "SUBNETS|POST",
                "SUBNET|GET",
                "SUBNET|PATCH",
                "STATEMENTS|GET",
                "STATEMENT|GET"
            ]
        }
        return data

    @staticmethod
    def format_oauth_header(header_ip, header_user, header_type, syn_oauth_key):
        """ format header to include oauth token for user endpoints for SynapseFi API """
        header = {
            "X-SP-USER-IP": header_ip,
            "X-SP-USER": syn_oauth_key + header_user,
            "Content-type": header_type
        }
        return header

    @staticmethod
    def get_hashed_password(password):
        """return encrypted password"""
        return bcrypt.generate_password_hash(password).decode('UTF-8')
    
    @staticmethod
    def is_authenticated(username, password):
        """return if password is the same as hashed password from local db"""
        user_dict = User.get_from_db(username)
        if user_dict != None:
            hashed_pw = user_dict.get("password")
            return bcrypt.check_password_hash(hashed_pw, password)
        else:
            return False

