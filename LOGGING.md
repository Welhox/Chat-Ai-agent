# 📊 Logging & Monitoring Guide

This document explains the comprehensive logging and monitoring system implemented in the AI Agent for security, usage tracking, and performance analysis.

## 🔍 What Gets Logged

### Security Events
- **Blocked Requests**: Rate limit violations, size limit violations
- **Authentication Failures**: Invalid/missing API keys
- **Usage Warnings**: High traffic patterns and potential abuse
- **Security Violations**: Requests exceeding safety thresholds

### Usage Tracking
- **Every Request**: Client IP, estimated token count, timestamp
- **Hourly Patterns**: Request volume aggregated by hour
- **Per-IP Statistics**: Usage patterns by individual clients
- **Token Consumption**: Estimated costs for budget monitoring

## 📋 Log Levels & Event Types

### INFO Level - Normal Operations
```
INFO: Request from 172.18.0.1, estimated tokens: 450
INFO: Moderate usage: 120 requests in hour 2025-09-25-14
```
- Successful requests with token estimates
- Moderate usage notifications (100+ requests/hour)

### WARNING Level - Security Concerns
```
WARNING: High usage warning: 155 requests in hour 2025-09-25-14
WARNING: Blocked request from 172.18.0.1
```
- High usage patterns (150+ requests/hour)
- Individual blocked requests due to rate limiting

### ERROR Level - Security Violations
```
ERROR: USAGE LIMIT EXCEEDED: 201 requests in hour 2025-09-25-14
ERROR: Authentication failed from 192.168.1.100
```
- Hourly limits exceeded (200+ requests/hour)
- Authentication failures and unauthorized access attempts

## 🛠️ Accessing Logs

### 1. Real-time Container Logs

#### View Live Logs
```bash
cd /home/casimirri/code/python/Chat-Ai-agent
docker compose logs -f
```

#### Recent Activity (Last 50 Lines)
```bash
docker compose logs --tail=50
```

#### Filter Security Events Only
```bash
docker compose logs | grep -E "(WARNING|ERROR)"
```

#### Monitor During Demonstrations
```bash
# Perfect for job interview demos
docker compose logs -f | grep -E "(Request from|WARNING|ERROR)"
```

### 2. Usage Statistics API

#### Get Comprehensive Stats
```bash
curl -H "X-API-Key: test123" http://localhost:8000/usage-stats | jq .
```

#### Example Response
```json
{
  "total_requests": 42,
  "blocked_requests": 2,
  "estimated_total_tokens": 15750,
  "requests_last_24h": {
    "2025-09-25-13": 28,
    "2025-09-25-14": 14
  },
  "top_ips": {
    "172.18.0.1": 30,
    "192.168.1.100": 12
  }
}
```

#### Quick Checks
```bash
# Check hourly patterns
curl -s -H "X-API-Key: test123" localhost:8000/usage-stats | jq '.requests_last_24h'

# Check for blocked requests
curl -s -H "X-API-Key: test123" localhost:8000/usage-stats | jq '.blocked_requests'

# Monitor token usage for costs
curl -s -H "X-API-Key: test123" localhost:8000/usage-stats | jq '.estimated_total_tokens'
```

## 📈 Security Thresholds & Triggers

### Rate Limiting
| Limit | Action | Log Level |
|-------|--------|-----------|
| 30/minute | Block excess requests | WARNING |
| 100/hour | Info logging | INFO |
| 150/hour | Warning logging | WARNING |
| 200/hour | Block all requests | ERROR |

### Size Limits
| Limit | Threshold | Action |
|-------|-----------|--------|
| Message | 10,000 chars | Block with 413 status |
| History | 100 messages | Block with 413 status |
| Total Request | 100,000 chars | Block with 413 status |

### Tool Call Limits
- **Max Iterations**: 5 per request
- **Timeout**: 20 seconds total
- **Purpose**: Prevent runaway costs and infinite loops

## 🎯 Practical Monitoring Scenarios

### During Job Interviews
```bash
# Terminal 1: Run the demo
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test123" \
  -d '{"message": "Tell me about Casimirs projects"}'

# Terminal 2: Monitor in real-time
docker compose logs -f | grep -E "(Request from|WARNING|ERROR)"
```

### Daily Health Checks
```bash
# Morning routine - check overnight activity
docker compose logs --since=24h | grep -c "Request from"
docker compose logs --since=24h | grep -c "ERROR"

# Get usage summary
curl -s -H "X-API-Key: test123" localhost:8000/usage-stats
```

