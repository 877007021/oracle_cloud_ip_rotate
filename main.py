import os
import sys
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

import cloudflare_api
import oci_api
from config import AppConfig
from util import log, is_not_empty, ping, is_empty

config_path = os.getenv('config_path')
if is_empty(config_path):
    config_path = "config.ini"
AppConfig.load(config_path)


def switch_ip():
    if is_not_empty(AppConfig.ip_address):
        log(f"检测 IP: {AppConfig.ip_address} 是否能够连接")
        delay = ping(AppConfig.ip_address)
        AppConfig.ip_connection = delay < 200
        if AppConfig.ip_connection:
            log(f"IP: {AppConfig.ip_address} 连接成功")
            return
        log(f"IP: {AppConfig.ip_address} 连接失败，开始更换IP地址")
    try:
        if is_not_empty(AppConfig.ip_address):
            oci_api.delete_public_ip()
        oci_api.create_temporary_ip()
        log(f"获取新的临时IP成功: {AppConfig.ip_address}")
        switch_ip()
    except Exception as e:
        time.sleep(30)
        switch_ip()


def start():
    oci_api.init()
    switch_ip()
    log(f"更新IP成功，最新 IP 地址：{AppConfig.ip_address}")
    log("更新 cloudflare DNS 记录")
    cloudflare_api.update()


def job():
    cron = AppConfig.get("outer", "cron")
    if is_empty(cron):
        log("未配置定时任务，开始单次执行")
        start()
        sys.exit(0)
    else:
        log(f"创建定时任务成功，crontab: {cron}")
        scheduler = BlockingScheduler()
        scheduler.add_job(start, CronTrigger.from_crontab(cron))
        scheduler.start()


if __name__ == '__main__':
    print()
    job()
