

local now = tonumber(ARGV[1])
local num_scopes = #KEYS

local current_tokens = {}
local capacities = {}
local refill_rates = {}
local ttls = {}


for i = 1, num_scopes do
    local key = KEYS[i]
    local base = 2 + (i - 1) * 3
    local capacity = tonumber(ARGV[base])
    local refill_rate = tonumber(ARGV[base + 1])
    local ttl = tonumber(ARGV[base + 2])

    local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
    local tokens = tonumber(bucket[1])
    local last_refill = tonumber(bucket[2])

    if tokens == nil then
        tokens = capacity
        last_refill = now
    end

    local elapsed = math.max(0, now - last_refill)
    local new_tokens = math.floor(elapsed * refill_rate)
    tokens = math.min(tokens + new_tokens, capacity)

    current_tokens[i] = tokens
    capacities[i] = capacity
    refill_rates[i] = refill_rate
    ttls[i] = ttl
end

local allowed = 1
for i = 1, num_scopes do
    if current_tokens[i] <= 0 then
        allowed = 0
        break
    end
end


for i = 1, num_scopes do
    local key = KEYS[i]
    if allowed == 1 then
        current_tokens[i] = current_tokens[i] - 1
    end
    redis.call('HMSET', key, 'tokens', current_tokens[i], 'last_refill', now)
    redis.call('EXPIRE', key, ttls[i])
end

return allowed