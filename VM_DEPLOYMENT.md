# Vocalysis VM Deployment Guide

This guide provides instructions for deploying the Vocalysis system on a virtual machine (VM) for production use.

## System Requirements

- 8+ CPU cores
- 16GB+ RAM
- SSD storage (at least 100GB)
- Ubuntu 20.04 LTS or later
- CUDA-compatible GPU (optional, for faster model training)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CittaaHealthServices/CittaaHealthServices.git
   cd CittaaHealthServices
   ```

2. **Set up a Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y postgresql postgresql-contrib
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   
   # Create a database and user
   sudo -u postgres psql -c "CREATE DATABASE vocalysis;"
   sudo -u postgres psql -c "CREATE USER vocalysis WITH ENCRYPTED PASSWORD 'your_secure_password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vocalysis TO vocalysis;"
   ```

5. **Configure environment variables:**
   Create a `.env` file in the root directory with the following content:
   ```
   DB_TYPE=postgresql
   DB_CONNECTION_STRING=postgresql://vocalysis:your_secure_password@localhost/vocalysis
   ENCRYPTION_KEY=your_secure_encryption_key
   ```

## Running the System

### Option 1: Direct Python Execution

1. **Start the application:**
   ```bash
   streamlit run app.py
   ```

### Option 2: Docker Deployment (Recommended)

1. **Install Docker and Docker Compose:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER
   ```

2. **Build and start the containers:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   Open your browser and navigate to `http://your_vm_ip:8501`

## Performance Optimization

1. **CPU Optimization:**
   - Set the number of worker processes based on available CPU cores:
     ```bash
     export OMP_NUM_THREADS=$(nproc)
     ```

2. **Memory Optimization:**
   - Monitor memory usage with `htop` or similar tools
   - Adjust batch sizes in the code based on available memory

3. **GPU Acceleration:**
   - If a CUDA-compatible GPU is available, the system will automatically use it
   - Verify GPU usage with `nvidia-smi`

## Monitoring and Maintenance

1. **Set up logging:**
   ```bash
   mkdir -p logs
   ```

2. **Set up regular backups:**
   ```bash
   # Backup PostgreSQL database
   pg_dump -U vocalysis vocalysis > backup_$(date +%Y%m%d).sql
   
   # Backup model files
   tar -czf models_backup_$(date +%Y%m%d).tar.gz model/
   ```

3. **Set up a cron job for regular backups:**
   ```bash
   crontab -e
   ```
   
   Add the following line for daily backups at 2 AM:
   ```
   0 2 * * * /path/to/backup_script.sh
   ```

## Security Considerations

1. **Enable HTTPS:**
   - Install certbot for Let's Encrypt certificates:
     ```bash
     sudo apt-get install -y certbot python3-certbot-nginx
     sudo certbot --nginx -d your_domain.com
     ```

2. **Set up a firewall:**
   ```bash
   sudo ufw allow 'Nginx Full'
   sudo ufw allow ssh
   sudo ufw enable
   ```

3. **Regular updates:**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade
   ```

## Troubleshooting

1. **Database connection issues:**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check connection string in `.env` file
   - Ensure the database user has proper permissions

2. **Audio processing issues:**
   - Verify all audio processing libraries are installed: `pip list | grep -E 'librosa|soundfile|pydub'`
   - Check that ffmpeg is installed: `ffmpeg -version`

3. **Model training performance:**
   - For slow model training, verify GPU usage: `nvidia-smi`
   - Adjust batch sizes based on available memory

4. **Storage issues:**
   - Monitor disk usage: `df -h`
   - Set up log rotation to prevent log files from filling disk space

## Support

For additional support or to report issues, please contact Cittaa Health Services at support@cittaa.in or open an issue on the GitHub repository.
