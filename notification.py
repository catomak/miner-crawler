import telegram
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class Notification:

    def __init__(self, devices, token, recipients):
        self.token = token
        self.devices = devices
        self.message = self.create_text(devices)
        self.recipients = recipients

    def create_text(self, devices):
        mess_start = 'Перечисленные устройства не отвечают:'
        mess_end = f'Всего {len(self.devices)} устройств'
        return mess_start + '\n'.join(devices) + mess_end

    def send_message(self, recipient):
        pass

    def notify_all(self):
        pass


class TelegramNotification(Notification):

    def send_message(self, recipient):
        tg = telegram.Bot(self.token)
        tg.send_message(text=self.message, chat_id=recipient)

    def notify_recipients(self):
        for r in self.recipients:
            self.send_message(r)


class EmailNotification(Notification):

    pass
