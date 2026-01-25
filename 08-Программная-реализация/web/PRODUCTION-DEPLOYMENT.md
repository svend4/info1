# AI Generator API - Production Deployment Guide

🚀 Руководство по production deployment AI-powered генератора проектов

---

## 🐳 Docker Deployment

### Quick Start

```bash
# Build and run с docker-compose
docker-compose up -d

# Проверка здоровья
curl http://localhost:8080/health
curl http://localhost:5001/api/ai/health

# Логи
docker-compose logs -f ai-api

# Остановка
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t ai-generator-api:latest -f Dockerfile ../..

# Run container
docker run -d \
  --name ai-api \
  -p 5001:5001 \
  -e SECRET_KEY="your-secret-key" \
  -e API_KEYS="key1,key2,key3" \
  -v $(pwd)/../../tools/ai_generator/models:/app/tools/ai_generator/models:ro \
  ai-generator-api:latest

# Health check
curl http://localhost:5001/api/ai/health
```

---

## 🔐 Security Configuration

### API Keys

Set up API keys через environment variables:

```bash
# В docker-compose.yml
environment:
  - API_KEYS=production-key-1,production-key-2,admin-key-xyz

# Или в .env файле
API_KEYS=key1,key2,key3
SECRET_KEY=your-super-secret-key-change-this
```

### Usage

```bash
# С header
curl -H "X-API-Key: production-key-1" \
  -X POST http://localhost:5001/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"description": "Финтех стартап"}'

# С query parameter
curl -X POST "http://localhost:5001/api/ai/analyze?api_key=production-key-1" \
  -H "Content-Type: application/json" \
  -d '{"description": "Финтех стартап"}'
```

---

## ⚡ Rate Limiting

**Default limits (nginx + Flask):**

- **General:** 100 requests/hour
- **Analyze:** 50 requests/hour
- **Generate:** 20 requests/hour

**Customize limits:**

```python
# В ai_api_production.py
RATE_LIMIT_ANALYZE = "100 per hour"
RATE_LIMIT_GENERATE = "50 per hour"
```

```nginx
# В nginx.conf
limit_req_zone $binary_remote_addr zone=ai_limit:10m rate=20r/m;
```

---

## 📊 Monitoring & Metrics

### Health Check

```bash
curl http://localhost:5001/api/ai/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-24T22:00:00",
  "ai_components": "ready",
  "ml_model": "loaded"
}
```

### Metrics Endpoint

```bash
curl -H "X-API-Key: your-key" http://localhost:5001/api/ai/metrics
```

Response:
```json
{
  "requests_total": 1523,
  "requests_success": 1498,
  "requests_error": 25,
  "analyze_count": 890,
  "generate_count": 633,
  "uptime_seconds": 86400,
  "success_rate": 98.36
}
```

### Logs

```bash
# Docker logs
docker-compose logs -f ai-api

# Nginx access logs
docker-compose exec nginx tail -f /var/log/nginx/access.log

# Nginx error logs
docker-compose exec nginx tail -f /var/log/nginx/error.log
```

---

## 🚦 CI/CD Pipeline

### GitHub Actions Workflow

Автоматический CI/CD настроен в `.github/workflows/ai-api-deploy.yml`:

**Triggers:**
- Push to `main` → Deploy to production
- Push to `develop` → Deploy to staging
- Pull requests → Run tests only

**Steps:**
1. **Test** - Run AI component tests
2. **Build** - Build Docker image
3. **Test Docker** - Health check on container
4. **Deploy** - Deploy to environment
5. **Notify** - Send notification

### Manual Deployment

```bash
# 1. Build
docker build -t ai-api:v1.0.0 .

# 2. Tag
docker tag ai-api:v1.0.0 your-registry.com/ai-api:v1.0.0
docker tag ai-api:v1.0.0 your-registry.com/ai-api:latest

# 3. Push
docker push your-registry.com/ai-api:v1.0.0
docker push your-registry.com/ai-api:latest

# 4. Deploy на сервере
ssh user@production-server
docker pull your-registry.com/ai-api:latest
docker-compose up -d --no-deps --build ai-api
```

