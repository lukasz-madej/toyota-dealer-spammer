import importlib.util
from email.message import EmailMessage
from dotenv import load_dotenv
import requests
import smtplib
import os
import inquirer

load_dotenv()

api_url = 'https://www.toyota.pl/api/dealer/drive'
coordinates = {
    'lat': 21.060651,
    'lng': 52.249529
}
parameters = {
    'count': 100,
    'limitSearchDistance': 600,
    'isCurrentLocation': 'false'
}
exclude_from_emails = ['radosc', 'dostawcze']
gmail_user = os.getenv('GMAIL_USER')
gmail_pass = os.getenv('GMAIL_PASS')
templates = []
templates_path = 'templates'
email_subject = ''
email_text = ''


def get_unique_list(full_list):
    return list(set(full_list))


def filter_email_list(email_list):
    return [filtered_email for filtered_email in email_list if
            not any(exclude in filtered_email for exclude in exclude_from_emails)]


def get_params():
    for key, value in parameters.items():
        input_param = input('Enter the value for parameter "{0}": '.format(key)).split()
        if input_param:
            # noinspection PyTypeChecker
            parameters[key] = input_param[0]

    return parameters


def select_template():
    for (dirpath, dirnames, filenames) in os.walk(templates_path):
        templates.extend(filenames)
        break

    print(templates)

    questions = [
        inquirer.List('template',
                      message='Select an email template',
                      choices=templates,
                      ),
    ]

    answers = inquirer.prompt(questions)
    spec = importlib.util.spec_from_file_location(answers['template'], 'templates/' + answers['template'])
    template = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(template)

    global email_text
    email_text = template.email_text
    global email_subject
    email_subject = template.email_subject


def compose_url():
    final_url = '{0}/{1}/{2}'.format(api_url, coordinates['lat'], coordinates['lng'])

    return final_url


def get_dealers_data():
    response = requests.get(compose_url(), get_params())
    data = response.json()

    return data


def parse_dealers_data(data):
    dealer_emails = []

    for dealer in data['dealers']:
        if dealer['country'] == 'pl' \
                and any(service['service'] == 'ShowRoom' for service in dealer['services']) \
                and dealer['eMail']:
            dealer_emails.append(dealer['eMail'])

    return filter_email_list(get_unique_list(dealer_emails))


def get_dealer_emails():
    return parse_dealers_data(get_dealers_data())


def send_email(recipient, recipient_count):
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        msg = EmailMessage()

        server.ehlo()
        server.login(gmail_user, gmail_pass)

        msg['Subject'] = email_subject
        msg['From'] = gmail_user
        msg['To'] = recipient
        msg.set_content(email_text)

        server.send_message(msg)
        server.close()

        print('[{0}] Sent email to: {1}'.format(recipient_count, recipient))
    except Exception as ex:
        print('Error sending email to: {0}'.format(recipient))
        print(ex)


select_template()
emails = get_dealer_emails()
print('Found {0} email addresses'.format(len(emails)))

for count, email in enumerate(emails, start=1):
    send_email(email, count)
