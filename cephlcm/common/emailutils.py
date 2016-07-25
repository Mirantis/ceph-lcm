# -*- coding: utf-8 -*-
"""This module contains a set of utilities, used to manage email send."""


import smtplib

from email.mime import multipart
from email.mime import text


DEFAULT_FROM = "cephlcm <cephlcm@example.com>"


def send(to, subject, text_body, html_body=None, cc=None, bcc=None,
         from_=DEFAULT_FROM, host="localhost", port=smtplib.SMTP_PORT,
         login=None, password=None):
    to, cc, bcc = make_lists(to, cc, bcc)
    message = make_message(from_, to, cc, subject, text_body, html_body)
    client = make_client(host, port, login, password)

    client.sendmail(from_, to, message.as_string())
    client.quit()


def make_lists(to, cc, bcc):
    to = set(to)
    cc = set(cc)
    bcc = set(bcc)

    to -= cc | bcc
    cc -= to | bcc
    bcc -= to | cc

    return list(to), list(cc), list(bcc)


def make_message(from_, to, cc, subject, text_body, html_body):
    message = multipart.MIMEMultipart("alternative")

    message["Subject"] = subject
    message["To"] = ", ".join(to)
    message["Cc"] = ", ".join(cc)

    text_part = text.MIMEText(text_body, "plain")
    message.attach(text_part)

    if html_body:
        html_part = text.MIMEText(html_body, "html")
        message.attach(html_part)

    return message


def make_client(host, port, login, password):
    smtp = smtplib.SMTP(host, port)
    smtp.ehlo()

    if smtp.has_extn("STARTTLS"):
        smtp.starttls()
        smtp.ehlo()

    if login and password:
        smtp.login(login, password)

    return smtp
