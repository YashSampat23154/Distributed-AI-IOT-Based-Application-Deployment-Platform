from ldap3 import Server, Connection, ALL_ATTRIBUTES, ALL, MODIFY_ADD,SUBTREE
import json
import os
from flask import Flask, jsonify,request, make_response
from dotenv import load_dotenv
import requests
from flask_cors import CORS, cross_origin
import loggingMessage as log
import hashlib
load_dotenv()



app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/login',methods=['POST'])
@cross_origin()
def confirm_the_password():
    data = request.get_json()
    email = data["userID"]
    passWord = data["password"]
    groupName = data["role"]
    response, flag = ldap.check_password(email,passWord,groupName)
    if flag==False :
        return make_response(response, 500)
    else :
        return make_response(response, 200)   
    return response
    


@app.route('/register',methods=['POST'])
@cross_origin()
def make_registeration():
    data = request.get_json()
    email = data["userID"]
    firstName = data["firstname"]
    lastName = data["lastname"]
    passWord = data["password"]
    groupName = "AppDeveloper"
    response = ldap.add_entry(email,firstName,lastName,passWord,groupName)
    # print(response)
    return response









class LDAP_Server :
    def __init__(self,ip,port,admin,password,dc,salt):
        self.ip = ip
        self.port = port
        self.admin = admin
        self.password = password
        self.dc = dc
        self.salt = salt

    def set_the_connection(self):
        server = Server(self.ip, port=self.port)
        # print("Done")
        conn = Connection(server, user=f'cn={self.admin},{self.dc}', password=self.password, auto_bind=True)
        return conn
        # conn.unbind()


    def make_group(self,group_name,group_description):
        conn = self.set_the_connection()
        
        if self.is_group_already_exist(group_name) :
            # print("print group already exists")
            conn.unbind()
            return
            # return "print group already exists"

        members = [f'uid=captaincold,{self.dc}']
        group_dn = f'cn={group_name},{self.dc}'

        group_attrs = {
            'objectClass': ['groupOfUniqueNames'],
            'cn': group_name,
            'description': group_description,
            'uniqueMember': members,
        }

        check_group = conn.add(group_dn, ['groupOfUniqueNames'], group_attrs)

        if check_group:
            print(f"Group made.. '{group_dn}' has been added to the LDAP server.")
            log.log_message("ldap","DEBUG",f"Group made.. '{group_dn}' has been added to the LDAP server.")
        else:
            print(f"Failed to make group.. DN '{group_dn}' not added to the LDAP server.")
            log.log_message("ldap","DEBUG","Failed to make group.. DN '{group_dn}' not added to the LDAP server.")

        conn.unbind()
        return    


    def hash_the_password(self,password):
        dataBase_password = password+self.salt
        hashed = hashlib.md5(dataBase_password.encode())
        return hashed.hexdigest()  


    def add_entry(self,mail,firstName,lastName,password,groupName):
        conn = self.set_the_connection()
        cn = f'{mail}${groupName}'

        if self.is_entry_at_server(cn) :
            data =  {'status': '0', 'message': 'User ID already registered'}
            conn.unbind()
            # print("Already exists")
            return json.dumps(data).encode("utf-8")
        

        hasedPassword = self.hash_the_password(password)

        new_entry = {
            'objectClass': ['inetOrgPerson'],
            'cn': cn,
            'sn': lastName,
            'givenName': firstName,
            'mail': mail,
            'userPassword': hasedPassword
        }


        dn = f'cn={cn},{self.dc}'
        result = conn.add(dn, ['inetOrgPerson'], new_entry)
        
        if result:
            print(f"Entry with DN '{dn}' has been added to the LDAP server.")
            log.log_message("ldap","DEBUG",f"Entry with DN '{dn}' has been added to the LDAP server.")
            conn.unbind()
            self.add_entry_to_group(cn,groupName)
            data =  {'status': '1', 'message': 'Registered Successfully'}
            return json.dumps(data).encode("utf-8")


        else:
            print(f"Failed to add entry with DN '{dn}' to the LDAP server.")
            log.log_message("ldap","DEBUG",f"Failed to add entry with DN '{dn}' to the LDAP server.")
            conn.unbind()
            data =  {'status': '0', 'message': 'Unable to make account'}
            return json.dumps(data).encode("utf-8")


    def add_entry_to_group(self,mail,groupName):
        member_dn = f'uid={mail},{self.dc}'
        conn = self.set_the_connection()

        if self.search_for_entry_in_group(mail,groupName):
            # print("Entery alreay in group")
            conn.unbind()
            return
        group_dn = f'cn={groupName},{self.dc}'
        
        change = {
        'uniqueMember': [(MODIFY_ADD, [member_dn])]
        }

        conn.modify(group_dn, change)

        conn.search(group_dn, '(uniqueMember={})'.format(member_dn))

        if conn.entries:
            print(f'Member {member_dn} has been added to group {group_dn}')
            log.log_message("ldap","DEBUG",f'Member {member_dn} has been added to group {group_dn}')
            conn.unbind()
        else:
            print(f'Error: Member {member_dn} was not added to group {group_dn}')
            log.log_message("ldap","DEBUG",f'Error: Member {member_dn} was not added to group {group_dn}')
            conn.unbind()


    def search_for_entry_in_group(self,mail,groupname):
        conn = self.set_the_connection()


        member_dn = f'uid={mail},{self.dc}'
        search_filter = '(objectClass=groupOfUniqueNames)'
        group_dn = f'cn={groupname},{self.dc}'

        search_filter = f'(&(objectClass=groupOfUniqueNames)(cn={groupname})(uniqueMember={member_dn}))'
        conn.search(group_dn, search_filter, attributes=[ALL_ATTRIBUTES], search_scope=SUBTREE)

        # for entry in conn.entries:
        #     # print(f"DN: {entry.entry_dn}")
        #     print(entry)

        if len(conn.entries):
            conn.unbind()
            return True
            
        else:
            conn.unbind()
            return False


    def is_group_already_exist(self,groupName):
        conn = self.set_the_connection()
        search_filter = '(objectClass=groupOfUniqueNames)'
        group_dn = f'cn={groupName},{self.dc}'
        conn.search(group_dn, search_filter, attributes=[ALL_ATTRIBUTES], search_scope=SUBTREE)
        
        if len(conn.entries):
            conn.unbind()
            return True
        
        conn.unbind()
        return False

    def is_entry_at_server(self,cn):
        conn = self.set_the_connection()

        conn.search(self.dc, f'(cn={cn})', attributes=[ALL_ATTRIBUTES])


        # print(len(conn.entries))
        # for entry in conn.entries:
        #     print(entry)
        if len(conn.entries):
            conn.unbind()
            return True
        conn.unbind()
        return False

        # print(len(conn.entries))
        # for entry in conn.entries:
        #     print(entry)


    def list_all_members_in_grp(self,groupName):
        conn = self.set_the_connection()
        search_filter = '(objectClass=groupOfUniqueNames)'
        group_dn = f'cn={groupName},{self.dc}'
        conn.search(group_dn, search_filter, attributes=[ALL_ATTRIBUTES], search_scope=SUBTREE)
        # for entry in conn.entries:
        #     print(entry)

        conn.unbind()    


    def check_password(self,mail,entered_password,groupName):
        
        conn = self.set_the_connection()
        conn.search(self.dc, f'(cn={mail}${groupName})', attributes=[ALL_ATTRIBUTES])
        
        hash_of_entered_password = self.hash_the_password(entered_password)

        # print("Hashed password",hash_of_entered_password)

        for entry in conn.entries:
            # print("Here")
            # print(entry.entry_attributes_as_dict['userPassword'])
            # conn.unbind()

            if entry.entry_attributes_as_dict['userPassword'][0].decode('utf-8') == hash_of_entered_password :
                data =  {'status': '1', 'message': 'Password matched'}
                conn.unbind()
                return json.dumps(data).encode("utf-8"), True
            
            else :
                data =  {'status': '0', 'message': 'Invalid Credentials'}
                conn.unbind()
                return json.dumps(data).encode("utf-8"), False


        data =  {'status': '0', 'message': 'UserID not found.'}
        conn.unbind()
        return json.dumps(data).encode("utf-8"), False






if __name__ == '__main__':
    # print("Here")
    print("[+] LDAP SERVER Live")
    log.log_message("ldap","DEBUG","[+] LDAP SERVER Live")
    ldap = LDAP_Server('localhost',389,"admin","admin","dc=ias,dc=group5","$#123Aa")
    
    ldap.make_group("Admin","Admin's group")
    print("[+] Admin's ID created")
    log.log_message("ldap","DEBUG","[+] Admin's ID created")

    ldap.make_group("AppDeveloper","Developer's group")
    print("[+] App Developer group created")
    log.log_message("ldap","DEBUG","[+] App Developer group created")

    ldap.add_entry("admin@admin.com","Andrew","NG","admin","Admin")
    print("[+] Admin's ID created")
    log.log_message("ldap","DEBUG","[+] Admin's ID created")
    # app.run(host = os.getenv('SERVICE_IP'), port = os.getenv('SERVICE_PORT'), debug = True)
    # app.run(host = "192.168.1.200", port = 7424, debug = True)
    app.run(host = "0.0.0.0", port = 7424, debug = False)
