# toyota-dealer-spammer

This is a simple app I wrote to send emails to every Toyota dealership in Poland, to get a quote for a new car I was looking for

##Prerequisites

You will need to provide credentials for application access to your gmail account. Those credentials should be provided as environment variables with the following keys:
* `GMAIL_USER`
* `GMAIL_PASS`

You will also need to provide an email template that is stored in the `templates` directory. You can prepare as many templates as you want, and then select the desired one on application startup.
The template should by a python file containing two variables:
* `email_subject`
* `email_text`