---

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-secret-key...` |
| `API_KEYS` | Comma-separated API keys | `demo-key-123` |
| `FLASK_ENV` | Flask environment | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ML_MODEL_PATH` | Path to ML model | `/app/tools/...` |

**Example `.env` file:**
```env
SECRET_KEY=super-secret-production-key-xyz123
API_KEYS=prod-key-1,prod-key-2,admin-key-special
FLASK_ENV=production
LOG_LEVEL=WARNING
```

---

## 🌐 Reverse Proxy Setup (Nginx)

### With docker-compose

```yaml
# Уже настроено в docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"  # HTTP
      - "443:443"  # HTTPS (добавьте SSL)
```

### SSL/TLS Configuration

```nginx
# Добавьте в nginx.conf
server {
    listen 443 ssl http2;
    server_name api.your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # ... остальная конфигурация
}
```

---

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  ai-api:
    deploy:
      replicas: 3  # 3 инстанса API
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
```

### Load Balancing (nginx)

```nginx
upstream ai_api {
    least_conn;  # Load balancing algorithm
    server ai-api-1:5001;
    server ai-api-2:5001;
    server ai-api-3:5001;
}
```

---

## 🐛 Troubleshooting

### API не отвечает

```bash
# 1. Проверить контейнер
docker ps | grep ai-api

# 2. Проверить логи
docker logs ai-api

# 3. Проверить health
curl http://localhost:5001/api/ai/health

# 4. Перезапустить
docker-compose restart ai-api
```

### Rate limit errors (429)

```bash
# Проверить nginx rate limiting
docker-compose exec nginx cat /var/log/nginx/access.log | grep 429

# Увеличить лимиты в nginx.conf
limit_req_zone $binary_remote_addr zone=ai_limit:10m rate=30r/m;
```

### ML model not loaded

```bash
# 1. Проверить что модель существует
ls -la tools/ai_generator/models/project_classifier.pkl

# 2. Переобучить модель
cd tools/ai_generator
python ml_classifier.py --train

# 3. Перезапустить контейнер
docker-compose restart ai-api
```

### Out of memory

```bash
# Увеличить memory limit
# В docker-compose.yml
services:
  ai-api:
    deploy:
      resources:
        limits:
          memory: 4G  # Было 2G
```

---

## 📊 Performance

**Benchmarks:**

| Operation | Avg Time | P95 | P99 |
|-----------|----------|-----|-----|
| Health check | 5ms | 10ms | 15ms |
| Analyze | 80ms | 150ms | 200ms |
| Generate | 2s | 3s | 5s |

**Optimization tips:**

1. **Кэширование ML predictions** для одинаковых описаний
2. **Async processing** для generate endpoint
3. **CDN** для static файлов
4. **Database** для сохранения результатов

---

## 🔒 Security Checklist

- [ ] Сменить `SECRET_KEY` с default значения
- [ ] Сгенерировать уникальные `API_KEYS`
- [ ] Настроить HTTPS/SSL
- [ ] Настроить CORS для specific домена (убрать `*`)
- [ ] Включить rate limiting
- [ ] Настроить firewall rules
- [ ] Регулярные security updates
- [ ] Мониторинг подозрительной активности
- [ ] Backup ML модели

---

## 📚 Additional Resources

- [Flask Production Best Practices](https://flask.palletsprojects.com/en/3.0.x/deploying/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Nginx Rate Limiting](https://www.nginx.com/blog/rate-limiting-nginx/)

---

## ✅ Production Checklist

Before going to production:

- [ ] Environment variables настроены
- [ ] API keys сгенерированы
- [ ] SSL certificates установлены
- [ ] Nginx reverse proxy работает
- [ ] Rate limiting настроен
- [ ] Monitoring включён
- [ ] Logs rotation настроен
- [ ] Backup strategy определена
- [ ] CI/CD pipeline протестирован
- [ ] Load testing выполнен
- [ ] Documentation обновлена

---

**Ready for production!** 🚀
