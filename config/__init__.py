import configparser
from typing import Dict
from util import is_not_empty


class AppConfig:
    """应用程序配置"""
    config: Dict = {}
    config_path = "config.ini"
    instance_id = None
    compartment_id = None
    vnic_id = None
    private_id = None
    public_id = None
    ip_address = None
    ip_connection = False
    max_delay = 200

    @classmethod
    def load(cls, filename: str) -> None:
        """从配置文件中加载配置"""
        parser = configparser.ConfigParser()
        parser.read(filename, encoding='utf-8')
        cls.config.update(dict(parser.items()))
        cls.config_path = filename
        cls.instance_id = cls.get("oracle", "instance_id")
        delay = cls.get("outer", "delay")
        if is_not_empty(delay):
            cls.max_delay = delay

    @classmethod
    def get(cls, group_name, key):
        if hash(group_name):
            return AppConfig.config[group_name].get(key)
        return None

    @classmethod
    def hash_grup(cls, group_name):
        return group_name in AppConfig.config
