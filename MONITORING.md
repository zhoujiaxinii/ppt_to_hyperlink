# PPT超链接转换器 - 监控和日志配置指南

## 📊 监控配置

### 1. 系统资源监控

#### 使用 systemd 监控服务状态
```bash
# 查看服务状态
sudo systemctl status ppt-hyperlink-converter

# 查看服务日志
sudo journalctl -u ppt-hyperlink-converter -f

# 查看最近1小时日志
sudo journalctl -u ppt-hyperlink-converter --since "1 hour ago"
```

#### 使用 top/htop 监控进程
```bash
# 查看Python进程
top -p $(pgrep -f gunicorn)

# 或使用htop（如果已安装）
htop -p $(pgrep -f gunicorn)
```

### 2. 应用性能监控

#### 日志文件位置
```
/var/log/ppt-hyperlink-converter/access.log  # 访问日志
/var/log/ppt-hyperlink-converter/error.log   # 错误日志
```

#### 日志轮转配置
创建 `/etc/logrotate.d/ppt-hyperlink-converter`:
```
/var/log/ppt-hyperlink-converter/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload ppt-hyperlink-converter > /dev/null 2>&1 || true
    endscript
}
```

## 📈 性能指标监控

### 1. API响应时间监控
应用在每个响应中包含性能数据:
```json
{
  "performance": {
    "download_time": 0.53,
    "extract_time": 0.13,
    "hyperlink_time": 0.22,
    "upload_time": 1.62,
    "total_time": 2.51
  }
}
```

### 2. 自定义监控脚本
创建 `/opt/ppt-hyperlink-converter/monitor.sh`:
```bash
#!/bin/bash
# 性能监控脚本

LOG_FILE="/var/log/ppt-hyperlink-converter/monitor.log"
HEALTH_ENDPOINT="http://localhost:5000/health"

# 检查服务健康状态
health_check() {
    response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_ENDPOINT)
    if [ $response -eq 200 ]; then
        echo "$(date): Service is healthy" >> $LOG_FILE
        return 0
    else
        echo "$(date): Service is unhealthy (HTTP $response)" >> $LOG_FILE
        return 1
    fi
}

# 检查磁盘使用率
disk_usage() {
    usage=$(df /opt | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $usage -gt 80 ]; then
        echo "$(date): Disk usage is high: ${usage}%" >> $LOG_FILE
    fi
}

# 检查内存使用率
memory_usage() {
    usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    if [ $usage -gt 80 ]; then
        echo "$(date): Memory usage is high: ${usage}%" >> $LOG_FILE
    fi
}

# 执行检查
health_check
disk_usage
memory_usage
```

### 3. 定时监控任务
添加到 crontab:
```bash
# 每5分钟检查一次服务健康状态
*/5 * * * * /opt/ppt-hyperlink-converter/monitor.sh
```

## 🔍 日志分析

### 1. 关键日志模式

#### 成功处理日志
```
INFO:__main__:Processing PPTX from URL: https://example.com/file.pptx
INFO:__main__:Found 1 links in 0.13s: ['https://example.com/video.mp4']
INFO:__main__:Total processing time: 2.51s
```

#### 错误日志模式
```
ERROR:__main__:Error downloading PPTX file: Connection timeout
ERROR:__main__:Failed to initialize COS client: Invalid credentials
```

### 2. 日志分析脚本
创建 `/opt/ppt-hyperlink-converter/log_analyzer.sh`:
```bash
#!/bin/bash
# 日志分析脚本

LOG_FILE="/var/log/ppt-hyperlink-converter/error.log"
REPORT_FILE="/var/log/ppt-hyperlink-converter/daily_report.txt"

# 生成每日错误报告
generate_report() {
    echo "=== PPT Hyperlink Converter Daily Report ($(date)) ===" > $REPORT_FILE
    echo "" >> $REPORT_FILE

    # 统计错误类型
    echo "Error Summary:" >> $REPORT_FILE
    grep "ERROR" $LOG_FILE | cut -d' ' -f4- | sort | uniq -c | sort -nr >> $REPORT_FILE
    echo "" >> $REPORT_FILE

    # 统计处理时间
    echo "Performance Stats:" >> $REPORT_FILE
    grep "Total processing time" $LOG_FILE | awk '{sum+=$NF; count++} END {if(count>0) print "Average processing time: " sum/count "s"}' >> $REPORT_FILE
}

generate_report
```

## 🚨 告警配置

### 1. 基于日志的告警
使用 logwatch 或自定义脚本监控关键错误:

```bash
# 检查关键错误并发送告警
check_critical_errors() {
    critical_errors=$(grep -c "CRITICAL\|FATAL" /var/log/ppt-hyperlink-converter/error.log)
    if [ $critical_errors -gt 0 ]; then
        # 发送告警邮件或通知
        echo "Critical errors detected in PPT converter" | mail -s "PPT Converter Alert" admin@example.com
    fi
}
```

### 2. 性能告警
```bash
# 检查处理时间是否超过阈值
check_performance() {
    slow_requests=$(grep "Total processing time" /var/log/ppt-hyperlink-converter/access.log | awk '$NF > 30 {count++} END {print count+0}')
    if [ $slow_requests -gt 10 ]; then
        echo "Performance degradation detected" | mail -s "PPT Converter Performance Alert" admin@example.com
    fi
}
```

## 🛠️ 故障排除

### 1. 常见问题诊断

#### 服务无法启动
```bash
# 检查服务状态
sudo systemctl status ppt-hyperlink-converter

# 查看详细日志
sudo journalctl -u ppt-hyperlink-converter --no-pager

# 检查端口占用
netstat -tlnp | grep :5000
```

#### COS配置问题
```bash
# 验证环境变量
echo $COS_SECRET_ID
echo $COS_SECRET_KEY
echo $COS_REGION
echo $COS_BUCKET

# 测试COS连接
curl -I https://$COS_BUCKET.cos.$COS_REGION.myqcloud.com/
```

#### 性能问题
```bash
# 分析慢请求
grep "Total processing time" /var/log/ppt-hyperlink-converter/access.log | awk '$NF > 10'
```

### 2. 重启和恢复
```bash
# 重启服务
sudo systemctl restart ppt-hyperlink-converter

# 重新加载配置
sudo systemctl reload ppt-hyperlink-converter

# 查看启动日志
sudo journalctl -u ppt-hyperlink-converter -f
```