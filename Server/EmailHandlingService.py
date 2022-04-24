import socket
from datetime import datetime
import threading
from PIL import Image, ImageFont, ImageDraw
import time
import os
import smtplib
from email.message import EmailMessage
IP = 'Enter WLAN IPv4 Address'
emailid = 'Enter centralised from email, requires less secure app access'
password = '[REDACTED FOR OBVIOUS REASONS]'
SetTime = '00:00:01'#For scheduling
#print(socket.gethostbyname('Alive'))
def timecheck():#Checks for current time in background
    print('timecheck() started')
    while True:
        if datetime.now().strftime('%H:%M:%S') == SetTime:
            sendmail()

def sendmail():
    #count = 1
    f = open('Details.txt','r')
    DetailsList = f.read().split('\n')#Reads empty string at last as well
    DetailsList.pop()#Last item is empty string so popping it
    #print(DetailsList)
    for i in DetailsList:

        Date,From,To,ToEmail,Template,Font = i.split('$')
        #print(f'Scanned item {count}:\nDate:{Date}\nFrom:{From}\nTo:{To}\nToEmail:{ToEmail}\nTemplate:{Template}\n\n')
        #count+=1
        CurDT = datetime.now().strftime('%Y-%m-%d')
        if Date == CurDT:
            TheCard = customBirthdayCard(From,To,Template,Font)
            print('Card Created')
            emailHandler(emailid,userpassword,ToEmail,TheCard,To)
            os.remove(TheCard)#Deleteing the card once sent
        else:
            print('TODAY IS NOT THE DAY!\n\n')
    time.sleep(1)#This function executes in less than a second causing Details file to be scanned multiple times

def emailHandler(SendersAddress,SendersPass,RecieversAddress,TheCard,To):
    print('Email Service Start')
    msg = EmailMessage()
    msg['Subject'] = f'Happy Birthday Dear {To}'
    msg['From'] = SendersAddress
    msg['To'] = RecieversAddress
    msg.set_content('Image')

    with open(TheCard,'rb') as f:
        filedata = f.read()
    print('Card read')
    msg.add_attachment(filedata,maintype = 'image',subtype = 'jpeg', filename = f'To {To} with Love')
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        print('Connection made')
        smtp.login(SendersAddress,SendersPass)
        smtp.send_message(msg)
    print('Email Sent')

def customBirthdayCard(From,To,Template,Font):
    myimg = Image.open(Template)
    title_font = ImageFont.truetype(f'{Font}.ttf', 80)
    title_text = f'{From} wishes you a \n  very happy birthday.\n Have a very splendid year \n  {To}'

    imgedit = ImageDraw.Draw(myimg)
    imgedit.text((300,200), title_text, (0, 71, 171), font=title_font)
    myimg.save(f'HappyBirthdayto{To}.jpg')
    return f'HappyBirthdayto{To}.jpg'

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((IP,1337))
s.listen(5)
print('Server established')
DetailsString = ''
threading.Thread(target=timecheck).start()
while True:
    (clientsock,address) = s.accept()
    print('Connection Established')
    while True:
        DataRecieved = clientsock.recv(8)
        print(f'{DataRecieved}\n')
        if len(DataRecieved) <= 0:
            break
        DetailsString += DataRecieved.decode('utf-8')

    print(DetailsString)
    f = open('Details.txt','a')
    f.write(DetailsString+'\n')
    f.close()
    DetailsString = ''
    print('Data Recieved')
