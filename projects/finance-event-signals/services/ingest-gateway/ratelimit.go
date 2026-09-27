package main

import (
	"context"
	"fmt"
	"math"
	"strconv"
	"time"

	"github.com/redis/go-redis/v9"
)

// RateLimiter is a distributed token bucket backed by Redis. Every service instance
// shares one bucket, so the *global* outbound rate to SEC stays under the cap
// regardless of how many gateway replicas run.
type RateLimiter struct {
	rdb    *redis.Client
	key    string
	rate   float64 // tokens per second
	burst  float64 // bucket capacity
	script *redis.Script
}

const tokenBucketLua = `
local key       = KEYS[1]
local rate      = tonumber(ARGV[1])
local burst     = tonumber(ARGV[2])
local now       = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local d      = redis.call('HMGET', key, 'tokens', 'ts')
local tokens = tonumber(d[1])
local ts     = tonumber(d[2])
if tokens == nil then tokens = burst; ts = now end

local delta = now - ts
if delta < 0 then delta = 0 end
tokens = math.min(burst, tokens + delta * rate)

local allowed = 0
local wait    = 0.0
if tokens >= requested then
  tokens  = tokens - requested
  allowed = 1
else
  wait = (requested - tokens) / rate
end

redis.call('HSET', key, 'tokens', tokens, 'ts', now)
redis.call('EXPIRE', key, math.ceil(burst / rate) + 10)
return {allowed, tostring(wait)}
`

func NewRateLimiter(rdb *redis.Client, key string, ratePerSec, burst float64) *RateLimiter {
	if burst < 1 {
		burst = 1
	}
	return &RateLimiter{
		rdb:    rdb,
		key:    key,
		rate:   ratePerSec,
		burst:  burst,
		script: redis.NewScript(tokenBucketLua),
	}
}

// Wait blocks until one token is available or ctx is cancelled.
func (r *RateLimiter) Wait(ctx context.Context) error {
	for {
		now := float64(time.Now().UnixNano()) / 1e9
		res, err := r.script.Run(ctx, r.rdb, []string{r.key}, r.rate, r.burst, now, 1).Slice()
		if err != nil {
			return fmt.Errorf("ratelimit script: %w", err)
		}
		if len(res) != 2 {
			return fmt.Errorf("ratelimit: unexpected result %v", res)
		}
		allowed, _ := res[0].(int64)
		if allowed == 1 {
			return nil
		}
		waitStr, _ := res[1].(string)
		waitSec, _ := strconv.ParseFloat(waitStr, 64)
		sleep := time.Duration(math.Max(waitSec, 0.01)*float64(time.Second)) + 20*time.Millisecond
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(sleep):
		}
	}
}
