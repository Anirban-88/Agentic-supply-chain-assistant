# Redis Schema Design

## Overview

Redis is used for high-speed caching and real-time expiry tracking in the supply chain system. This document defines the key patterns, data structures, and management strategies.

## Key Patterns

### 1. Product Expiry Data
**Pattern**: `expiry:product:{product_id}`  
**Type**: Hash  
**Purpose**: Store expiry information for products

**Fields**:
- `batch_id`: Batch identifier
- `expiry_date`: ISO format date (YYYY-MM-DD)
- `quantity`: Remaining quantity
- `location_id`: Storage location
- `freshness_score`: 0-100 score
- `last_updated`: Timestamp

**Example**:
```redis
HSET expiry:product:P001 batch_id B001 expiry_date 2024-01-15 quantity 50 location_id L001 freshness_score 85.5
```

**TTL**: 1 hour (3600 seconds)

### 2. Near-Expiry Items
**Pattern**: `expiry:near:{days}`  
**Type**: Sorted Set  
**Purpose**: Track items expiring within N days

**Score**: Unix timestamp of expiry date  
**Member**: `{product_id}:{batch_id}`

**Example**:
```redis
ZADD expiry:near:7 1705276800 P001:B001
ZADD expiry:near:7 1705363200 P002:B002
```

**Query Examples**:
```redis
# Get all items expiring in next 7 days
ZRANGEBYSCORE expiry:near:7 0 +inf

# Get items expiring today
ZRANGEBYSCORE expiry:near:7 0 [current_timestamp]
```

**TTL**: No expiration (managed by sync process)

### 3. Freshness Scores
**Pattern**: `freshness:{product_id}:{batch_id}`  
**Type**: String (float value)  
**Purpose**: Cache calculated freshness scores

**Value**: Float between 0-100
- 100: Just manufactured
- 75-99: Fresh
- 50-74: Good
- 25-49: Fair
- 0-24: Near expiry

**Example**:
```redis
SET freshness:P001:B001 85.5 EX 1800
GET freshness:P001:B001
```

**TTL**: 30 minutes (1800 seconds)

### 4. Batch Information Cache
**Pattern**: `batch:{batch_id}`  
**Type**: Hash  
**Purpose**: Cache batch details for quick access

**Fields**:
- `product_id`: Product identifier
- `manufacturing_date`: ISO format date
- `expiry_date`: ISO format date
- `quantity`: Current quantity
- `location_id`: Storage location
- `status`: active|expired|recalled

**Example**:
```redis
HSET batch:B001 product_id P001 manufacturing_date 2024-01-01 expiry_date 2024-06-01 quantity 100 location_id L001 status active
```

**TTL**: 2 hours (7200 seconds)

### 5. Alert Cache
**Pattern**: `alert:cache:{product_id}`  
**Type**: List  
**Purpose**: Cache recent alerts for a product

**Elements**: JSON strings of alert objects

**Example**:
```redis
LPUSH alert:cache:P001 '{"alert_id": 1, "batch_id": "B001", "days_until_expiry": 5, "alert_level": "warning"}'
LTRIM alert:cache:P001 0 9  # Keep only last 10 alerts
```

**TTL**: 5 minutes (300 seconds)

### 6. Category Products
**Pattern**: `category:{category_name}`  
**Type**: Set  
**Purpose**: Quick lookup of products by category

**Members**: Product IDs

**Example**:
```redis
SADD category:dairy P001 P002 P003
SMEMBERS category:dairy
```

**TTL**: 1 hour (3600 seconds)

## Indexes and Secondary Access Patterns

### By Expiry Date Range
Use sorted sets with expiry timestamps as scores:

```redis
# Add product to expiry index
ZADD expiry:all [expiry_timestamp] {product_id}:{batch_id}

# Query products expiring between dates
ZRANGEBYSCORE expiry:all [start_timestamp] [end_timestamp]
```

### By Location
**Pattern**: `location:{location_id}:batches`  
**Type**: Set

```redis
SADD location:L001:batches B001 B002 B003
SMEMBERS location:L001:batches
```

### By Alert Level
**Pattern**: `alerts:{level}`  
**Type**: Sorted Set  
**Score**: Days until expiry

```redis
ZADD alerts:critical 2 P001:B001
ZADD alerts:warning 5 P002:B002
```

## Data Refresh Strategy

### 1. Real-time Updates
Triggered by application events:
- Batch creation/update
- Quantity changes
- Status changes

### 2. Periodic Sync
Scheduled synchronization from PostgreSQL:
- **Expiry Sync**: Every 15 minutes
- **Batch Sync**: Every 30 minutes
- **Alert Check**: Every 5 minutes

### 3. Cache Invalidation
Invalidate cache on:
- Quantity changes
- Status updates
- Manual refresh requests

