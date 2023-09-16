import schedule
import time
import datetime

# 定时任务默认执行时间为12:30

time_layout = '%Y-%m-%d %H:%M:%S'

# execute task in loop


def cron_task(task, time_string="12:30"):
    print(time.strftime(time_layout, time.localtime()), "cron task started!")
    schedule.every().day.at(time_string).do(task)

    while True:
        schedule.run_pending()
        time.sleep(0.01)

# execute task once


def cron_task_once(task, time_string="12:30"):

    print(time.strftime(time_layout, time.localtime()), "cron task started!")

    time_obj = time.strptime(time_string, "%H:%M")

    execute_time = datetime.datetime(
        time.localtime().tm_year,
        time.localtime().tm_mon,
        get_tomorrow_day(),
        time_obj.tm_hour,
        time_obj.tm_min,
    )

    while True:
        current_time = datetime.datetime.now()
        if current_time >= execute_time:
            task()
            break
        time.sleep(0.01)


def get_tomorrow_day():
    return time.localtime().tm_mday+1
