# Oracle Cloud Infrastructure Deployment Plan
## Store Supply Chain Multi-Agent System
 
### 📋 Overview
 
This document provides a comprehensive deployment plan for deploying the Store Supply Chain Multi-Agent System on Oracle Cloud Infrastructure (OCI) using a single Virtual Machine approach optimized for development/testing environments.
 
### 🏗️ Application Architecture Summary
 
Your application consists of:
- **Frontend**: Streamlit web application (Port 8501)
- **Backend**: Python-based multi-agent system with orchestrator
- **Databases**:
  - PostgreSQL (Port 5432) - Structured data
  - MongoDB (Port 27017) - Real-time data  
  - Redis (Port 6379) - Caching and expiry tracking
  - Neo4j (Port 7474/7687) - Knowledge graph
- **AI/ML**: Llama 3.2-1B model for natural language processing
 
### 🎯 Deployment Strategy
 
**Approach**: Single VM deployment with Docker Compose
**Environment**: Development/Testing
**Cost Optimization**: Always Free Tier eligible where possible
 
---
 
## 📝 Detailed Deployment Steps
 
### Step 1: Oracle Cloud Infrastructure Account Setup
 
#### 1.1 Create OCI Account
- Sign up at [cloud.oracle.com](https://cloud.oracle.com)
- Complete identity verification
- Set up billing information (Free Tier available)
- Choose your home region (recommend closest to your location)
 
#### 1.2 Initial Configuration
- Access OCI Console
- Create a compartment for your project:
  - Name: `supply-chain-dev`
  - Description: `Development environment for supply chain application`
- Note down your tenancy OCID and user OCID
 
### Step 2: Virtual Cloud Network (VCN) Setup
 
#### 2.1 Create VCN
```bash
# VCN Configuration
Name: supply-chain-vcn
CIDR Block: 10.0.0.0/16
DNS Resolution: Enabled
DNS Label: supplychain
```
 
#### 2.2 Create Subnet
```bash
# Public Subnet Configuration
Name: supply-chain-public-subnet
CIDR Block: 10.0.1.0/24
Subnet Type: Public
Route Table: Default Route Table
Security List: Default Security List
```
 
#### 2.3 Configure Internet Gateway
- Create Internet Gateway: `supply-chain-igw`
- Add route rule in Default Route Table:
  - Destination CIDR: `0.0.0.0/0`
  - Target: Internet Gateway
 
### Step 3: Security Configuration
 
#### 3.1 Security List Rules (Ingress)
Add the following ingress rules to Default Security List:
 
```bash
# SSH Access
Source: 0.0.0.0/0
Protocol: TCP
Port: 22
 
# Streamlit Application
Source: 0.0.0.0/0
Protocol: TCP
Port: 8501
 
# Neo4j HTTP Interface
Source: 0.0.0.0/0
Protocol: TCP
Port: 7474
 
# Neo4j Bolt Protocol
Source: 0.0.0.0/0
Protocol: TCP
Port: 7687
 
# PostgreSQL (if external access needed)
Source: 10.0.0.0/16
Protocol: TCP
Port: 5432
 
# MongoDB (if external access needed)
Source: 10.0.0.0/16
Protocol: TCP
Port: 27017
 
# Redis (if external access needed)
Source: 10.0.0.0/16
Protocol: TCP
Port: 6379
```
 
### Step 4: Compute Instance Provisioning
 
#### 4.1 Instance Specifications
```bash
# Recommended Configuration for Development
Shape: VM.Standard.E2.1.Micro (Always Free eligible)
- 1 OCPU
- 1 GB RAM
- 1 Gbps network bandwidth
 
# Alternative if more resources needed
Shape: VM.Standard2.1
- 1 OCPU  
- 15 GB RAM
- 1 Gbps network bandwidth
```
 
#### 4.2 Instance Configuration
```bash
Name: supply-chain-vm
Image: Oracle Linux 8
Boot Volume: 50 GB (Always Free: up to 200 GB total)
VCN: supply-chain-vcn
Subnet: supply-chain-public-subnet
Assign Public IP: Yes
SSH Key: Upload your public key or generate new key pair
```
 
#### 4.3 Create Instance
- Navigate to Compute > Instances
- Click "Create Instance"
- Configure as specified above
- Save private key securely
- Wait for instance to reach "Running" state
 
### Step 5: VM Initial Setup
 
#### 5.1 Connect to Instance
```bash
# SSH to your instance
ssh -i /path/to/private-key opc@<PUBLIC_IP>
 
# Update system
sudo dnf update -y
```
 
#### 5.2 Install Docker
```bash
# Install Docker
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io
 
# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
 
# Add user to docker group
sudo usermod -aG docker opc
newgrp docker
 
# Verify installation
docker --version
```
 
#### 5.3 Install Docker Compose
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
 
# Verify installation
docker-compose --version
```
 
#### 5.4 Install Additional Tools
```bash
# Install Git, Python, and other utilities
sudo dnf install -y git python3 python3-pip htop nano wget curl
 
# Install Python dependencies for local development (optional)
pip3 install --user python-dotenv
```
 
### Step 6: Application Deployment
 
#### 6.1 Transfer Application Code
```bash
# Option 1: Using Git (recommended)
git clone <your-repository-url>
cd store_supply_chain
 
# Option 2: Using SCP
# From your local machine:
scp -i /path/to/private-key -r /path/to/store_supply_chain opc@<PUBLIC_IP>:~/
```
 
#### 6.2 Configure Environment Variables
```bash
# Create production environment file
cp .env.example .env
 
# Edit environment variables
nano .env
```
 
**Required Environment Variables:**
```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
 
MONGO_USERNAME=admin
MONGO_PASSWORD=admin123
MONGO_HOST=mongodb
MONGO_PORT=27017
 
REDIS_PASSWORD=redis123
REDIS_HOST=redis
REDIS_PORT=6379
 
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=storechain123
 
# Application Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
 
# LLM Configuration
MODEL_NAME=meta-llama/Llama-3.2-1B
DEVICE=cpu
MAX_LENGTH=512
```
 
#### 6.3 Configure Docker Compose for Production
Create a production override file:
 
```bash
# Create docker-compose.prod.yml
nano docker-compose.prod.yml
```
 
```yaml
version: '3.8'
 
services:
  # Add application service
  app:
    build: .
    container_name: supply_chain_app
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_PORT=8501
    depends_on:
      - postgres
      - mongodb
      - redis
      - neo4j
    networks:
      - store_network
    volumes:
      - ./logs:/app/logs
      - ./synthetic_data:/app/synthetic_data
    restart: unless-stopped
 
  # Override database configurations for production
  postgres:
    restart: unless-stopped
    
  mongodb:
    restart: unless-stopped
    
  redis:
    restart: unless-stopped
    
  neo4j:
    restart: unless-stopped
```
 
#### 6.4 Create Dockerfile
```bash
# Create Dockerfile
nano Dockerfile
```
 
```dockerfile
FROM python:3.11-slim
 
WORKDIR /app
 
# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*
 
# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy application code
COPY . .
 
# Create logs directory
RUN mkdir -p logs
 
# Expose port
EXPOSE 8501
 
# Run the application
CMD ["python", "main.py"]
```
 
### Step 7: Deploy Application
 
#### 7.1 Build and Start Services
```bash
# Build and start all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
 
# Check service status
docker-compose ps
 
# View logs
docker-compose logs -f
```
 
#### 7.2 Initialize Databases
```bash
# Wait for databases to be ready, then run setup scripts
sleep 30
 
# Run database setup scripts
docker-compose exec app python scripts/02_setup_postgresql.py
docker-compose exec app python scripts/03_setup_mongodb.py
docker-compose exec app python scripts/06_create_knowledge_graph.py
docker-compose exec app python scripts/09_setup_redis.py
```
 
### Step 8: Configure Firewall (Oracle Linux)
 
```bash
# Configure firewall for application ports
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --permanent --add-port=7474/tcp
sudo firewall-cmd --permanent --add-port=7687/tcp
sudo firewall-cmd --reload
 
# Verify firewall rules
sudo firewall-cmd --list-all
```
 
### Step 9: Monitoring and Logging
 
#### 9.1 Set Up Log Rotation
```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/supply-chain
```
 
```bash
/home/opc/store_supply_chain/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 opc opc
}
```
 
#### 9.2 Create Monitoring Script
```bash
# Create monitoring script
nano monitor.sh
chmod +x monitor.sh
```
 
```bash
#!/bin/bash
# monitor.sh - Basic health check script
 
