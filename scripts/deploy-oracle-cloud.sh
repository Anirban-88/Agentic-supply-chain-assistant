#!/bin/bash
 
# =============================================================================
# Oracle Cloud Deployment Script for Store Supply Chain Application
# =============================================================================
 
set -e  # Exit on any error
 
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
 
# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}
 
warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}
 
error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}
 
# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root for security reasons"
fi
 
log "🚀 Starting Oracle Cloud deployment for Store Supply Chain Application"
 
# =============================================================================
# SYSTEM PREPARATION
# =============================================================================
 
log "📦 Updating system packages..."
sudo dnf update -y
 
log "🔧 Installing required system packages..."
sudo dnf install -y \
    curl \
    wget \
    git \
    htop \
    nano \
    unzip \
    firewalld \
    python3 \
    python3-pip
 
# =============================================================================
# DOCKER INSTALLATION
# =============================================================================
 
log "🐳 Installing Docker..."
 
# Add Docker repository
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
 
# Install Docker
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
 
# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
 
# Add current user to docker group
sudo usermod -aG docker $USER
 
log "✅ Docker installed successfully"
 
# =============================================================================
# DOCKER COMPOSE INSTALLATION
# =============================================================================
 
log "📦 Installing Docker Compose..."
 
# Install Docker Compose
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
 
# Verify installation
docker --version
docker-compose --version
 
log "✅ Docker Compose installed successfully"
 
# =============================================================================
# FIREWALL CONFIGURATION
# =============================================================================
 
log "🔥 Configuring firewall..."
 
# Start and enable firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld
 
# Add required ports
sudo firewall-cmd --permanent --add-port=22/tcp      # SSH
sudo firewall-cmd --permanent --add-port=8501/tcp    # Streamlit
sudo firewall-cmd --permanent --add-port=7474/tcp    # Neo4j HTTP
sudo firewall-cmd --permanent --add-port=7687/tcp    # Neo4j Bolt
 
# Reload firewall
sudo firewall-cmd --reload
 
# Show current rules
sudo firewall-cmd --list-all
 
log "✅ Firewall configured successfully"
 
# =============================================================================
# APPLICATION SETUP
# =============================================================================
 
log "📁 Setting up application directory..."
 
# Create application directory
APP_DIR="/home/$USER/store_supply_chain"
if [ ! -d "$APP_DIR" ]; then
    mkdir -p "$APP_DIR"
fi
 
cd "$APP_DIR"
 
# Create necessary directories
mkdir -p logs backups data
 
log "✅ Application directory setup complete"
 
# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================
 
log "⚙️ Setting up environment configuration..."
 
# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.prod" ]; then
        cp .env.prod .env
        log "📝 Created .env file from .env.prod template"
        warn "Please edit .env file with your specific configuration"
    else
        warn ".env.prod template not found. You'll need to create .env manually"
    fi
fi
 
log "✅ Environment configuration ready"
 
# =============================================================================
# DOCKER NETWORK SETUP
# =============================================================================
 
log "🌐 Setting up Docker network..."
 
# Create custom network if it doesn't exist
if ! docker network ls | grep -q "store_network"; then
    docker network create store_network
    log "✅ Created Docker network: store_network"
else
    log "ℹ️ Docker network 'store_network' already exists"
fi
 
# =============================================================================
# SYSTEM OPTIMIZATION
# =============================================================================
 
log "⚡ Applying system optimizations..."
 
# Increase file limits for databases
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
 
# Optimize kernel parameters for databases
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
echo "net.core.somaxconn=65535" | sudo tee -a /etc/sysctl.conf
 
# Apply sysctl changes
sudo sysctl -p
 
log "✅ System optimizations applied"
 
# =============================================================================
# MONITORING SETUP
# =============================================================================
 
log "📊 Setting up monitoring..."
 
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
# System and Application Monitoring Script
 
echo "=== Store Supply Chain Application Health Check ==="
echo "Date: $(date)"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime)"
echo
 
echo "=== Docker Services Status ==="
docker-compose -f docker-compose.prod.yml ps
echo
 
echo "=== System Resources ==="
echo "Memory Usage:"
free -h
echo
echo "Disk Usage:"
df -h
echo
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2 $3 $4 $5 $6 $7 $8}'
echo
 
echo "=== Network Connectivity ==="
echo "Checking application ports..."
netstat -tlnp | grep -E ':(8501|7474|7687|5432|27017|6379)'
echo
 
echo "=== Application Logs (last 10 lines) ==="
if [ -f "logs/application.log" ]; then
    tail -10 logs/application.log
else
    echo "Application log not found"
fi
echo
 
echo "=== Database Health Checks ==="
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "PostgreSQL:" $(docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U postgres 2>/dev/null || echo "Not ready")
    echo "MongoDB:" $(docker-compose -f docker-compose.prod.yml exec -T mongodb mongosh --eval "db.adminCommand('ping')" --quiet 2>/dev/null || echo "Not ready")
    echo "Redis:" $(docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping 2>/dev/null || echo "Not ready")
    echo "Neo4j:" $(docker-compose -f docker-compose.prod.yml exec -T neo4j cypher-shell -u neo4j -p storechain123 "RETURN 1" 2>/dev/null | grep -q "1" && echo "PONG" || echo "Not ready")
