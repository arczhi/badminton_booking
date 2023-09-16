from event_bus.interface import EventBusInterface


# 事件总线实现（消息发送，同步消费）

message_map = {}
consumer_function_map = {}


class EventBusExample(EventBusInterface):

    # implement interface functions
    def publish(self, event_name, message):
        message_map[event_name] = message
        self.execute_consumer_function(event_name)

    def subscribe(self, event_name, *consumer_functions):
        consumer_function_map[event_name] = []
        for func in consumer_functions:
            consumer_function_map[event_name].append(func)

    # self functions
    def execute_consumer_function(self, event_name):
        for func in consumer_function_map[event_name]:
            func(message_map[event_name])


event_bus_interface = None


def init_event_bus():
    global event_bus_interface
    event_bus_interface = EventBusExample()


def get_event_bus():
    global event_bus_interface
    if event_bus_interface == None:
        init_event_bus()
    return event_bus_interface