echo "=== Supply Chain Application Health Check ==="
echo "Date: $(date)"
echo
 
echo "Docker Services Status:"
docker-compose ps
 
echo -e "\nDisk Usage:"
df -h
 
echo -e "\nMemory Usage:"
free -h
 
echo -e "\nApplication Logs (last 10 lines):"
docker-compose logs --tail=10 app
 
echo -e "\nDatabase Connection Test:"
docker-compose exec -T postgres pg_isready -U postgres
docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" --quiet
docker-compose exec -T redis redis-cli ping
docker-compose exec -T neo4j cypher-shell -u neo4j -p storechain123 "RETURN 1"
```
 
### Step 10: Backup Strategy
 
#### 10.1 Database Backup Script
```bash
# Create backup script
nano backup.sh
chmod +x backup.sh
```
 
```bash
#!/bin/bash
# backup.sh - Database backup script
 
BACKUP_DIR="/home/opc/backups"
DATE=$(date +%Y%m%d_%H%M%S)
 
mkdir -p $BACKUP_DIR
 
echo "Starting backup at $(date)"
 
# PostgreSQL backup
docker-compose exec -T postgres pg_dump -U postgres postgres > $BACKUP_DIR/postgres_$DATE.sql
 
# MongoDB backup
docker-compose exec -T mongodb mongodump --archive > $BACKUP_DIR/mongodb_$DATE.archive
 
