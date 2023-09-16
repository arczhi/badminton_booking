import threading
import time


class Thread (threading.Thread):
    def __init__(self, name, target, args=()):
        self.__name = name
        self.__target = target
        self.__args = args
        # 初始化父类
        super().__init__(target=self.__target,
                         args=self.__args, daemon=True)  # daemon=True 主线程退出的时候，子线程一并退出

    def get_name(self):
        return self.__name


thread_list = []
time_layout = '%Y-%m-%d %H:%M:%S'


def append_to_thread_list(*threads):
    for t in threads:
        thread_list.append(t)


def start_thread_list():
    for t in thread_list:
        t.start()
        print("{} [{}] started !".format(time.strftime(
            time_layout, time.localtime()), t.get_name()))

    # for t in thread_list:
    #     t.join()
    #     print("{} [{}] exited !".format(time.strftime(
    #         time_layout, time.localtime()), t.get_name()))
