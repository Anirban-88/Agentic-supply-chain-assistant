# Oracle Cloud Deployment - Quick Reference Guide
 
## 🚀 Quick Start Checklist
 
### Pre-Deployment Requirements
- [ ] Oracle Cloud account with billing setup
- [ ] SSH key pair generated
- [ ] Application code ready
- [ ] Domain name (optional)
 
### Infrastructure Setup (30-45 minutes)
- [ ] Create compartment: `supply-chain-dev`
- [ ] Create VCN: `supply-chain-vcn` (10.0.0.0/16)
- [ ] Create public subnet: `supply-chain-public-subnet` (10.0.1.0/24)
- [ ] Configure Internet Gateway and routing
- [ ] Set up security list rules (ports: 22, 8501, 7474, 7687)
- [ ] Provision VM instance (VM.Standard.E2.1.Micro for free tier)
 
### VM Configuration (20-30 minutes)
- [ ] SSH to instance: `ssh -i key opc@<PUBLIC_IP>`
- [ ] Update system: `sudo dnf update -y`
- [ ] Install Docker and Docker Compose
- [ ] Add user to docker group: `sudo usermod -aG docker opc`
- [ ] Install Git and Python tools
 
### Application Deployment (15-20 minutes)
- [ ] Clone/transfer application code
- [ ] Configure `.env` file with production settings
- [ ] Create `Dockerfile` and `docker-compose.prod.yml`
- [ ] Build and start services: `docker-compose up -d`
- [ ] Initialize databases with setup scripts
- [ ] Configure firewall: `sudo firewall-cmd --add-port=8501/tcp --permanent`
 
### Post-Deployment (10-15 minutes)
- [ ] Test application: `http://<PUBLIC_IP>:8501`
- [ ] Set up monitoring script
- [ ] Configure backup strategy
- [ ] Schedule automated backups
 
---
 
## 📋 Essential Commands
 
### Docker Management
```bash
# Start all services
docker-compose up -d
 
# Check service status
docker-compose ps
 
# View logs
docker-compose logs -f
 
# Restart specific service
docker-compose restart <service-name>
 
# Stop all services
docker-compose down
```
 
### System Monitoring
```bash
# Check system resources
htop
free -h
df -h
 
# Monitor Docker containers
docker stats
 
# Check application logs
tail -f logs/application.log
```
 
### Database Operations
```bash
# PostgreSQL
docker-compose exec postgres psql -U postgres -d postgres
 
# MongoDB
docker-compose exec mongodb mongosh
 
# Redis
docker-compose exec redis redis-cli
 
# Neo4j
docker-compose exec neo4j cypher-shell -u neo4j -p storechain123
```
 
---
 
## 🔧 Configuration Templates
 
### Minimal .env Configuration
```bash
# Database passwords
POSTGRES_PASSWORD=postgres123
MONGO_PASSWORD=admin123
REDIS_PASSWORD=redis123
NEO4J_PASSWORD=storechain123
 
# Application settings
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_PORT=8501
```
 
### Security List Rules (OCI Console)
```
Ingress Rules:
- SSH: 0.0.0.0/0, TCP, 22
- App: 0.0.0.0/0, TCP, 8501
- Neo4j HTTP: 0.0.0.0/0, TCP, 7474
- Neo4j Bolt: 0.0.0.0/0, TCP, 7687
```
 
---
 
## 🚨 Troubleshooting Quick Fixes
 
### Application Won't Start
```bash
# Check Docker daemon
sudo systemctl restart docker
 
# Check logs for errors
docker-compose logs app
 
# Rebuild and restart
docker-compose down
docker-compose up -d --build
```
 
### Database Connection Issues
```bash
# Wait for databases to initialize
sleep 30
 
# Check database health
docker-compose exec postgres pg_isready -U postgres
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```
 
### Port Access Issues
```bash
# Check firewall
sudo firewall-cmd --list-all
 
# Add missing ports
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```
 
### Memory Issues
```bash
# Free up memory
docker system prune -f
 
# Restart services
docker-compose restart
```
 
---
 
## 💰 Cost Monitoring
 
### Always Free Tier Limits
- **Compute**: 2 VM.Standard.E2.1.Micro instances
- **Storage**: 200 GB total block storage
- **Network**: 10 TB outbound data transfer per month
 
### Cost Optimization Commands
```bash
# Stop instance when not needed
# (In OCI Console: Compute > Instances > Stop)
 
# Monitor resource usage
docker stats --no-stream
 
# Clean up unused Docker resources
docker system prune -a
```
 
---
 
## 📞 Support Resources
 
- **OCI Documentation**: https://docs.oracle.com/en-us/iaas/
- **OCI Support**: https://support.oracle.com/
- **Community Forums**: https://community.oracle.com/
- **Docker Issues**: https://docs.docker.com/
 
---
 
## 🔄 Maintenance Schedule
 
### Daily (2 minutes)
```bash
# Quick health check
./monitor.sh
```
 
### Weekly (10 minutes)
```bash
# System updates
sudo dnf update -y
 
# Service restart
docker-compose restart
 
# Log review
tail -100 logs/application.log
```
 
### Monthly (30 minutes)
```bash
# Full backup verification
./backup.sh
 
# Security updates
sudo dnf update -y --security
 
# Performance review
docker stats --no-stream
```
 
This quick reference guide provides the essential information needed for day-to-day management of your Oracle Cloud deployment.
 