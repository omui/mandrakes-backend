import flask
from flask import request, jsonify, Flask, json
from elasticsearch import Elasticsearch, helpers
import string 
import random 
import time
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

app = flask.Flask(__name__)
app.config["DEBUG"] = True

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

es = Elasticsearch(['10.150.154.107:9200'])

def sendemail(from_addr, to_addr_list, cc_addr_list,subject, message, login, password,
              smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
    
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return 'Mail Sent'

@app.route('/create', methods = ['POST'])
def create():
    
    if request.headers['Content-Type'] == 'application/json':
        indata = request.json
    indata['id'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
    indata['creation_date'] = time.time() 
    indata['status'] = 0
    if 'content' not in indata:
        indata['data'] = json.dumps(indata['data'])
    else:
        indata['data'] = json.dumps(indata['content'])
    #if 'response' in indata:
    #    indata['response'] = json.dumps(indata['response'])
    #print(indata)
    action1 = [{"_index": "hackathon_ticket","_type": "_doc","_id": indata['id'],"doc": indata}] #for key,value in indata.items()]
    helpers.bulk(es, action1)
    ticket_id = indata['id']
    data = indata['data']
    receiver = ['c-himanshu.pachori@timesinternet.in', 'hariom.bangari@timesinternet.in']   #indata['uid']

    sendemail(from_addr    = 'bot.mandrake@gmail.com', 
                to_addr_list = receiver,
                cc_addr_list = ['hariom.bangari@timesinternet.in'], 
                subject      = 'Ticket Created.', 
                message      = f"A ticket with refrence number {ticket_id} has been created for the issue {data}",
                login        = 'bot.mandrake@gmail.com', 
                password     = 'Asd@56789')
      
    return ticket_id

@app.route('/statusUpdate', methods = ['POST'])
def statusUpdate():
    
    if request.headers['Content-Type'] == 'application/json':
        indata = request.json
    es.update(index= 'hackathon_ticket', id= indata['id'], _source= True,
                body= {"doc": {"doc": {"status": indata['status']}}})
    
    ticket_id = indata['id']
    receiver = ['c-himanshu.pachori@timesinternet.in']   #indata['uid']

    sendemail(from_addr    = 'bot.mandrake@gmail.com', 
                  to_addr_list = receiver,
                  cc_addr_list = ['hariom.bangari@timesinternet.in'], 
                  subject      = 'Ticket Created.', 
                  message      = f"The status of ticket with refrence number {ticket_id} has been changed",
                  login        = 'bot.mandrake@gmail.com', 
                  password     = 'Asd@56789')
        
    return 'Status Updated.'

@app.route('/response', methods = ['POST'])
def response():
    if request.headers['Content-Type'] == 'application/json':
        indata = request.json
    res = es.get(index="hackathon_ticket", id= indata['id'])
    res = res['_source']['doc']['response']
    res = str(res)+' '+json.dumps(indata) 
    es.update(index= 'hackathon_ticket', id= indata['id'], _source= True,
                body= {"doc": {"doc": {"response": res}}})
    
    ticket_id = indata['id']
    receiver = ['c-himanshu.pachori@timesinternet.in'] 
    
    sendemail(from_addr    = 'bot.mandrake@gmail.com', 
                  to_addr_list = receiver,
                  cc_addr_list = ['hariom.bangari@timesinternet.in'], 
                  subject      = 'Ticket Created.', 
                  message      = f"A ticket with refrence number {ticket_id} has been modified with the response {res}",
                  login        = 'bot.mandrake@gmail.com', 
                  password     = 'Asd@56789')
    
    return 'Response Sent.'

@app.route('/listId', methods = ['GET'])
def listId():
    #if request.headers['Content-Type'] == 'application/json':
    #    indata = request.json
    indata = es.search(index="hackathon_ticket")  #, id= indata['id'])
    y = indata['hits']['hits']
    z =[]
    for i in range(len(y)):
        z.append(y[i]['_source']['doc'])
    return jsonify(z)

if __name__ == '__main__':
    app.run(host='172.29.72.33',port='9001',debug=True)