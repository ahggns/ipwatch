#!/usr/bin/python
import logging, os, sys, time 
import ConfigParser
import requests
import smtplib
from email.Message import Message

CONFIG_FILE="./ipwatch.ini"

def readConfig():
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def sendMail(config, value):
    notify_email = config.get("notify","email")
    
    smtp_host = config.get("smtp","host")
    smtp_port = config.get("smtp","port")
    smtp_user = config.get("smtp","user")
    smtp_pass = config.get("smtp","pass")

    hostname = os.uname()[1]

    m = Message()
    m['From'] = 'me'
    m['bcc'] = notify_email 
    m['Subject'] = 'IP Address for ' + hostname + ' is now ' + value

    server = smtplib.SMTP(smtp_host,smtp_port)
    server.starttls()
    server.login(smtp_user,smtp_pass)
    server.sendmail(smtp_user, notify_email, m.as_string())
    server.quit()

def doCheck(config):
    check_site = config.get("check","site")
    check_cache = config.get("check","cache")
    check_delay_s = config.getfloat("check","delay_seconds")
    
    if not os.path.isfile(check_cache):
        open(check_cache, 'w').close()

    with open (check_cache, "r") as f:
        latest_value=f.readline()

    while True:
	try:
		new_value=requests.get(check_site).text
		if not new_value == latest_value:
		    print "New value: " + new_value
		    sendMail(config, new_value)
		    with open (check_cache, 'w') as f:
			f.write(new_value)
			f.close()
		    latest_value = new_value
	except Exception as e:
		e = sys.exc_info()
		print("Error: {}".format(e))	
        time.sleep(check_delay_s)

def main():
    # set working directory to script path
    os.chdir(os.path.dirname(sys.argv[0]))

    config = readConfig()
    doCheck(config)

if __name__ == "__main__":
    main()
