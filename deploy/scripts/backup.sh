#!/bin/bash
# 备份 Plab-Rundown 数据和配置

echo "=========================================="
echo "💾 Plab-Rundown 数据备份"
echo "=========================================="
echo ""

# 配置
PROJECT_DIR="/home/ubuntu/plab-rundown"
BACKUP_DIR="/home/ubuntu/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="plab-rundown-backup-${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# 创建备份目录
mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_PATH"

echo "📁 备份目录: $BACKUP_PATH"
echo ""

# 1. 备份环境变量
echo "1️⃣  备份环境变量..."
if [ -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env" "$BACKUP_PATH/.env"
    echo "✅ .env 已备份"
else
    echo "⚠️  .env 文件不存在"
fi

# 2. 备份配置文件
echo ""
echo "2️⃣  备份配置文件..."
if [ -d "$PROJECT_DIR/config" ]; then
    cp -r "$PROJECT_DIR/config" "$BACKUP_PATH/"
    echo "✅ config/ 已备份"
else
    echo "⚠️  config/ 目录不存在"
fi

# 3. 备份凭证文件
echo ""
echo "3️⃣  备份凭证文件..."
if [ -d "$PROJECT_DIR/credentials" ]; then
    cp -r "$PROJECT_DIR/credentials" "$BACKUP_PATH/"
    echo "✅ credentials/ 已备份"
else
    echo "⚠️  credentials/ 目录不存在"
fi

# 4. 备份数据库
echo ""
echo "4️⃣  备份数据库..."
if [ -f "$PROJECT_DIR/data/plab_rundown.db" ]; then
    mkdir -p "$BACKUP_PATH/data"
    cp "$PROJECT_DIR/data/plab_rundown.db" "$BACKUP_PATH/data/"
    echo "✅ 数据库已备份"
else
    echo "⚠️  数据库文件不存在"
fi

# 5. 备份日志 (最近 7 天)
echo ""
echo "5️⃣  备份日志..."
if [ -d "$PROJECT_DIR/logs" ]; then
    mkdir -p "$BACKUP_PATH/logs"
    find "$PROJECT_DIR/logs" -name "*.log" -mtime -7 -exec cp {} "$BACKUP_PATH/logs/" \;
    echo "✅ 日志已备份 (最近 7 天)"
else
    echo "⚠️  logs/ 目录不存在"
fi

# 6. 压缩备份
echo ""
echo "6️⃣  压缩备份..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

echo "✅ 备份已压缩: ${BACKUP_NAME}.tar.gz"

# 7. 清理旧备份 (保留最近 7 个)
echo ""
echo "7️⃣  清理旧备份..."
cd "$BACKUP_DIR"
ls -t plab-rundown-backup-*.tar.gz | tail -n +8 | xargs -r rm
echo "✅ 已清理旧备份 (保留最近 7 个)"

# 8. 显示备份信息
echo ""
echo "=========================================="
echo "✅ 备份完成!"
echo "=========================================="
echo ""
echo "📦 备份文件: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "📊 备份大小: $(du -h ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz | cut -f1)"
echo ""
echo "📋 备份列表:"
ls -lh "$BACKUP_DIR"/plab-rundown-backup-*.tar.gz
echo ""
echo "=========================================="

