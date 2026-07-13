#!/usr/bin/env bash
set -euo pipefail

# Wargear production setup script
# Run from anywhere. Must be run as root (or with sudo).
#
# Usage:  REPO_URL=https://github.com/you/wargear.git DOMAIN=wargear.example.com ./deploy/setup.sh
#
# If REPO_URL is not set and /opt/wargear doesn't exist, the script will prompt for it.
# If DOMAIN is not set, the script will prompt for it.

APP_ROOT="/home/ubuntu/warband-creator"
CADDY_ROOT="/home/ubuntu/caddy"
ENV_FILE="$APP_ROOT/.env"
CADDYFILE="$APP_ROOT/deploy/caddy/Caddyfile"
CADDY_COMPOSE_ROOT="$APP_ROOT/deploy/caddy"

# ---- helpers ----

echo_step() { echo -e "\n\033[1;34m==>\033[0m $1"; }
echo_ok()   { echo -e "\033[32m  OK:\033[0m $1"; }
echo_warn() { echo -e "\033[33m  WARN:\033[0m $1"; }
gen_secret() { python3 -c "import secrets; print(secrets.token_hex(32))"; }

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || { echo "ERROR: '$1' is required but not installed." >&2; exit 1; }
}

# ---- pre-flight checks ----

echo_step "Checking prerequisites"
require_cmd docker
require_cmd python3
require_cmd git

# ---- step 3: clone repo ----

if [ ! -d "$APP_ROOT" ]; then
    if [ -z "${REPO_URL:-}" ]; then
        read -r -p "  Git repo URL: " REPO_URL
    fi
    if [ -z "$REPO_URL" ]; then
        echo "ERROR: REPO_URL is required." >&2
        exit 1
    fi

    echo_step "Cloning repository"
    git clone "$REPO_URL" "$APP_ROOT"
    echo_ok "Cloned to $APP_ROOT"
else
    echo_ok "$APP_ROOT already exists — pulling latest"
    cd "$APP_ROOT"
    git pull --ff-only 2>/dev/null || echo_warn "Could not pull (detached HEAD or local changes)"
fi

# ---- step 4: .env ----

echo_step "Setting up environment file"

if [ -f "$ENV_FILE" ]; then
    echo_warn ".env already exists at $ENV_FILE — skipping generation"
else
    # Domain
    if [ -z "${DOMAIN:-}" ]; then
        read -r -p "  Domain (e.g. wargear.example.com): " DOMAIN
    fi
    if [ -z "$DOMAIN" ]; then
        echo "ERROR: DOMAIN is required." >&2
        exit 1
    fi

    DB_PASSWORD=$(gen_secret)

    cat > "$ENV_FILE" <<EOF
# Django
DEBUG=0
SECRET_KEY=$(gen_secret)
ALLOWED_HOSTS=$DOMAIN

# PostgreSQL
POSTGRES_DB=wargear
POSTGRES_USER=wargear
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_HOST=db
POSTGRES_PORT=5432
EOF

    chmod 600 "$ENV_FILE"
    echo_ok "Created $ENV_FILE"
fi

# Read domain from .env for Caddyfile
DOMAIN=$(grep -E '^ALLOWED_HOSTS=' "$ENV_FILE" | cut -d= -f2 | awk '{print $1}')
if [ -z "$DOMAIN" ]; then
    echo "ERROR: Could not read domain from ALLOWED_HOSTS in .env" >&2
    exit 1
fi

# ---- step 5: Caddyfile ----

echo_step "Configuring Caddyfile with domain: $DOMAIN"
cat > "$CADDYFILE" <<EOF
# Change this to your real domain. For multiple domains use commas:
#   yourdomain.com, www.yourdomain.com { ... }
#
# After editing, reload with: make caddy-reload
$DOMAIN {
    reverse_proxy wargear-web-1:8000
}
EOF
echo_ok "Caddyfile written"

# ---- Caddy directory (step 3 continued) ----

