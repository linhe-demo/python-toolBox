import json

from rocketmq.client import Producer, Message

from tools.file import File


class RocketMq:
    def __init__(self, topic=None, message=None):
        self.topic = topic
        self.message = message
        self.config = File(path="\config\config.json").read_json_config()

    def sendMsg(self):
        producer = Producer('生产者名字')
        producer.set_name_server_address("{}:{}".format(self.config["rocketMq"]["host"], self.config["rocketMq"]["port"]))
        producer.start()

        msg = Message(self.topic)
        msg.set_keys('XXX')
        msg.set_tags('XXX')
        msg.set_body(self.message)
        ret = producer.send_sync(msg)
        print(ret.status, ret.msg_id, ret.offset)
        producer.shutdown()

    def receiveMsg(self):
        pass
        # return KafkaConsumer(self.topic, bootstrap_servers="{}:{}".format(self.config["rocketMq"]["host"], self.config["rocketMq"]["port"]), group_id='my-group')