### 4. TTL Management
Automatic expiration for stale data:
- Short TTL for frequently changing data
- Longer TTL for relatively static data
- No TTL for index structures (managed by sync)

## Redis Commands Reference

### Basic Operations
```redis
# Set with expiration
SET key value EX seconds

# Hash operations
HSET key field value
HGET key field
HGETALL key
HDEL key field

# Sorted set operations
ZADD key score member
ZRANGE key start stop
ZRANGEBYSCORE key min max
ZREM key member

# Set operations
SADD key member
SMEMBERS key
SISMEMBER key member
SREM key member

# List operations
LPUSH key value
RPUSH key value
LRANGE key start stop
LTRIM key start stop
```

### Expiry Management
```redis
# Set TTL
EXPIRE key seconds
EXPIREAT key timestamp

# Check TTL
TTL key

# Remove expiry
PERSIST key
```

## Performance Optimization

### Connection Pooling
```python
from redis import ConnectionPool, Redis

pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50,
    decode_responses=True
)

redis_client = Redis(connection_pool=pool)
```

### Pipeline for Bulk Operations
```python
pipe = redis_client.pipeline()
pipe.hset('batch:B001', 'quantity', 100)
pipe.zadd('expiry:near:7', {' P001:B001': timestamp})
pipe.execute()
```

### Lua Scripts for Atomic Operations
```lua
-- Update freshness score atomically
local key = KEYS[1]
local score = ARGV[1]
redis.call('SET', key, score, 'EX', 1800)
return score
```

## Monitoring

### Key Metrics
- Memory usage
- Hit/miss ratio
- Command latency
- Connection count
- Eviction count

### Redis INFO Commands
```redis
INFO memory
INFO stats
INFO clients
INFO keyspace
```

## Backup and Recovery

### RDB Snapshots
Configured in docker-compose with `appendonly yes`

### AOF (Append Only File)
Provides durability for critical data

## Security

### Authentication
Password protected: `redis123`

### Network Isolation
Runs in Docker network `store_network`

### Command Restrictions
Consider using ACLs for production:
```redis
ACL SETUSER agent_user on >password ~expiry:* ~batch:* +get +set +hget +hset
```

## Example Usage Patterns

### Pattern 1: Check Near-Expiry Items
```python
import redis
from datetime import datetime, timedelta

r = redis.Redis(host='localhost', port=6379, db=0, password='redis123')

# Get items expiring in next 7 days
end_timestamp = (datetime.now() + timedelta(days=7)).timestamp()
near_expiry = r.zrangebyscore('expiry:near:7', 0, end_timestamp)

for item in near_expiry:
    product_id, batch_id = item.split(':')
    batch_info = r.hgetall(f'batch:{batch_id}')
    print(f"Product {product_id}, Batch {batch_id}: {batch_info}")
```

### Pattern 2: Update Freshness Score
```python
def calculate_and_cache_freshness(product_id, batch_id, manufacturing_date, expiry_date):
    # Calculate freshness score
    total_days = (expiry_date - manufacturing_date).days
    remaining_days = (expiry_date - datetime.now()).days
    freshness = (remaining_days / total_days) * 100
    
    # Cache with 30-minute TTL
    key = f'freshness:{product_id}:{batch_id}'
    r.setex(key, 1800, freshness)
    
    return freshness
```

### Pattern 3: Batch Pipeline Updates
```python
def sync_batches_from_postgres(batches):
    pipe = r.pipeline()
    
    for batch in batches:
        key = f'batch:{batch["batch_id"]}'
        pipe.hset(key, mapping=batch)
        pipe.expire(key, 7200)  # 2 hour TTL
        
        # Add to expiry index
        expiry_ts = batch['expiry_date'].timestamp()
        member = f"{batch['product_id']}:{batch['batch_id']}"
        pipe.zadd('expiry:near:7', {member: expiry_ts})
    
    pipe.execute()
```

## Troubleshooting

### High Memory Usage
```redis
# Check memory usage
INFO memory

# Find large keys
MEMORY USAGE key

# Clear specific patterns
SCAN 0 MATCH expiry:* COUNT 100
```

### Slow Queries
```redis
# Enable slow log
CONFIG SET slowlog-log-slower-than 10000

# View slow log
SLOWLOG GET 10
```

### Connection Issues
```bash
# Test connection
redis-cli -h localhost -p 6379 -a redis123 PING

# Check connections
redis-cli -a redis123 CLIENT LIST
```

## Best Practices

1. **Use appropriate data structures** for each use case
2. **Set TTLs** on all cached data
3. **Use pipelines** for bulk operations
4. **Monitor memory usage** regularly
5. **Implement connection pooling**
6. **Use Lua scripts** for complex atomic operations
7. **Regular backups** of critical data
8. **Monitor slow queries**
9. **Use key prefixes** for organization
10. **Document key patterns** and their purposes