import json

# personal information


class UserInfo(object):
    def __init__(self, username, password, phone, email, booking_time, booking_field_number):
        self.__username = username
        self.__password = password
        self.__phone = phone
        self.__email = email
        self.__booking_time = booking_time
        self.__booking_field_number = booking_field_number

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def get_phone(self):
        return self.__phone

    def get_email(self):
        return self.__email

    def get_booking_time(self):
        return self.__booking_time

    def get_booking_field_number(self):
        return self.__booking_field_number


my_user_info = None


def init_my_user_info():
    with open('my_user_info.json', encoding='utf-8') as f:
        content = f.read()
        json_data = json.loads(content)
        global my_user_info
        my_user_info = UserInfo(
            json_data['username'],
            json_data['password'],
            json_data['phone'],
            json_data['email'],
            json_data['booking_time'],
            json_data['booking_field_number'],
        )

        f.close()


# 注意初始化用户信息
init_my_user_info()