### Security Audits
```bash
# Look for abuse patterns
docker compose logs | grep "USAGE LIMIT EXCEEDED"
docker compose logs | grep "Invalid or missing API key"
docker compose logs | grep "Blocked request"

# Analyze top IPs for unusual activity
curl -s -H "X-API-Key: test123" localhost:8000/usage-stats | jq '.top_ips'
```

### Performance Analysis
```bash
# Token usage trends
docker compose logs | grep "estimated tokens" | tail -20

# Request distribution by hour
curl -s -H "X-API-Key: test123" localhost:8000/usage-stats | jq '.requests_last_24h'
```

## 🔍 Log Analysis & Interpretation

### Identifying Traffic Patterns

#### Normal Legitimate Usage
```
INFO: Request from 192.168.1.50, estimated tokens: 450
INFO: Request from 192.168.1.50, estimated tokens: 720
INFO: Request from 10.0.0.100, estimated tokens: 320
```
- Varied request timing
- Different IP addresses
- Reasonable token counts
- Mixed request patterns

#### Suspicious Activity
```
WARNING: High usage warning: 180 requests in hour 2025-09-25-14
INFO: Request from 172.18.0.1, estimated tokens: 50
INFO: Request from 172.18.0.1, estimated tokens: 50
INFO: Request from 172.18.0.1, estimated tokens: 50
```
- Regular intervals
- Identical token counts
- Single IP high frequency
- Repetitive patterns

#### Confirmed Abuse
```
ERROR: USAGE LIMIT EXCEEDED: 205 requests in hour 2025-09-25-14
WARNING: Blocked request from 172.18.0.1
WARNING: Blocked request from 172.18.0.1
```
- Exceeded hourly limits
- Continued attempts after blocking
- No authentication or invalid keys

### Cost Monitoring

#### Token Estimation Formula
```python
# Rough estimation: 4 characters = 1 token
estimated_tokens = total_characters // 4 + buffer

# Buffer accounts for:
# - System prompt (~300 tokens)
# - Tool call overhead (~200 tokens)  
# - Response generation (~500 tokens)
```

#### Daily Cost Tracking
```bash
# Get total estimated tokens for the day
TODAY=$(date +%Y-%m-%d)
docker compose logs --since=24h | grep "estimated tokens" | \
  grep -oE "tokens: [0-9]+" | grep -oE "[0-9]+" | \
  awk '{sum += $1} END {print "Total estimated tokens today:", sum}'
```

## ⚙️ Configuration & Customization

### Adjusting Log Levels
Edit `app/main.py`:
```python
# Change log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)

# For more detailed debugging
logging.basicConfig(level=logging.DEBUG)
```

### Customizing Thresholds
```python
# In check_hourly_limits() function
if hourly_requests > 200:  # Adjust this value
    logger.error(f"USAGE LIMIT EXCEEDED: {hourly_requests}")
    return False
```

### Adding Custom Metrics
```python
# Add to usage_stats dictionary
usage_stats["custom_metric"] = defaultdict(int)

# Track in your functions
usage_stats["custom_metric"]["key"] += 1
```

## 🚨 Alert Integration (Future Enhancement)

### Email Alerts
```python
# Add to high usage detection
if hourly_requests > 150:
    send_alert_email(f"High usage: {hourly_requests} requests/hour")
```

### Webhook Notifications
```python
# Integrate with Slack/Discord
def send_webhook_alert(message):
    requests.post(WEBHOOK_URL, json={"text": message})
```

### Log Rotation
```python
# For production, consider log rotation
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'ai-agent.log', 
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

## 📚 Best Practices

### For Development
- Monitor logs during testing: `docker compose logs -f`
- Check usage stats regularly: `curl localhost:8000/usage-stats`
- Test rate limits before deploying

### For Demonstrations
- Have monitoring terminal open during demos
- Show usage statistics to demonstrate security awareness
- Explain the security measures implemented

### For Production
- Set up log rotation for disk space management
- Implement automated alerting for abuse detection
- Regular security audits of access patterns
- Monitor token usage for cost control

### For Employment Interviews
- Demonstrate real-time monitoring capabilities
- Show understanding of security logging principles
- Explain cost management through usage tracking
- Highlight abuse prevention measures

This logging system provides comprehensive visibility into your AI agent's operation, making it production-ready and interview-worthy! 🚀