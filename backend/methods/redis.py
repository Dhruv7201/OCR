from redis import Redis as RedisClient


class MyRedis:
    def __init__(self):
        self.redis = RedisClient(host="localhost", port=6379, db=0)

    def get(self, key):
        return self.redis.get(key)

    def set(self, key, value, ex=7200):
        return self.redis.set(key, value, ex=ex)

    def delete(self, key):
        return self.redis.delete(key)

    def keys(self, pattern):
        return self.redis.keys(pattern)

    def flushall(self):
        return self.redis.flushall()

    def keys(self, pattern):
        return self.redis.keys(pattern)


if __name__ == "__main__":
    redis = MyRedis()
    redis.flushall()
