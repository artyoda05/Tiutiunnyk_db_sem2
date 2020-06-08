import redis


class Messages:
    def __init__(self):
        self.connection = redis.Redis(host="192.168.99.102", charset="utf-8", decode_responses=True)

    def create(self, content, sender_id, receiver_id):
        if not receiver_id:
            print("Message sending error! Receiver doesn't exist!")
            return

        message_id = int(self.connection.incr('message:id:'))
        pipe = self.connection.pipeline(True)
        pipe.hmset('message:%s' % message_id, {
            'status': "created",
            'content': content,
            'message_id': message_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id
        })

        pipe.lpush("queue:", message_id)
        pipe.hmset('message:%s' % message_id, {'status': 'in_queue'})

        pipe.zincrby("sent:", 1, "user:%s" % self.connection.hmget("user:%s" % sender_id, ["login"])[0])
        pipe.hincrby("user:%s" % sender_id, "in_queue", 1)
        pipe.execute()
        return message_id

    def get_all(self, user_id):
        msg_list = self.connection.smembers("sentto:%s" % user_id)
        for message_id in msg_list:
            msg = self.connection.hmget("message:%s" % message_id, ["sender_id", "content", "status"])
            print("From %s - %s" % (self.connection.hmget("user:%s" % msg[0], ["login"])[0], msg[1]))

            if msg[2] != "delivered":
                pipe = self.connection.pipeline(True)
                pipe.hset("message:%s" % message_id, "status", "delivered")
                pipe.hincrby("user:%s" % msg[0], "sent", -1)
                pipe.hincrby("user:%s" % msg[0], "delivered", 1)
                pipe.execute()
