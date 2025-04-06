# FTP网站自动备份工具

自动备份多个FTP网站文件的Python脚本，使用lftp实现高效同步。

## 功能特点

- 支持多站点备份
- 自动压缩备份文件
- 自动清理过期日志

## 系统要求

- macOS系统
- Python 3.6+
- lftp命令行工具 (`brew install lftp`)

## 使用方法

1. 配置`ftp_config.json`：
```json
{
    "sites": [
        {
            "enable": true,
            "name": "站点名称1",
            "host": "ftp.example.com",
            "username": "用户名",
            "password": "密码",
            "remote_path": "/网站目录"
        },
        {
            "enable": true,
            "name": "站点名称2",
            "host": "ftp.example.com",
            "username": "用户名",
            "password": "密码",
            "remote_path": "/网站目录"
        }
    ]
}
```

2. 运行脚本：
```bash
python3 ftp_backup.py
```

## 定时任务

每天凌晨2点执行：
```bash
0 2 * * * /usr/bin/python3 /path/to/ftp_backup.py
```

---

# FTP Website Auto Backup Tool

A Python script for automatically backing up multiple FTP website files using lftp for efficient synchronization.

## Features

- Multi-site backup support
- Automatic backup compression
- Automatic log cleanup

## Requirements

- macOS system
- Python 3.6+
- lftp command-line tool (`brew install lftp`)

## Usage

1. Configure `ftp_config.json`:
```json
{
    "sites": [
        {
            "enable": true,
            "name": "site_name1",
            "host": "ftp.example.com",
            "username": "username",
            "password": "password",
            "remote_path": "/website_directory"
        },
        {
            "enable": true,
            "name": "site_name2",
            "host": "ftp.example.com",
            "username": "username",
            "password": "password",
            "remote_path": "/website_directory"
        }
    ]
}
```

2. Run the script:
```bash
python3 ftp_backup.py
```

## Scheduled Task

Execute daily at 2 AM:
```bash
0 2 * * * /usr/bin/python3 /path/to/ftp_backup.py
```