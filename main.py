from module.user_info import my_user_info
import module.badminton_booking as badminton_booking
import tools.cron as cron
import tools.thread as thread
import module.event_bus_example_impl as event_bus_example_impl
import module.email as email
import time
from flask import Flask, request, jsonify

event_name = "badminton_booking"


def booking_start():
    booking = badminton_booking.BadmintonBooking(
        my_user_info.get_username(),
        my_user_info.get_password(),
        my_user_info.get_phone(),
        my_user_info.get_booking_time(),
        my_user_info.get_booking_field_number(),
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

    # 向这个接口发起一次请求，即可创建一次预约任务
    # GET http://localhost:9000/badminton-booking?token=0916

    @app.route("/badminton-booking", methods=["GET"])
    def badminton_booking_handler():
        token = request.args.get("token")
        if token != "0916":
            return jsonify({"msg": "forbidden!"})

        try:
            thread.Thread(
                name="my-task",
                target=cron.cron_task_once,
                args=(booking_start, "12:30")).start()
        except Exception as e:
            return jsonify({"msg": "mission creation failed,{}".format(e)})

        return jsonify({"msg": "booking mission created!"})

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
