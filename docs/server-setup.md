# Server Setup Guide

## Prerequisites

Start with a fresh Ubuntu server with a domain name pointed to it.

## 1. Install dependencies on the server

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git python3 ufw curl
sudo usermod -aG docker $USER
```

Log out and back in for the docker group to take effect.

## 2. Push the repo to a git remote

The setup script clones from a git URL, so the repo must be available at a remote.

## 3. Run the setup script

```bash
git clone <your-repo-url> /opt/wargear
REPO_URL=<your-repo-url> DOMAIN=deadlight.systems sudo bash /opt/wargear/deploy/setup.sh
```

The script (`deploy/setup.sh`) handles everything automatically:

- Generates a `.env` file with secure random secrets
- Writes a Caddyfile configured for your domain
- Configures Caddy as a reverse proxy (auto-HTTPS via Let's Encrypt)
- Installs systemd units so services start on boot
- Opens firewall ports 22, 80, 443
- Builds and starts the production Docker Compose stack
- Runs database migrations and prompts for a Django superuser
- Sets up a daily cron job for database backups (3 AM, retains 30 days)

## 4. Done

The app will be live at:
- **Site:** `https://deadlight.systems`
- **Admin:** `https://deadlight.systems/admin`

## Ongoing management

```bash
# Watch logs
docker compose -f /opt/wargear/docker-compose.yml -f /opt/wargear/docker-compose.prod.yml logs -f

# Restart the app
sudo systemctl restart wargear

# Manual database backup
make -C /opt/wargear backup-db

# Reload Caddy after config changes
make -C /opt/wargear caddy-reload

# Check service status
sudo systemctl status wargear caddy
```
