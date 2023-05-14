import oci as oci
import config as app_config
from util import is_empty

config = oci.config.from_file(app_config.AppConfig.config_path)


def init_instances_info():
    core_client = oci.core.ComputeClient(config)
    instance_response = core_client.get_instance(instance_id=app_config.AppConfig.instance_id)
    app_config.AppConfig.compartment_id = instance_response.data.compartment_id


def init_vnic_info():
    compute_client = oci.core.ComputeClient(config)
    vnic_attachments = compute_client.list_vnic_attachments(
        compartment_id=app_config.AppConfig.compartment_id,
        instance_id=app_config.AppConfig.instance_id
    ).data
    if len(vnic_attachments) == 0:
        raise ValueError("获取 vnic 失败, 请检测配置信息")
    vnic = vnic_attachments[0]
    app_config.AppConfig.vnic_id = vnic.vnic_id


def init_private_id():
    virtual_network_client = oci.core.VirtualNetworkClient(config)
    ips = virtual_network_client.list_private_ips(vnic_id=app_config.AppConfig.vnic_id).data
    if len(ips) == 0:
        raise ValueError("获取 private_ip_id 失败, 请检测配置信息")
    ip = ips[0]
    app_config.AppConfig.private_id = ip.id


def init_public_ip():
    virtual_network_client = oci.core.VirtualNetworkClient(config)
    vnic_details = virtual_network_client.get_vnic(app_config.AppConfig.vnic_id).data
    app_config.AppConfig.ip_address = vnic_details.public_ip


def init_public_id():
    if is_empty(app_config.AppConfig.ip_address):
        return
    core_client = oci.core.VirtualNetworkClient(config)
    get_public_ip_by_ip_address = core_client.get_public_ip_by_ip_address(
        get_public_ip_by_ip_address_details=oci.core.models.GetPublicIpByIpAddressDetails(
            ip_address=app_config.AppConfig.ip_address)).data
    app_config.AppConfig.public_id = get_public_ip_by_ip_address.id


def delete_public_ip():
    core_client = oci.core.VirtualNetworkClient(config)
    core_client.delete_public_ip(public_ip_id=app_config.AppConfig.public_id)
    app_config.AppConfig.ip_address = None


def create_temporary_ip():
    core_client = oci.core.VirtualNetworkClient(config)
    create_public_ip_response = core_client.create_public_ip(
        create_public_ip_details=oci.core.models.CreatePublicIpDetails(
            compartment_id=app_config.AppConfig.compartment_id,
            lifetime="EPHEMERAL",
            private_ip_id=app_config.AppConfig.private_id)).data
    app_config.AppConfig.public_id = create_public_ip_response.id
    app_config.AppConfig.ip_address = create_public_ip_response.ip_address


def init():
    init_instances_info()
    init_vnic_info()
    init_private_id()
    init_public_ip()
    init_public_id()
