#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import logging
import datetime
import subprocess
import tarfile

# 配置日志
def setup_logging(site_name, log_dir):
    """设置日志配置"""
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名，包含时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{site_name}_{timestamp}.log")
    
    # 配置日志
    logger = logging.getLogger(site_name)
    logger.setLevel(logging.INFO)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def clean_old_logs(log_dir, days=7):
    """清理超过指定天数的日志文件"""
    logger = logging.getLogger("cleanup")
    logger.info(f"开始清理 {log_dir} 中超过 {days} 天的日志文件")
    
    # 确保日志目录存在
    if not os.path.exists(log_dir):
        logger.info(f"日志目录 {log_dir} 不存在，跳过清理")
        return
    
    # 获取当前时间
    now = datetime.datetime.now()
    
    # 遍历日志目录
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            if file.endswith('.log'):
                file_path = os.path.join(root, file)
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # 计算文件年龄（天数）
                age_days = (now - file_time).days
                
                # 如果文件超过指定天数，则删除
                if age_days > days:
                    try:
                        os.remove(file_path)
                        logger.info(f"已删除旧日志文件: {file_path} (年龄: {age_days} 天)")
                    except Exception as e:
                        logger.error(f"删除日志文件 {file_path} 时出错: {e}")

def ensure_directory_exists(directory):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        return True
    return False

def sync_ftp_site(site_config, base_dir):
    """同步单个FTP站点"""
    site_name = site_config["name"]
    host = site_config["host"]
    username = site_config["username"]
    password = site_config["password"]
    remote_path = site_config["remote_path"]
    
    # 设置目录
    temp_dir = os.path.join(base_dir, "temp", site_name)
    backup_dir = os.path.join(base_dir, "backup", site_name)
    log_dir = os.path.join(base_dir, "logs", site_name)
    
    # 确保目录存在
    ensure_directory_exists(temp_dir)
    ensure_directory_exists(backup_dir)
    
    # 设置日志
    logger = setup_logging(site_name, log_dir)
    logger.info(f"开始同步站点: {site_name}")
    
    try:
        # 清理临时目录
        if os.path.exists(temp_dir):
            logger.info(f"清理临时目录: {temp_dir}")
            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
        
        # 使用lftp同步文件
        logger.info(f"使用lftp从 {host} 同步文件到 {temp_dir}")
        
        # 生成时间戳
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 构建lftp命令
        lftp_cmd = [
            "lftp",
            "-u", f"{username},{password}",
            f"ftp://{host}",
            '-e', f'''
                set xfer:log yes;
                set xfer:log-file {os.path.join(log_dir, f'{site_name}_{timestamp}_lftp.log')};
                set net:timeout 60;
                set ftp:list-options -a;
                set ftp:ssl-allow no;
                mirror --verbose --delete --parallel=4 --include-glob * {remote_path} {temp_dir};
                quit
            '''
        ]
        
        # 执行lftp命令
        process = subprocess.Popen(
            lftp_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 获取输出
        stdout, stderr = process.communicate()
        
        # 记录输出
        if stdout:
            logger.info(f"lftp输出: {stdout}")
        if stderr:
            logger.warning(f"lftp错误: {stderr}")
        
        # 检查命令执行结果
        if process.returncode != 0:
            logger.error(f"lftp同步失败，返回码: {process.returncode}")
            return False
        
        # 检查同步结果
        if os.path.exists(temp_dir):
            files = os.listdir(temp_dir)
            logger.info(f"同步完成，临时目录中的文件: {files}")
        else:
            logger.error("临时目录不存在，同步可能失败")
            return False
        
        # 创建压缩文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{site_name}_{timestamp}.tar.gz"
        archive_path = os.path.join(backup_dir, archive_name)
        
        logger.info(f"创建压缩文件: {archive_path}")
        
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(temp_dir, arcname=os.path.basename(temp_dir))
        
        logger.info(f"站点 {site_name} 同步完成")
        return True
        
    except Exception as e:
        logger.error(f"同步站点 {site_name} 时出错: {e}")
        return False

def main():
    """主函数"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置基础目录
    base_dir = script_dir
    
    # 确保必要的目录存在
    ensure_directory_exists(os.path.join(base_dir, "backup"))
    ensure_directory_exists(os.path.join(base_dir, "logs"))
    ensure_directory_exists(os.path.join(base_dir, "temp"))
    
    # 读取配置文件
    config_file = os.path.join(base_dir, "ftp_config.json")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"读取配置文件 {config_file} 时出错: {e}")
        sys.exit(1)
    
    # 同步每个站点
    for site in config.get("sites", []):
        if site.get("enabled", False):
            sync_ftp_site(site, base_dir)
    
    # 清理旧日志
    clean_old_logs(os.path.join(base_dir, "logs"), days=7)

if __name__ == "__main__":
    main()