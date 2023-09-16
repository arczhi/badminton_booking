from module.user_info import my_user_info


def send_email(message):
    print("{} send_email ! {}".format(my_user_info.get_email(), message))
    # TODO implement send_email logic
