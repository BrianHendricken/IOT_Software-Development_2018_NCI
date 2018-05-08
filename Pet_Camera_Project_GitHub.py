# Author : Brian hendricken
# Student Number: x17125561
# Email : x17125561@student.ncirl.ie
# May 2018 : IOT Software development Project:
# Project Title: Raspberry Pi Pet Camera :

""" This python file is a project for an IOT Pet Camera !
    Using a PIR sensor to detect motion of a pet which activates the Pi Camera to take an image.
    The time and date of the PIR sensor activation is written to a textfile called pet_cam_log.txt
    The camera image is stored as a .jpg image
    The Rsperberry Pi / Python code then pings my other PC using it IP address
    The PI then Receives a response from my PC
    If my PC responds with a zero result i.e. itmis online within a time then :
        The image is emailed as an attachment to my personal gmail account
        The logfile is also attached to the email
        The LED comes on for 5 seconds and then goes off for 20 seconds to add a time delay to prevent multiple emails being sent in short space of time
"""
# import libraries required for this project
import os # used for ping request to check if my PC is online and if so send pet cam image and tect file to remote gmail account
import time # import time
import sys # import sys
import grovepi # import library for grove pi sensor board
from picamera import PiCamera #import camera library
from time import sleep # import for time sleep / delays 
from time import strftime # for string time
import datetime 

# Libraries below for email to send log files via email
import smtplib # Smtp - form email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage # for emailing images

# Define Receiver and Sender email addresses
fromAddress = "PaulOB19999@gmail.com" # send emails from this email address setup for testing purposes
toAddress = "bhendricken@gmail.com"   # receive email to my gmail account

emailMessage = MIMEMultipart() # message, emailMessage will be a MIMEMultipart message
emailMessage['From'] = fromAddress # email address of my Sender email ( Gmail )
emailMessage['To'] = toAddress # email address of my Receiver email ( Gmail_BH )

# log/text file to send via email / network from rasperberry pi
logfile ="/home/pi/pet_cam_log.txt" # specifies the logfile from my Pi cam/PIR device - will store activation times and dates
LogAttachment = open(logfile, 'rb')  # Open File name "logfile"
events = MIMEBase('application', 'octet-stream') # an instance of MIMEBase and named as events , octet-stream is default according to:  https://docs.python.org/3/library/email.mime.html#email.mime.application.MIMEApplication
events.set_payload((LogAttachment).read()) # change into encoded form, "set_payload() to change the payload to encoded form" as described at:  https://docs.python.org/2/library/email.mime.html
events.add_header('Content-Disposition', "attachment; filename= %s" % logfile)
emailMessage.attach(events) # attach instance events i.e. logfile to the  emailMessage

emailMessage['Subject'] = "Pet Cam Activation ALERT - Photo & log attached" # subject of email message
emailBody = "Your Pet Cam Has Been Activated !" # string to store the body of the email
emailMessage.attach(MIMEText(emailBody, 'plain')) # attach the body with the emailMessageinstance
emailMessage.add_header("Pet Cam Image activation ALERT",emailBody)


today = datetime.datetime.now().strftime( "at: " '%H %M on date: %d %m %y') # for sensor log to return the time ( hour and minute ) and dat , month and year of sensor activation
#text_file=open("pet_cam_log.txt","a+") # append the pet cam log for sensor actications
text_file=open("/home/pi/pet_cam_log.txt","a+")


# Camera settings and rotate image 90 degrees to show correct orientation
camera = PiCamera()
camera.rotation = 90

# Define Grove INPUTS , OUTPUTS and connection ports
pir_sensor = 8 # PIR sensor on port D8 on Grove board
grovepi.pinMode(pir_sensor,"INPUT") # sets PIR sensor as an input device

led = 3 # LED connected to port D3 of Grove
grovepi.pinMode(led,"OUTPUT") #sets up LED as an output device