# Neo4j backup
docker-compose exec -T neo4j neo4j-admin database dump neo4j --to-path=/tmp/
docker cp $(docker-compose ps -q neo4j):/tmp/neo4j.dump $BACKUP_DIR/neo4j_$DATE.dump
 
# Redis backup
docker-compose exec -T redis redis-cli --rdb /tmp/dump.rdb
docker cp $(docker-compose ps -q redis):/tmp/dump.rdb $BACKUP_DIR/redis_$DATE.rdb
 
# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.archive" -mtime +7 -delete
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete
 
echo "Backup completed at $(date)"
```
 
#### 10.2 Schedule Backups
```bash
# Add to crontab
crontab -e
 
# Add this line for daily backups at 2 AM
0 2 * * * /home/opc/store_supply_chain/backup.sh >> /home/opc/backup.log 2>&1
```
 
### Step 11: SSL Certificate Setup (Optional)
 
#### 11.1 Install Certbot
```bash
# Install certbot for Let's Encrypt SSL
sudo dnf install -y certbot
 
# If you have a domain name, get SSL certificate
sudo certbot certonly --standalone -d your-domain.com
```
 
#### 11.2 Configure Nginx Reverse Proxy (Optional)
```bash
# Install Nginx
sudo dnf install -y nginx
 
# Configure Nginx
sudo nano /etc/nginx/conf.d/supply-chain.conf
```
 
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
 
server {
    listen 443 ssl;
    server_name your-domain.com;
 
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
 
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
 
### Step 12: Testing and Verification
 
#### 12.1 Application Testing
```bash
# Test application endpoints
curl -I http://<PUBLIC_IP>:8501
 
# Test Neo4j connection
curl -I http://<PUBLIC_IP>:7474
 
# Run application tests
docker-compose exec app python scripts/11_test_agents.py
```
 
#### 12.2 Performance Testing
```bash
# Monitor resource usage
htop
 
# Check Docker stats
docker stats
 
# Test database connections
docker-compose exec app python scripts/04_verify_setup.py
```
 
---
 
## 🔧 Maintenance Procedures
 
### Daily Tasks
- Check application logs: `docker-compose logs --tail=50`
- Monitor disk space: `df -h`
- Verify all services running: `docker-compose ps`
 
### Weekly Tasks
- Review backup logs
- Update system packages: `sudo dnf update -y`
- Restart services if needed: `docker-compose restart`
 
### Monthly Tasks
- Review and rotate logs
- Update Docker images: `docker-compose pull && docker-compose up -d`
- Security updates and patches
 
---
 
## 💰 Cost Optimization Tips
 
1. **Use Always Free Tier**: VM.Standard.E2.1.Micro is always free
2. **Monitor Usage**: Set up billing alerts in OCI console
3. **Stop When Not Needed**: Stop instance during non-working hours
4. **Optimize Images**: Use multi-stage Docker builds to reduce image size
5. **Resource Monitoring**: Use OCI monitoring to track resource usage
 
---
 
## 🚨 Troubleshooting Guide
 
### Common Issues
 
#### Services Not Starting
```bash
# Check Docker daemon
sudo systemctl status docker
 
# Check logs
docker-compose logs <service-name>
 
# Restart services
docker-compose restart
```
 
#### Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready -U postgres
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
docker-compose exec redis redis-cli ping
docker-compose exec neo4j cypher-shell -u neo4j -p storechain123 "RETURN 1"
```
 
#### Memory Issues
```bash
# Check memory usage
free -h
docker stats
 
# Restart services to free memory
docker-compose restart
```
 
#### Port Access Issues
```bash
# Check if ports are open
sudo netstat -tlnp | grep :8501
sudo firewall-cmd --list-all
 
# Test connectivity
telnet <PUBLIC_IP> 8501
```
 
---
 
## 📚 Additional Resources
 
- [Oracle Cloud Infrastructure Documentation](https://docs.oracle.com/en-us/iaas/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Streamlit Deployment Guide](https://docs.streamlit.io/knowledge-base/deploy)
- [Neo4j Operations Manual](https://neo4j.com/docs/operations-manual/)
 
---
 
## 🔐 Security Best Practices
 
1. **Regular Updates**: Keep OS and packages updated
2. **Strong Passwords**: Use complex passwords for all services
3. **Firewall Rules**: Restrict access to necessary ports only
4. **SSH Keys**: Use SSH keys instead of passwords
5. **Backup Encryption**: Encrypt sensitive backup data
6. **Access Logging**: Monitor access logs regularly
7. **Network Security**: Use VCN security lists effectively
 
---
 
This deployment plan provides a comprehensive pathway to deploy your Store Supply Chain Multi-Agent System on Oracle Cloud Infrastructure with proper security, monitoring, and maintenance procedures.
 