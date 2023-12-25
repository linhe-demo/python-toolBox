from pkg.rocketMq import RocketMq

if __name__ == "__main__":
    RocketMq(topic="LinHe-Demo", message="hello world").sendMsg()
