#!/bin/bash
# =============================================================================
# PyService Mini-ITSM Platform - Docker Entrypoint Script
# Handles database migrations, static files, and application startup
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        PyService Mini-ITSM Platform - Starting...        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"

# =============================================================================
# Wait for Database
# =============================================================================
wait_for_db() {
    echo -e "${YELLOW}⏳ Waiting for database...${NC}"
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if python -c "
import django
django.setup()
from django.db import connection
connection.ensure_connection()
" 2>/dev/null; then
            echo -e "${GREEN}✅ Database is ready!${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}   Attempt $attempt/$max_attempts - Database not ready, waiting...${NC}"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ Database connection failed after $max_attempts attempts${NC}"
    exit 1
}

# =============================================================================
# Wait for Redis
# =============================================================================
wait_for_redis() {
    echo -e "${YELLOW}⏳ Waiting for Redis...${NC}"
    
    max_attempts=15
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379} 2>/dev/null; then
            echo -e "${GREEN}✅ Redis is ready!${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}   Attempt $attempt/$max_attempts - Redis not ready, waiting...${NC}"
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ Redis connection failed after $max_attempts attempts${NC}"
    exit 1
}

# =============================================================================
# Run Migrations
# =============================================================================
run_migrations() {
    echo -e "${YELLOW}📦 Running database migrations...${NC}"
    python manage.py migrate --noinput
    echo -e "${GREEN}✅ Migrations completed!${NC}"
}

# =============================================================================
# Collect Static Files
# =============================================================================
collect_static() {
    echo -e "${YELLOW}📁 Collecting static files...${NC}"
    python manage.py collectstatic --noinput --clear
    echo -e "${GREEN}✅ Static files collected!${NC}"
}

# =============================================================================
# Create Superuser if not exists
# =============================================================================
create_superuser() {
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        echo -e "${YELLOW}👤 Creating superuser if not exists...${NC}"
        python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created!')
else:
    print('Superuser already exists.')
"
        echo -e "${GREEN}✅ Superuser check completed!${NC}"
    fi
}

# =============================================================================
# Setup Elasticsearch Indices
# =============================================================================
setup_elasticsearch() {
    if [ "$ELASTICSEARCH_ENABLED" = "true" ]; then
        echo -e "${YELLOW}🔍 Setting up Elasticsearch indices...${NC}"
        python manage.py search_index --rebuild -f 2>/dev/null || echo "Elasticsearch indices not configured"
        echo -e "${GREEN}✅ Elasticsearch setup completed!${NC}"
    fi
}

# =============================================================================
# Main Execution
# =============================================================================
main() {
    # Set Django settings module
    export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-pyservice.settings}
    
    # Wait for services
    wait_for_db
    wait_for_redis
    
    # Run setup tasks
    run_migrations
    collect_static
    create_superuser
    setup_elasticsearch
    
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           🚀 PyService is ready to serve!                ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    
    # Execute the main command
    exec "$@"
}

# Run main function
main "$@"
