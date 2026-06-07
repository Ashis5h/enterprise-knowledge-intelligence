# AWS Deployment Guide

## Architecture

```
Browser
  |
  v
EC2 Public IP
  |
  +--> Nginx (port 80)
        |
        +--> React Frontend (port 5173 -> 80)
        +--> FastAPI Backend (port 8000)
              |
              +--> PostgreSQL (Docker, port 5432)
              +--> Pinecone (cloud, no local setup needed)
              +--> Ollama (port 11434, runs on same EC2)
```

## Step 1: Create AWS Account

1. Go to https://aws.amazon.com and click "Create an AWS Account"
2. Enter email, password, account name
3. Enter credit card (you won't be charged if you use free tier)
4. Verify phone number
5. Choose "Basic support" (free)
6. Sign in to AWS Console at https://console.aws.amazon.com

## Step 2: Launch EC2 Instance

1. In AWS Console, search for "EC2" and click it
2. Click "Launch Instance"
3. Fill in:
   - Name: `enterprise-knowledge-platform`
   - AMI: `Ubuntu Server 22.04 LTS` (Free tier eligible)
   - Instance type: `t3.medium` (2 vCPU, 4GB RAM — needed for Ollama)
   - Key pair: Click "Create new key pair"
     - Name: `eki-key`
     - Type: RSA
     - Format: .pem
     - Click "Create key pair" — it will download `eki-key.pem` automatically
   - Network settings: Click "Edit"
     - Add inbound rules:
       | Type | Port | Source |
       |------|------|--------|
       | SSH | 22 | My IP |
       | Custom TCP | 8000 | Anywhere |
       | Custom TCP | 5173 | Anywhere |
       | Custom TCP | 80 | Anywhere |
   - Storage: Change to `30 GB`
4. Click "Launch Instance"
5. Note the Public IPv4 address (e.g. `13.233.xx.xx`)

## Step 3: Connect to EC2

Move the downloaded key file to a safe location, then:

```powershell
# Windows PowerShell
$env:KEY = "C:\path\to\eki-key.pem"
ssh -i $env:KEY ubuntu@<EC2_PUBLIC_IP>
```

If you get a permissions error on Windows:
```powershell
icacls "C:\path\to\eki-key.pem" /inheritance:r /grant:r "$($env:USERNAME):(R)"
```

## Step 4: Install Dependencies on EC2

Once SSH'd into the EC2 instance, run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose-plugin git curl
sudo usermod -aG docker ubuntu
newgrp docker

# Verify
docker --version
docker compose version

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model (runs in background)
ollama pull llama3.2 &

# Verify Ollama
ollama list
```

## Step 5: Upload Project to EC2

**Option A: Git (recommended)**
```bash
# On EC2
git clone https://github.com/<your-username>/enterprise-knowledge-intelligence.git
cd enterprise-knowledge-intelligence
```

**Option B: SCP from your Windows machine**
```powershell
# On your local machine (PowerShell)
scp -i "C:\path\to\eki-key.pem" -r "E:\Enterprise Knowledge Intelligence" ubuntu@<EC2_PUBLIC_IP>:~/enterprise-knowledge-intelligence
```

## Step 6: Configure Environment on EC2

```bash
cd enterprise-knowledge-intelligence/backend
cp .env.example .env
nano .env
```

Set these values:
```env
ENVIRONMENT=production
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
VECTOR_DB_PROVIDER=pinecone
PINECONE_API_KEY=pcsk_ZiZVQ_9k1yCX2YD4xkGnxX8qzj7qTojquVGcxJaBjnzRTjrAUUpsVjjgDxd5yGHLPkWne
PINECONE_INDEX_NAME=enterprise-knowledge
PINECONE_NAMESPACE=enterprise-documents
PINECONE_CREATE_INDEX=false
JWT_SECRET_KEY=<generate a long random string>
```

Generate a strong JWT secret:
```bash
openssl rand -hex 32
```

## Step 7: Update CORS for EC2 IP

Edit `docker-compose.yml` and update:
```yaml
BACKEND_CORS_ORIGINS: '["http://<EC2_PUBLIC_IP>:5173","http://<EC2_PUBLIC_IP>"]'
```

Also rebuild frontend with the EC2 IP:
```yaml
args:
  VITE_API_BASE_URL: http://<EC2_PUBLIC_IP>:8000
```

## Step 8: Start the Stack

```bash
cd ~/enterprise-knowledge-intelligence
docker compose up --build -d
docker compose ps
```

All three services should show `healthy`:
```
postgres    healthy
backend     healthy
frontend    healthy
```

## Step 9: Verify

```bash
curl http://localhost:8000/api/health
```

Then open in your browser:
```
http://<EC2_PUBLIC_IP>:5173
```

Login with:
- Email: `atul@enterprise.ai`
- Password: `atul123`

## Step 10: Keep Ollama Running

```bash
# Check Ollama is running
curl http://localhost:11434

# If not, start it
ollama serve &
```

## Troubleshooting

**Backend won't start:**
```bash
docker compose logs backend
```

**Ollama not reachable from Docker:**
- On EC2, `host.docker.internal` may not work on Linux
- Use the EC2 private IP instead:
```bash
hostname -I  # get private IP e.g. 172.31.xx.xx
```
Then set in docker-compose.yml:
```yaml
OLLAMA_BASE_URL: http://172.31.xx.xx:11434
```

**Port not accessible:**
- Check EC2 Security Group has port 5173 and 8000 open
- Check Docker containers are running: `docker compose ps`

## Estimated Cost

| Resource | Type | Cost |
|----------|------|------|
| EC2 | t3.medium | ~$30/month |
| Storage | 30GB EBS | ~$3/month |
| Data transfer | minimal | ~$1/month |
| **Total** | | **~$34/month** |

To stop billing when not in use:
- Stop (not terminate) the EC2 instance from the AWS Console
- Stopped instances are not charged for compute, only storage (~$3/month)
