import json
import openai
import os

try:
    if os.environ['OPENAI_API_KEY']:
        print(os.environ['OPENAI_API_KEY'])
except KeyError:
    print('variable is not set.')
    from pathlib import Path
    from dotenv import load_dotenv
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

openai.api_key = os.environ['OPENAI_API_KEY']

import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders

# open json file UCLA_JSON_NAME.json
with open('JSON_NAME.json') as json_file:
    data = json.load(json_file)
    for p in data[3:4]:
        print('Subject: ' + p['Subject'])
        print('Sender: ' + p['Sender'])
        print('Date: ' + p['Date'])
        print('Snippet: ' + p['Snippet'])
        print('Message_body: ' + p['Message_body'])
        print('')
        
        # OpenAI API
        prompt = "Write a resume that would be perfect for the following job position. Format it in raw markdown.\n\n" + p['Message_body']
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                ]
        )
        print(response['choices'][0]['message']['content'])
        
        # save resume as markdown file
        filename = p['Subject'] + '.md'
        # clean filename for filename
        filename = filename.replace('/', '').replace('|', '')
        with open('./dist/' + filename, 'w') as f:
            f.write(response['choices'][0]['message']['content'])
        
        # OpenAI API
        prompt = "Write a cover letter as an applicant wishing employment for the following job position. Format it in raw markdown.\n\n ### \nJob Position Email:\n\n" + p['Message_body']
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                ]
        )
        print(response['choices'][0]['message']['content'])
        
        # save resume as markdown file
        filename = p['Subject'] + ' - cover letter.md'
        # clean filename for filename
        filename = filename.replace('/', '').replace('|', '')
        with open('./dist/' + filename, 'w') as f:
            f.write(response['choices'][0]['message']['content'])
            
        
        SCOPES = [
        "https://www.googleapis.com/auth/gmail.send"
        ]
        flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)

        service = build('gmail', 'v1', credentials=creds)
     
        # message = MIMEText('This is the body of the email\n\nJob Description: \n\nTESTING')
        
        cover_letter_filename = p['Subject'] + ' - cover letter.md'
        # clean filename for filename
        cover_letter_filename = cover_letter_filename.replace('/', '').replace('|', '')
        cover_letter_path = os.path.join('./dist/', cover_letter_filename)
        cover_letter_file = open(cover_letter_path, 'rb')
        cover_letter_content = cover_letter_file.read()
        cover_letter_file.close()
        # instance of MIMEMultipart 
        message = MIMEMultipart() 
        # message = MIMEText(cover_letter_content)
        
        # attach the body with the msg instance 
        message.attach(MIMEText(cover_letter_content.decode('utf-8'))) 
        
        message['to'] = 'paglipayucla@gmail.com'
        # message['from'] = 'paglipay@gmail.com'
        message['subject'] = 'Reply for Subject: ' + p['Subject']
        # create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        
        # attach resume
        resume_filename = p['Subject'] + '.md'
        # clean filename for filename
        resume_filename = resume_filename.replace('/', '').replace('|', '')
        # `resume_path` is a variable that stores the file path of the resume file. It is used to
        # specify the location of the resume file that will be attached to the email.
        resume_path = os.path.join('./dist/', resume_filename)
        resume_file = open(resume_path, 'rb')
        resume_content = resume_file.read()
        resume_file.close()
        
        print(resume_content)
        # resume_attachment = MIMEText(str(resume_content))
        # resume_attachment.add_header('Content-Disposition', 'attachment', filename=resume_filename)
        
        # message.attach(resume_attachment)
        
        # with open(resume_path, "rb") as attachment:
            # Add the attachment to the message
        part = MIMEBase("application", "octet-stream")
        part.set_payload(resume_content)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= '" + resume_filename + "'",
        )
        message.attach(part)
        
        
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        
        try:
            message = (service.users().messages().send(userId="me", body=create_message).execute())
            print(F'sent message to {message} Message Id: {message["id"]}')
        except HTTPError as error:
            print(F'An error occurred: {error}')
            message = None
            