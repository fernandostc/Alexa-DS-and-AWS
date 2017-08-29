#Flask-ask Imports
import os
import logging
import subprocess
from subprocess import call
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

#DSP3 Imports
import requests
import urllib3
from requests.packages import urllib3
urllib3.disable_warnings()
from urllib.request import urlopen
from sys import argv
from dsp3.models import manager

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)

@ask.intent("AnswerAction")
def action_to_do(action):
	ask_msg = render_template('ask')

	if action == "create an instance":
		return question("Which instance type do you want to create?")

	elif action == "check last antimalware event host id":
		hostid = get_antimalwareevent_hostid()
		return question("The last Antimalware event from Deep Security was with the instance %s. %s" %(hostid, ask_msg) )

	elif action == "check last antimalware event host name":
		hostid_AM = get_antimalwareevent_hostid()
		hostname_AM = get_antimalware_hostname(hostid_AM)
		return question("The last Antimalware event from Deep Security was with the instance %s. %s" %(hostname_AM, ask_msg) )

	elif action =="change security profile of an instance affected with malware":
		affectedhostid = change_securityprofile_for_instance_affected_with_malware()
		return question("The security profile will be changed on Host ID %d. %s" %(affectedhostid, ask_msg))

	elif action =="create demo environment":
		create_demo_environment()
		return question("The demo environment is being created. %s" % ask_msg)

	elif action =="delete demo environment":
		delete_demo_environment()
		return question("The demo environment is being deleted. %s" % ask_msg)

	elif action =="about":
		return question("I'm Sec in Cloud. I'm the voice command system to help you to create any AWS workloads with Deep Security or check your security level in the cloud. Deep Security will be able to protect all your Journey to the Cloud. %s" % ask_msg)

	elif action == "nothing":
		return statement("Thank you very much to use Sec in Cloud. Have a good one!")

	elif action == "set docker environment in prevent mode":
		change_securityprofile_for_dockerenv()
		return question("The docker environment was changed to prevent mode. %s" % ask_msg)

@ask.intent("AnswerTypeInstance")
def type_instance(typeinstance):
	ask_msg = render_template('ask')
	return question("I will create an instace type of %s. %s" %(typeinstance, ask_msg))


def get_antimalwareevent_hostid():
    #Add Deep Security credentials to login in and run the web APIs commands
    dsm = manager.Manager(tenant="",username="", password="")
	response = dsm.antimalware_event_retreive(time_type="LAST_24_HOURS")
	events = response.antiMalwareEvents[0]
	hostid = events[-1]['hostID']
	dsm.end_session()
	return hostid

def get_antimalware_hostname(id):
    #Add Deep Security credentials to login in and run the web APIs commands
    dsm = manager.Manager(tenant="",username="", password="")
	hostinfo = dsm.host_detail_retrieve(host_id=id)
	name = hostinfo['displayName']
	dsm.end_session()
	return name

def change_securityprofile_for_instance_affected_with_malware():
	#Add Deep Security credentials to login in and run the web APIs commands
    dsm = manager.Manager(tenant="",username="", password="")
	hostid = get_antimalwareevent_hostid()
	#Add the profile ID for the security profile that you will need
	dsm.security_profile_assign_to_host(5721,hostid)
	dsm.end_session()
	return hostid

def create_demo_environment():
    #CloudFormation Stack Name
	stack = 'SecDashCloud'
    #Add the JSON file location with CloudFormation
	subprocess.run(['aws', 'cloudformation', 'create-stack', '--stack-name', stack, '--template-body', 'file://./SecDashCloud.json', '--tags', 'Key=Name,Value=SecDashCloudAlexa'])

def delete_demo_environment():
	stack = 'SecDashCloud'
	print (stack)
	subprocess.run(['aws', 'cloudformation', 'delete-stack', '--stack-name', stack])

def change_securityprofile_for_dockerenv():
    #Add Deep Security credentials to login in and run the web APIs commands
    dsm = manager.Manager(tenant="",username="", password="")
    #Add policyid and hostid
	dsm.security_profile_assign_to_host(policyid,hostid)
	dsm.end_session()

if __name__ == '__main__':
    app.run(debug=True)