if [ ! -L "$CADDY_ROOT" ]; then
    echo_step "Linking Caddy configuration"
    ln -sf "$CADDY_COMPOSE_ROOT" "$CADDY_ROOT"
    echo_ok "$CADDY_ROOT -> $CADDY_COMPOSE_ROOT"
else
    echo_ok "$CADDY_ROOT already linked"
fi

# ---- step 6: systemd units ----

echo_step "Installing systemd units"
cp "$APP_ROOT/deploy/wargear.service" /etc/systemd/system/
cp "$APP_ROOT/deploy/caddy.service"   /etc/systemd/system/
systemctl daemon-reload
echo_ok "Units installed"

# ---- firewall ----

echo_step "Configuring firewall"
if command -v ufw >/dev/null 2>&1; then
    ufw allow 22/tcp   >/dev/null 2>&1 || true   # SSH
    ufw allow 80/tcp   >/dev/null 2>&1 || true   # HTTP
    ufw allow 443/tcp  >/dev/null 2>&1 || true   # HTTPS
    ufw --force enable >/dev/null 2>&1 || true
    echo_ok "ufw: allowed ports 22, 80, 443"
else
    echo_warn "ufw not found — skipping firewall. Allow ports 22, 80, 443 manually."
fi

# ---- shared network ----

if ! docker network inspect shared >/dev/null 2>&1; then
    echo_step "Creating shared Docker network"
    docker network create shared
else
    echo_ok "shared network exists"
fi

# ---- step 7: start services ----

echo_step "Building and starting services"
cd "$APP_ROOT"
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
echo_ok "Containers started"

# Wait for web container to be ready
echo_step "Waiting for web container..."
for i in $(seq 1 30); do
    if docker compose -f "$APP_ROOT/docker-compose.yml" -f "$APP_ROOT/docker-compose.prod.yml" exec -T web curl -sf http://localhost:8000/weapons/ >/dev/null 2>&1; then
        echo_ok "web container ready"
        break
    fi
    echo "  waiting... ($i/30)"
    sleep 2
done

systemctl enable caddy   >/dev/null 2>&1 || true
systemctl enable wargear >/dev/null 2>&1 || true
echo_ok "Systemd units enabled for auto-start on boot"

# ---- step 8: migrations ----

echo_step "Running database migrations"
docker compose -f "$APP_ROOT/docker-compose.yml" -f "$APP_ROOT/docker-compose.prod.yml" exec -T web poetry run python manage.py migrate --noinput
echo_ok "Migrations complete"

# ---- step 9: superuser ----

echo_step "Creating superuser"
echo "  Enter credentials for the admin user at https://$DOMAIN/admin/"
docker compose -f "$APP_ROOT/docker-compose.yml" -f "$APP_ROOT/docker-compose.prod.yml" exec -it web poetry run python manage.py createsuperuser || echo_warn "Superuser creation skipped (Ctrl+C to skip)"

# ---- step 10: backup cron ----

echo_step "Setting up daily database backup"

BACKUP_SCRIPT="/usr/local/bin/wargear-backup"
cat > "$BACKUP_SCRIPT" <<'SCRIPT'
#!/usr/bin/env bash
set -e
cd /opt/wargear
mkdir -p /opt/wargear/backups
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db pg_dump -U wargear wargear | gzip > /opt/wargear/backups/wargear-$(date +%Y%m%d).sql.gz
find /opt/wargear/backups -name '*.sql.gz' -mtime +30 -delete
SCRIPT
chmod +x "$BACKUP_SCRIPT"

if ! crontab -l 2>/dev/null | grep -q 'wargear-backup'; then
    (crontab -l 2>/dev/null || true; echo "0 3 * * * $BACKUP_SCRIPT") | crontab -
    echo_ok "Cron job installed (runs daily at 3 AM, keeps 30 days in /opt/wargear/backups/)"
else
    echo_ok "Cron job already exists"
fi

# ---- done ----

echo -e "\n\033[1;32mSetup complete!\033[0m"
echo "  Site:     https://$DOMAIN"
echo "  Admin:    https://$DOMAIN/admin"
echo "  Logs:     journalctl -fu wargear"
echo "  Backups:  $APP_ROOT/backups/"
