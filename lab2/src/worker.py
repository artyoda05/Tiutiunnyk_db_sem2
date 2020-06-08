import redis
import random
import datetime
import time
from threading import Thread


class Worker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.connection = redis.Redis(host='192.168.99.102', charset="utf-8", decode_responses=True)
        self.delay = random.randint(0, 5)

    def run(self):
        while True:
            message = self.connection.brpop("queue:")
            if message:
                msg_id = int(message[1])

                self.connection.hmset('message:%s' % msg_id, {'status': 'checking'})

                message = self.connection.hmget("message:%s" % msg_id, ["sender_id", "receiver_id"])
                sender_id = int(message[0])

                self.connection.hincrby("user:%s" % sender_id, "in_queue", -1)
                self.connection.hincrby("user:%s" % sender_id, "checking", 1)
                time.sleep(self.delay)

                is_spam = random.random() > 0.65

                pipe = self.connection.pipeline(True)
                pipe.hincrby("user:%s" % sender_id, "checking", -1)

                if is_spam:
                    sender_login = self.connection.hmget("user:%s" % sender_id, ["login"])[0]
                    pipe.zincrby("spam:", 1, "user:%s" % sender_login)
                    pipe.hmset('message:%s' % msg_id, {'status': 'blocked'})
                    pipe.hincrby("user:%s" % sender_id, "blocked", 1)
                    pipe.publish('spam', f"{datetime.datetime.now()} - Spam from user \"%s\""
                                         f"\"%s\"\n" % (
                                            sender_login, self.connection.hmget("message:%s" % msg_id, ["content"])[0]))

                else:
                    pipe.hmset('message:%s' % msg_id, {'status': 'sent'})
                    pipe.hincrby("user:%s" % sender_id, "sent", 1)
                    pipe.sadd("sentto:%s" % int(message[1]), msg_id)

                pipe.execute()


if __name__ == '__main__':
    for x in range(10):
        worker = Worker()
        worker.daemon = True
        worker.start()
    while True:
        pass
