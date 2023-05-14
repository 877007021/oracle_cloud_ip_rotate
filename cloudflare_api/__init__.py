import requests
import config
from util import log, is_empty


def get_dns_record(zone_id, api_key, dns_name):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={dns_name}'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()['result']
        if len(data) > 0:
            return data[0]
    return None


def update_dns_record_ip(zone_id, api_key, record, new_ip) -> bool:
    record_id = record['id']
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'type': 'A',
        'name': record['name'],
        'content': new_ip,
        'proxied': record['proxied']
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        return True
    else:
        return False


def update():
    if not config.AppConfig.hash_grup("cloudflare"):
        log("未配置 cloudflare 信息，跳过 DNS 记录更新")
        return
    zone_id = config.AppConfig.get("cloudflare", "cloudflare_zone_id")
    if is_empty(zone_id):
        log("未配置 zone_id 信息，跳过 DNS 记录更新")
        return
    api_key = config.AppConfig.get("cloudflare", "cloudflare_api_key")
    if is_empty(api_key):
        log("未配置 api_key 信息，跳过 DNS 记录更新")
        return
    domains = config.AppConfig.get("cloudflare", "domains")
    domain_list = domains.split(' ')
    for domain in domain_list:
        record = get_dns_record(zone_id, api_key, domain)
        if update_dns_record_ip(zone_id, api_key, record, config.AppConfig.ip_address):
            log(f"成功将 DNS 记录 {domain} 的 IP 修改为 {config.AppConfig.ip_address}")
