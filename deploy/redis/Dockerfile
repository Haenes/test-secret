# FROM redis:7.4.2-alpine
FROM redis:7.4.2-alpine

COPY redis.conf /usr/local/etc/redis/redis.conf

USER redis

CMD [ "redis-server", "/usr/local/etc/redis/redis.conf" ]
