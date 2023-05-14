# oracle_cloud_ip_rotate

Oracle cloud 国内IP更换

## 简介

自动检测当前实例IP是否能在国内访问，无法访问的情况下会自动进行更换IP，并修改 cloudflare dns记录（可选）

项目所用到的配置统一在 `config.ini ` 配置文件当中，请根据实际情况自行调整配置

## 配置

### DEFAULT

此配置是在申请 OCI 时自动生成的，具体申请过程请参考：https://github.com/877007021/oracle-cloud-network-tools

| 配置        | 描述                                                         | 必须 |
| ----------- | ------------------------------------------------------------ | ---- |
| user        |                                                              | 是   |
| fingerprint |                                                              | 是   |
| tenancy     |                                                              | 是   |
| region      |                                                              | 是   |
| key_file    | 申请 OCI 时下载的 pem 文件，项目默认使用 oci.pem，如果名称不一致请更改 | 是   |

### oracle

| 配置        | 描述                        | 必须 |
| ----------- | --------------------------- | ---- |
| instance_id | 当前要操作的实例的 **OCID** | 是   |

### cloudflare（可选）

cloudflare 的配置信息，用于更改 cloudflare 的 DNS 解析记录

| 配置               | 描述           | 必须 |
| ------------------ | -------------- | ---- |
| cloudflare_zone_id | 区域ID         | 否   |
| cloudflare_api_key | api_key        | 否   |
| domains            | 需要更新的域名 | 否   |

### outer（可选）

检测 IP ping 的延迟，默认 200

| 配置  | 描述                                          | 必须 |
| ----- | --------------------------------------------- | ---- |
| delay | 延迟，ping 超过此延迟则认为无法连接，默认 200 | 否   |

## 使用

### 本地

``` she
git clone https://github.com/877007021/oracle_cloud_ip_rotate.git
cd oracle_cloud_ip_rotate
# 修改配置信息
pip install -r requirements.txt
python main.py
```



