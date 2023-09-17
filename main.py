from module.user_info import init_or_update_my_user_info
import module.user_info
import module.badminton_booking as badminton_booking
import tools.cron as cron
import tools.thread as thread
import module.event_bus_example_impl as event_bus_example_impl
import module.email as email
import time
from flask import Flask, request, jsonify, send_from_directory
import json

TOKEN = "0916"
event_name = "badminton_booking"
regular_time = "12:30"

# global my_user_info


def booking_start():
    booking = badminton_booking.BadmintonBooking(
        # 使用 module.user_info.XXX 确保引用的是最新修改的变量
        module.user_info.my_user_info.get_username(),
        module.user_info.my_user_info.get_password(),
        module.user_info.my_user_info.get_phone(),
        module.user_info.my_user_info.get_booking_time(),
        module.user_info.my_user_info.get_booking_field_number(),
    )
    try:
        booking.exec()
        event_bus_example_impl.get_event_bus().publish(
            event_name, "booking OK!!!")

    except Exception as e:
        print(e)
        event_bus_example_impl.get_event_bus().publish(
            event_name, "booking [ERROR]")


def subscribe_event(event_name):
    event_bus_example_impl.get_event_bus().subscribe(
        event_name,
        email.send_email,
    )


def start_api():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.config['STATIC_FOLDER'] = './ui'

    # 向这个接口发起一次请求，即可创建一次预约任务
    # GET http://localhost:9000/badminton-booking?token=0916

    @app.route("/badminton-booking", methods=["GET"])
    def badminton_booking_handler():
        token = request.args.get("token")
        if token != TOKEN:
            return jsonify({"msg": "forbidden!"})

        print(module.user_info.my_user_info.get_username(),  module.user_info.my_user_info.get_booking_time(),
              module.user_info.my_user_info.get_booking_field_number())

        try:
            t = thread.Thread(
                name="my-task",
                target=cron.cron_task_once,
                args=(booking_start, regular_time))
            thread.append_to_thread_list(t)

        except Exception as e:
            return jsonify({"msg": "mission creation failed,{}".format(e)})

        return jsonify({"msg": "booking mission created!"})

    # 个人信息页面
    # GET http://localhost:9000/user-info/index.html?token=0916

    @app.route("/user-info/<path:filename>", methods=["GET"])
    def user_info_page(filename):
        token = request.args.get("token")
        if token != TOKEN:
            return jsonify({"msg": "forbidden!"})
        return send_from_directory(app.config['STATIC_FOLDER'], filename)

    @app.route("/update-user-info", methods=["PUT"])
    def update_user_info():
        json_data = json.loads(request.data)
        # print(json_data)
        file_data = {
            "username": json_data["username"],
            "password": json_data["password"],
            "phone": json_data["phone"],
            "email": json_data["email"],
            "booking_time": json_data["bookingTime"],
            "booking_field_number": json_data["bookingFieldNumber"],
        }

        # 更新用户信息文件
        with open("my_user_info.json", 'w') as f:
            f.write(json.dumps(file_data))
        f.close()
        # 更新用户信息
        init_or_update_my_user_info()

        return jsonify({"msg": "user_info updated!"})

    app.run("0.0.0.0", "9000", threaded=True)


def main():
    if __name__ == '__main__':
        subscribe_event(event_name)
        start_api()


main()


# def main():
#     subscribe_event(event_name)
#     # booking_start()

#     # 单线程 定时任务
#     thread.Thread(name="my-task", target=cron.cron_task_once,
#                   args=(booking_start, "12:30")).start()
#     time.sleep(2)


# 多线程 定时任务
# thread.append_to_thread_list(
#     thread.Thread(name="booking-task-01", target=cron.cron_task_once,
#                   args=(booking_start, "22:32")),
#     thread.Thread(name="booking-task-02", target=cron.cron_task_once,
#                   args=(booking_start, "22:33"))
# )
# thread.start_thread_list()
# time.sleep(2)


# main()
