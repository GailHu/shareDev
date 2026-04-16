# -*- coding: utf-8 -*-

import logging
import os
import datetime
import sys

if sys.gettrace() is None:
    print("当前代码处于运行模式 (Run Mode)")
    level = logging.INFO
else:
    print("当前代码处于调试模式 (Debug Mode)")
    level = logging.DEBUG

log_date = datetime.date.today()
# 创建日志文件夹
log_folder = "logs/" + datetime.datetime.now().strftime('%Y-%m')
os.makedirs(log_folder, exist_ok=True)

# 配置日志记录器
log_file = os.path.join(log_folder, f"log-{datetime.datetime.now().strftime('%Y-%m-%d')}.log")
logging.basicConfig(filename=log_file, level=level,
                    format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(console_handler)


# 用于重新配置日志文件的函数
def reconfigure_logging(new_date):
    global log_file, log_date
    log_date = new_date
    new_log_file = os.path.join(log_folder, f"log-{log_date.strftime('%Y-%m-%d')}.log")
    # 如果日期变化，则重新配置日志文件
    if new_log_file != log_file:
        print(f"Switching to new log file: {new_log_file}")
        logging.shutdown()  # 关闭现有日志处理器
        logging.basicConfig(filename=new_log_file, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')


def check_date():
    current_date = datetime.date.today()
    if current_date > log_date:  # 检查日期是否已变更
        reconfigure_logging(current_date)


def debug(msg, *args, **kwargs):
    check_date()
    logging.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    check_date()
    logging.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    check_date()
    logging.warning(msg, *args, **kwargs)


def error(msg):
    logging.error(msg)


