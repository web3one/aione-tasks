BACKUP_NAME="backup-$(date +%Y%m%d).sql"

nohup docker exec mariadb mysqldump -uroot -paPuYeuVwqhrwTJTIpNtXAvYjzbNow0mN0RJUP0xl --all-databases > /opt/backup/$BACKUP_NAME 2>&1 &
