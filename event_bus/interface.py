
from abc import ABCMeta, abstractmethod


class EventBusInterface(object):
    __metaclass__ = ABCMeta  # 指定这是一个抽象类

    @abstractmethod  # 抽象方法
    def publish(self, event_name, message):
        pass

    def subscribe(self, event_name, *consumer_functions):
        pass
