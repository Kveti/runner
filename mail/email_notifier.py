import smtplib


def send_email_notification(recepient, subject, body):
    # Set email server settings
    smtp_server = 'mail.maurit.sk'
    smtp_port = 587  # For use with the STARTTLS command
    
    # Set email user credentials
    email_address = 'teresa@maurit.sk'
    email_password = ''

    # Set email headers and body
    from_header = 'From: Teresa <teresa@maurit.sk>'
    to_header = 'To: ' + recepient[0]
    subject_header = 'Subject: ' + subject
    
    message = f'{from_header}\n{to_header}\n{subject_header}\n\n{body}'
    
    # Create secure connection with server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(email_address, email_password)
        server.sendmail(email_address, recepient[1], message) #.encode("utf-8"))


if __name__ == "__main__":
    send_notification(["Tester <tester@maurit.sk>", "tester@maurit.sk"], "DEV - PortalVS - webapp", "nula, jedna, dva")
