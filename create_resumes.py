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

# preprompt for OpenAI API
pre_prompt = """Using my actual resume information

###
# Paul Aglipay

**Senior Network Engineer | CCNP R/S, CCNA Voice, Python**

Los Angeles, CA 90065

Email: paglipay@gmail.com

Phone: (323)610-6668

---

## Work Experience

### Network Engineer / Programmer Analyst III

**UCLA Campus Backbone** - Los Angeles, CA

*October 2016 to Present*

- Provide tier-3 operational support for Firewalls, Proxies, IDS/IPS, NAC to resolve critical business issues
- Independently own the Security Infrastructure support, solving complex issues and suggesting design modifications
- Ensure SLAs are met by performing proactive troubleshooting and capacity planning
- Monitor and maintain the overall environment
- Participate in troubleshooting, capacity planning, performance analysis, and Root Cause Analysis

### Senior Network Engineer

**Optomi** (UCLA Contracted) - Los Angeles, CA

*April 2016 to October 2016*

- Involved in network engineering tasks and projects
- Assisted in the design and implementation of network solutions
- Collaborated with a cross-functional team to meet project deadlines

### Network Engineer

**NIC Partners INC (Cedars Sinai Medical Center)** - Rancho Cucamonga, CA

*October 2015 to April 2016*

- Managed network infrastructure for Cedars Sinai Medical Center
- Implemented and maintained network switches, routers, and firewalls
- Conducted troubleshooting and resolved network issues

### Network Engineer

**Bob Hope (Burbank) Airport** - Burbank, CA

*November 2014 to October 2015*

- Supported network infrastructure for Bob Hope Airport
- Configured and maintained routers, switches, and wireless access points
- Resolved network issues and provided technical support to end-users

### Network/System Administrator

**Prescott Communications Inc** - Mission Hills, CA

*May 2007 to November 2014*

- Managed network and system administration tasks
- Monitored network performance and implemented necessary improvements
- Conducted system upgrades and ensured data security

### LAN Systems Administrator

**BMS Communications Inc** - Simi Valley, CA

*September 2001 to May 2007*

- Oversaw LAN administration tasks
- Configured and maintained network devices
- Provided technical support to end-users

---

## Education

**CCNP, CCNA Voice, Python**

*Brand College* - Glendale, CA

- Completed training in Python Programming for Network Engineers
- Completed Cisco Switch (642-813) class for CCNP certification
- Completed Cisco Route (642-902) class for CCNP certification

**B.S in Computer Visualizations Technology**

*ITT Technical Institute* - Sylmar, CA

---

## Skills

- Python (10+ years)

## Certifications/Licenses

- CCNA

---
"""

# open json file UCLA_JSON_NAME.json
with open('JSON_NAME.json') as json_file:
    data = json.load(json_file)
    
    SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
    ]
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)

    service = build('gmail', 'v1', credentials=creds)
        
    for p in data:
        print('Subject: ' + p['Subject'])
        print('Sender: ' + p['Sender'])
        print('Date: ' + p['Date'])
        print('Snippet: ' + p['Snippet'])
        print('Message_body: ' + p['Message_body'])
        print('')
        
        # save email as txt file
        filename = p['Subject']
        filename = filename.replace('/', '').replace('|', '')
        
        # clean filename for filename from characters like Â\xa0, Â\xa0C2C and % symbols
        filename = filename.replace('%', '').replace(':', '')
        filename = filename.replace('Â\xa0', '')
        filename = filename.replace('Â\xa0C2C', '')
        
        with open('./dist/' + filename + '.txt', 'w') as f:
            f.write(p['Message_body'])
        
        # OpenAI API
        prompt = pre_prompt + "Write a resume that would be perfect for the following job position. Format it in raw markdown.\n\n" + p['Message_body']
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                        # {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "system", "content": "You are an expert in resume and career consultation."},
                        {"role": "user", "content": prompt}
                ]
        )
        print(response['choices'][0]['message']['content'])
        

        
        # save resume as markdown file
        with open('./dist/' + filename + '.md', 'w') as f:
            f.write(response['choices'][0]['message']['content'])
        
        # OpenAI API
        prompt = pre_prompt + "Write a cover letter as the applicant wishing employment for the following job position. Format it in raw markdown.\n\n ### \nJob Position Email:\n\n" + p['Message_body']
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                        # {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "system", "content": "You are an expert in resume and career consultation."},
                        {"role": "user", "content": prompt}
                ]
        )
        print(response['choices'][0]['message']['content'])
        
        # save resume as markdown file
        cover_letter_filename = filename + ' - cover letter.md'

        with open('./dist/' + cover_letter_filename, 'w') as f:
            f.write(response['choices'][0]['message']['content'])
            
        

     
        # message = MIMEText('This is the body of the email\n\nJob Description: \n\nTESTING')
        
        # clean filename for filename
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
        resume_filename = filename + '.md'
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
            f"attachment; filename= " + resume_filename + "",
        )
        message.attach(part)
        
        
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        
        try:
            message = (service.users().messages().send(userId="me", body=create_message).execute())
            print(F'sent message to {message} Message Id: {message["id"]}')
        except HTTPError as error:
            print(F'An error occurred: {error}')
            message = None
            