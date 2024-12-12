# -*- coding: utf-8 -*-

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json

with open("config.json", "r") as json_file:
    conf = json.load(json_file)

mail_config = conf['mail']


# 发送邮件
def send_mail(address, title, body):
    # 邮件配置
    smtp_server = mail_config['smtp_server']
    smtp_port = mail_config['smtp_port']
    sender_email = mail_config['sender_email']
    sender_password = mail_config['sender_password']
    receiver_email = address

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = title

    message.attach(MIMEText(body, 'plain'))

    # 建立与SMTP服务器的连接
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # 启用TLS加密
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.close()


# 训练完成后发送邮件
def send_train_over_mail(address):
    # 构建邮件内容
    subject = '【AutoSD】Lora模型训练完成'
    body = 'Lora模型训练完成，请查看共享云盘中的模型文件，或登录AutoSD平台查看，谢谢！'
    send_mail(address, subject, body)


# if __name__ == '__main__':
#     mail_addr = "gail.hu@applesay.cn"
#     # send_train_over_mail(address)
#     m_title = "测试邮件-管理员通知"
#     m_body = "这是开发者发送的测试邮件，可以直接删除！"
#     send_mail(mail_addr, m_title, m_body)