# Main While Loop
while True:    
    try:
        if grovepi.digitalRead(pir_sensor): # if PIR Senses motion of my dog or human in range of PIR sensor then do the following:
                camera.start_preview() # Start the camera preview 
                print("Motion Detected  - Pi Camera is now activating !!!") # indicator to user that camera is activating
                sleep(1) # Sleep or delay for 1 second until next action
                #camera.image_effect = 'watercolor'  # nice watercolour effect used for this project to test photo processing but not used for final project usage
                camera.annotate_text = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') # Adds timestamp overlay to image - modified this line of code from PiCamera Docs : https://picamera.readthedocs.io/en/release-1.10/recipes1.html
                camera.capture('/home/pi/Desktop/petcam_photo.jpg' ) # location of folder and filename for captured camera photo
                camera.stop_preview() # Stop the camera preview
                
                with open("/home/pi/pet_cam_log.txt","a") as text_file:     # here the a is used to append the log file ( brian h )
                    text_file.write("\n Pet_Camera-Activation {0}".format(today)) # here logfile is written to with time and date info for PIR sensor activation in this format: at: " '%H %M on date: %d %m %y
                sleep(0.5) # Sleep for 0.5 second before next action
                text_file.close() #pet_cam_log.close()
                
                hostname = "192.168.1.6" # IP address of my personal PC
                # RECEIVE feature of my device - Raspberry Pi pings another PC and oif it is online it will send camera image and textfile
                response = os.system("ping -c 1 -w2 " + hostname + " > /dev/null 2>&1") # send  packet within the deadline of 2 seconds & direct all output to /dev/null, retrieve just the return value , modified this line & next line of code from this address: https://stackoverflow.com/questions/2953462/pinging-servers-in-python
                if response == 0: # checks if pinged response is zero or active/online
                    print (hostname, 'is up! - Sending pet cam image and log file to external gmail account')
                    
                    
                    #camera photo capture file to send via email / network
                    jpgFile = "/home/pi/Desktop/petcam_photo.jpg" #image capture directory on Pi of Camera Images
                    fileOpen = open(jpgFile, 'rb')  # Open .jpg image file called name "jpgFile"
                    petCamPhoto = MIMEImage(fileOpen.read())  # Read the image file.
                    fileOpen.close()  # close the file.
                    
                    #Send Email and creates SMTP session
                    emailMessage.attach(petCamPhoto) # Attach the petcamPhoto image file to the email message
                    sendEmail = smtplib.SMTP('smtp.gmail.com', 587) # creates SMTP gmail session using protocol 587
                    sendEmail.starttls() # start TLS or transport Level Security for network socket security
                    sendEmail.login(fromAddress, "xxxxxx") # Authentication email address and password
                    message = emailMessage.as_string() # Converts the Multipart msg into a string
                    sendEmail.sendmail(fromAddress, toAddress, message) # sending the mail if my other PC is powered up and online
                    sendEmail.quit() # terminating the email session
                    
                    # Green LED now comes ON for 5 seconds and then OFF for 20 seconds
                    grovepi.digitalWrite(led,1) # after message has been sent the Green LED on port 3 comes on for 5 seconds
                    print ("LED_ON for 5 seconds!")
                    time.sleep(5)
                    grovepi.digitalWrite(led,0) # After 5 seconds LED goes off for 10 seconds and system resumes
                    print ("LED_OFF for 20 seconds!")
                    time.sleep(20) # added delay to prevent multiple photo captures from one or similar PIR sensor event
                else:
                    print (hostname, 'PC is down ! Saved image to Pi memory but not emailing image or log')

                     
        else:
            print ("<<-+++->>") # some characters to display to show sensor is active and sensing
            print ("---<+>---") # some more characters to display to show sensor is active and sensing

        # if your hold time is less than this, you might not see as many detections - from camera manual
        time.sleep(.2)

    except KeyboardInterrupt:
        print("Program has been interuppted !")
        sys.exit(0)

    except IOError:
        print ("Error !!")