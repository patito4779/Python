# This code reads the contents of my mailbox and gets the SUbject and the from line and then prints it out to a folder path automatically created with the email subject name.
import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import sys

# account credentials
#username = "" # Take out the email address and put in an external file.
#password = ""    # Take out your password from here 
username = sys.argv[1] 
password = sys.argv[2]

def clean(text):
    # This is a text for creating a folder naem
    new = ""
    for c in text:
        if c.isalnum():
            new += c
        else:
            new += "_"
    return new
# line 15 - 23 above is same as line 25 - 26 below
# def clean(text):
#     return "".join(c if c.isalnum() else "_" for c in text)

""" Create an IMAP4 class with SSL using the imaplib"""
imap = imaplib.IMAP4_SSL("imap.mail.yahoo.com")
# The line below will allow you to authenticate your credentials
imap.login(username, password)

print(imap.list()) # This prints out the list of folders in your mailbox.


# Now start grabbing of emails in the mailbox
status, messages = imap.select("Inbox")
N = 10   # This is the number of top emails to fetch from the Inbox or any folder selected.
messages = int(messages[0])

for i in range(messages, messages-N, -1):
    # fetching the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            print(msg.keys())
            
            # decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # if the output is a byte, decode to str
                subject = subject.decode(encoding)
            # decode email sender
            From, encoding = decode_header(msg.get("From"))[0]
            if isinstance(From, bytes):
                From = From.decode(encoding)
            print("Subject:", subject)
            print('From:', From)
            
            # if the email message is multipart
            if msg.is_multipart():
                
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        # get the body of the email
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        # print text/plain emails and skip attachments
                        print(body)
                    elif "attachment" in content_disposition:
                        # download attachment
                        filename = part.get_filename()
                        if filename:
                            folder_name = clean(subject)
                            if not os.path.isdir(folder_name):
                                # make a folder for this email (named after the subject)
                                os.mkdir(folder_name)
                            filepath = os.path.join(folder_name, filename)
                            # download attachment and save it
                            open(filepath, "wb").write(part.get_payload(decode=True))
                    else:
                        continue
                
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                
                # get the email body
                body = msg.get_payload(decode=True).decode()
                print(content_type)
                if content_type == "text/plain":
                    # print only text email parts
                    print(body)
            
            if content_type == "text/html":
                # if it's HTML, create a new HTML file and open it in browser
                folder_name = clean(subject)
                if not os.path.isdir(folder_name):
                    # make a folder for this email (named after the subject)
                    os.mkdir(folder_name)
                filename = "index.html"
                filepath = os.path.join(folder_name, filename)
                # write the file
                open(filepath, "w").write(body)
                # open in the default browser
                webbrowser.open(filepath)
            print("="*100)
# close the connection and logout
imap.close()
imap.logout()