else
    echo "Services not running"
fi
 
echo
echo "=== Health Check Complete ==="
EOF
 
chmod +x monitor.sh
 
log "✅ Monitoring script created"
 
# =============================================================================
# BACKUP SETUP
# =============================================================================
 
log "💾 Setting up backup system..."
 
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
# Database Backup Script for Store Supply Chain Application
 
set -e
 
BACKUP_DIR="/home/$USER/backups"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$BACKUP_DIR/backup_$DATE.log"
 
# Create backup directory
mkdir -p $BACKUP_DIR
 
echo "Starting backup at $(date)" | tee $LOG_FILE
 
# Function to log messages
log_backup() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}
 
# PostgreSQL backup
log_backup "Backing up PostgreSQL..."
if docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U postgres postgres > $BACKUP_DIR/postgres_$DATE.sql 2>>$LOG_FILE; then
    log_backup "PostgreSQL backup completed successfully"
else
    log_backup "PostgreSQL backup failed"
fi
 
# MongoDB backup
log_backup "Backing up MongoDB..."
if docker-compose -f docker-compose.prod.yml exec -T mongodb mongodump --archive > $BACKUP_DIR/mongodb_$DATE.archive 2>>$LOG_FILE; then
    log_backup "MongoDB backup completed successfully"
else
    log_backup "MongoDB backup failed"
fi
 
# Neo4j backup
log_backup "Backing up Neo4j..."
if docker-compose -f docker-compose.prod.yml exec -T neo4j neo4j-admin database dump neo4j --to-path=/tmp/ 2>>$LOG_FILE; then
    docker cp $(docker-compose -f docker-compose.prod.yml ps -q neo4j):/tmp/neo4j.dump $BACKUP_DIR/neo4j_$DATE.dump 2>>$LOG_FILE
    log_backup "Neo4j backup completed successfully"
else
    log_backup "Neo4j backup failed"
fi
 
# Redis backup
log_backup "Backing up Redis..."
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli --rdb /tmp/dump.rdb 2>>$LOG_FILE; then
    docker cp $(docker-compose -f docker-compose.prod.yml ps -q redis):/tmp/dump.rdb $BACKUP_DIR/redis_$DATE.rdb 2>>$LOG_FILE
    log_backup "Redis backup completed successfully"
else
    log_backup "Redis backup failed"
fi
 
# Application data backup
log_backup "Backing up application data..."
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz logs synthetic_data 2>>$LOG_FILE
log_backup "Application data backup completed"
 
# Cleanup old backups (keep last 7 days)
log_backup "Cleaning up old backups..."
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete 2>>$LOG_FILE
find $BACKUP_DIR -name "*.archive" -mtime +7 -delete 2>>$LOG_FILE
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete 2>>$LOG_FILE
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete 2>>$LOG_FILE
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete 2>>$LOG_FILE
find $BACKUP_DIR -name "*.log" -mtime +30 -delete 2>>$LOG_FILE
 
log_backup "Backup process completed at $(date)"
 
# Display backup summary
echo
echo "=== Backup Summary ==="
ls -lh $BACKUP_DIR/*_$DATE.* 2>/dev/null || echo "No backup files created"
echo
echo "Total backup directory size: $(du -sh $BACKUP_DIR | cut -f1)"
EOF
 
chmod +x backup.sh
 
log "✅ Backup script created"
 
# =============================================================================
# CRON JOBS SETUP
# =============================================================================
 
log "⏰ Setting up automated tasks..."
 
# Add cron jobs for monitoring and backup
(crontab -l 2>/dev/null; echo "# Store Supply Chain Application Tasks") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * * cd $APP_DIR && ./backup.sh >> $APP_DIR/logs/backup.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "*/30 * * * * cd $APP_DIR && ./monitor.sh >> $APP_DIR/logs/monitor.log 2>&1") | crontab -
 
log "✅ Automated tasks configured"
 
# =============================================================================
# COMPLETION
# =============================================================================
 
log "🎉 Oracle Cloud deployment setup completed successfully!"
echo
echo "=== Next Steps ==="
echo "1. Edit the .env file with your specific configuration"
echo "2. Transfer your application code to: $APP_DIR"
echo "3. Run: docker-compose -f docker-compose.prod.yml up -d"
echo "4. Initialize databases with setup scripts"
echo "5. Test the application at: http://$(curl -s ifconfig.me):8501"
echo
echo "=== Useful Commands ==="
echo "• Start services: docker-compose -f docker-compose.prod.yml up -d"
echo "• Stop services: docker-compose -f docker-compose.prod.yml down"
echo "• View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "• Check status: docker-compose -f docker-compose.prod.yml ps"
echo "• Run monitoring: ./monitor.sh"
echo "• Run backup: ./backup.sh"
echo
warn "Please reboot the system or log out and back in for Docker group changes to take effect"
echo
 
log "✅ Deployment script completed successfully!"
 
deploy-oracle-cloud.sh
 