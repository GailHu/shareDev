# -*- coding: utf-8 -*-

import redis


class RedisHelper:
    __instance = None

    @staticmethod
    def get_instance():
        if RedisHelper.__instance is None:
            RedisHelper()
        return RedisHelper.__instance

    def __init__(self, host='localhost', port=6379, db=0, password='123456'):
        if RedisHelper.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.pool = redis.ConnectionPool(host=host, port=port, db=db, password=password)
            self.conn = redis.StrictRedis(connection_pool=self.pool)
            RedisHelper.__instance = self

    '''#################### SORTED SET ###### START ##############'''
    def all_queue(self, key_pattern):
        return self.conn.keys(key_pattern)

    # z_add，放入消息， 指定分数9
    def z_add_message(self, key, message):
        return self.push_message(key, message, 9)

    # 放入一个消息
    def push_message(self, queue_name, message, score):
        self.conn.zadd(queue_name, {message: score})

    # 获取消息，非原子操作，不安全
    def get_message(self, key):
        print(f'get_message :{key}...')
        data_list = self.z_range(key, 0, -1)
        if len(data_list) > 0:
            data = data_list[0]
            self.conn.zrem(key, data)
            return data

    # z_set，获取一条消息，原子操作；将消息翻入另一个执行中队列中
    def pop_message(self, message_queue, executing_queue):
        pop_script = """
        local message = redis.call('ZRANGE', KEYS[1], 0, 0)[1]
        if message ~= nil then
            local score = redis.call('ZSCORE', KEYS[1], message)
            redis.call('ZREM', KEYS[1], message)
            redis.call('ZADD', KEYS[2], score, message)  
        end
        return message
        """
        result = self.conn.eval(pop_script, 2, message_queue, executing_queue)
        return result

    # 通过索引区间返回有序集合成指定区间内的成员
    def z_range(self, key, start_index, end_index):
        return self.conn.zrange(key, start_index, end_index)

    # 删除指定的key
    def z_rem(self, key, data):
        self.conn.zrem(key, data)

    '''#################### SORTED SET ###### END ##############'''

    def set(self, key, value):
        self.conn.set(key, value)

    # 获取key-value
    def get(self, key):
        return self.conn.get(key).decode()

    # 获取key-value
    def h_get(self, key, field):
        return self.conn.hget(key, field).decode()

    # 获取key-value
    def h_set(self, key, field, value):
        return self.conn.hset(key, field, value)

    # 获取hashtable中所有的值
    def h_get_all(self, key):
        res = self.conn.hgetall(key)
        for k in res:
            res[k] = res[k].decode()
        return res

    # 判断key是否存在
    def is_exists(self, key):
        # 返回1存在，0不存在
        return self.conn.exists(key)

    # 添加集合操作
    def add_set(self, key, value):
        # 集合中存在该元素则返回0,不存在则添加进集合中，并返回1、如果key不存在，则创建key集合，并添加元素进去,返回1
        return self.conn.sadd(key, value)

    # 判断value是否在key集合中
    def is_set_exists(self, key, value):
        # 判断value是否在key集合中，返回布尔值
        return self.conn.sismember(key, value)

    # 给key设置过期时间，单位秒
    def expire(self, key, seconds):
        return self.conn.expire(key, seconds)
