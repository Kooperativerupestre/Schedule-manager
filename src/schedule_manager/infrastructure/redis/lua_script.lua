local now = tonumber(ARGV[1])
local num_scopes = #KEYS

if num_scopes == 0 then
    return 0
end

local tokens = {}
local ttls = {}

for i = 1, num_scopes do
    local key = KEYS[i]
    local base = 2 + (i - 1) * 3

    local capacity = tonumber(ARGV[base])
    local refill_rate = tonumber(ARGV[base + 1])
    local ttl = tonumber(ARGV[base + 2])

    local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')

    local current = tonumber(bucket[1])
    local last_refill = tonumber(bucket[2])

    if current == nil then
        current = capacity
    else
        local elapsed = math.max(0, now - last_refill)
        current = math.min(
            current + elapsed * refill_rate,
            capacity
        )
    end

    tokens[i] = current
    ttls[i] = ttl
end

for i = 1, num_scopes do
    if tokens[i] < 1 then
        return 0
    end
end

for i = 1, num_scopes do
    local key = KEYS[i]

    tokens[i] = tokens[i] - 1

    redis.call(
        'HSET',
        key,
        'tokens', tokens[i],
        'last_refill', now
    )

    redis.call('EXPIRE', key, ttls[i])
end

return 1