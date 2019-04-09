#!/usr/bin/env python

"""
Author: Jason Stratman
Executes whenever motion is detected to upload image file of
captured motion to Dropbox, send notification email with
image attached, and send notification SMS. Deletes image file
after these tasks are completed in order to save space.
"""

import argparse
import os
import dropbox
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from twilio.rest import Client


def arguments():
    description = """
    Executes whenever motion is detected to upload the media
    files and notify the homeowner.

    Command format:
    python on-motion.py -f <file_path>
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-f',
                        dest='file_path',
                        type=str,
                        default=None,
                        help='Path to motion captured media file.')

    args = parser.parse_args()

    if args.file_path is None:
        print(
            '[!] Please specify a media file path.')
        parser.print_help()
        exit(0)

    return args


class OnMotion:

    @staticmethod
    def get_env_var(name):
        result = os.environ.get(name)

        if result is None:
            raise Exception('Unable to find {}'.format(name))

        return result

    @staticmethod
    def dropbox_upload(file_path):
        """
        Uploads specified file to dropbox.
        """
        dropbox_client = dropbox.Dropbox(
            OnMotion.get_env_var('DROPBOX_ACCESS_TOKEN'))
        upload_location = '/Public/' + os.path.basename(file_path)
        file = open(file_path, 'rb')

        # Upload file to Dropbox
        dropbox_client.files_upload(file.read(), upload_location)

        print('Uploaded image from {} to Dropbox at {}'.format(
              file_path, upload_location))

    @staticmethod
    def send_notification_email(file_path):
        """
        Sends a notification email with the media attached
        """
        sender_email = OnMotion.get_env_var('SENDER_EMAIL')

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email
        msg['Subject'] = "Motion Detected by Raspberry Pi"
        msg.attach(
            MIMEText("Motion detected by Raspberry Pi", 'plain'))

        mime = MIMEBase('application', 'octet-stream')
        mime.set_payload((open(file_path, "rb")).read())
        encoders.encode_base64(mime)
        file_name = os.path.basename(file_path)
        mime.add_header('Content-Disposition',
                        "attachment; filename= %s" % file_name)

        msg.attach(mime)

        smtp_session = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_session.starttls()

        sender_auth = OnMotion.get_env_var('SENDER_AUTH')

        # Gmail Authentication
        smtp_session.login(sender_email, sender_auth)

        # Send email to homeowner
        smtp_session.sendmail(sender_email, sender_email,
                              msg.as_string())

        print('Notification email sent.')

        smtp_session.quit()

    @staticmethod
    def send_notification_sms():
        client = Client(OnMotion.get_env_var('TWILIO_SID'),
                        OnMotion.get_env_var('TWILIO_AUTH_TOKEN'))

        client.messages.create(to=OnMotion.get_env_var('TWILIO_DESTINATION'),
                               from_=OnMotion.get_env_var('TWILIO_SOURCE'),
                               body="Motion detected by Raspberry Pi")

        print('Notification text sent')


if __name__ == '__main__':
    args = arguments()
    file_path = args.file_path

    try:
        if file_path is not None:
            print("Motion file recorded to {}".format(file_path))
            OnMotion.send_notification_email(file_path)
            OnMotion.dropbox_upload(file_path)
            OnMotion.send_notification_sms()
            os.remove(file_path)
        else:
            raise Exception(
                'Please specify a file_path to the media')
    except Exception as e:
        print(e)
