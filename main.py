import time
import cloudflare_api
import oci_api
from config import AppConfig
from util import ping_ip, log, is_not_empty, ping

AppConfig.load("config.ini")


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


if __name__ == '__main__':
    print()
    oci_api.init()
    switch_ip()
    log(f"更新IP成功，最新 IP 地址：{AppConfig.ip_address}")
    log("更新 cloudflare DNS 记录")
    cloudflare_api.update()
