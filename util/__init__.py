import logging
import socket
import struct
import subprocess
import time

import chardet
import select


def ping_ip(ip, timeout):
    if is_empty(ip):
        return False
    p = subprocess.Popen(["ping", ip], stdout=subprocess.PIPE)

    output = p.communicate()[0]
    encoding = chardet.detect(output)["encoding"]
    output = output.decode(encoding)

    if p.returncode == 0:
        return True
    else:
        time.sleep(timeout)
        return False


def log(message):
    """
        打印 log 信息

        Parameters:
            message (str): 要输出的 log 信息
            level (logging.LEVEL): log 信息的级别，默认为 INFO 级别
        """
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logging.log(logging.INFO, message)


def is_empty(obj):
    """
    判断对象是否为空

    Parameters:
        obj (Any): 要判断的对象

    Returns:
        bool: True 表示对象为空，False 表示对象不为空
    """
    if obj is None:

        return True
    elif isinstance(obj, str):

        return len(obj.strip()) == 0
    elif isinstance(obj, (list, tuple, set, dict)):

        return len(obj) == 0
    else:

        return False


def is_not_empty(obj):
    return not is_empty(obj)


def check_byte(data):
    n = len(data)
    m = n % 2
    sum = 0
    for i in range(0, n - m, 2):
        sum += (data[i]) + ((data[i + 1]) << 8)
    if m:
        sum += (data[-1])
    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)
    answer = ~sum & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def raw_socket(dst_addr, imcp_packet):
    rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    send_request_ping_time = time.time()
    rawsocket.sendto(imcp_packet, (dst_addr, 80))
    return send_request_ping_time, rawsocket, dst_addr


def request_ping(data_type, data_code, data_checksum, data_ID, data_Sequence, payload_body):
    imcp_packet = struct.pack('>BBHHH32s', data_type, data_code, data_checksum, data_ID, data_Sequence, payload_body)
    icmp_chesksum = check_byte(imcp_packet)
    imcp_packet = struct.pack('>BBHHH32s', data_type, data_code, icmp_chesksum, data_ID, data_Sequence, payload_body)
    return imcp_packet


def reply_ping(send_request_ping_time, rawsocket, data_sequence, timeout=2):
    while True:
        started_select = time.time()
        what_ready = select.select([rawsocket], [], [], timeout)
        wait_for_time = (time.time() - started_select)
        if what_ready[0] == []:
            return -1
        time_received = time.time()
        received_packet, addr = rawsocket.recvfrom(1024)
        icmpHeader = received_packet[20:28]
        type, code, checksum, packet_id, sequence = struct.unpack(
            ">BBHHH", icmpHeader
        )
        if type == 0 and sequence == data_sequence:
            return time_received - send_request_ping_time
        timeout = timeout - wait_for_time
        if timeout <= 0:
            return -1


def ping(host):
    data_type = 8
    data_code = 0
    data_checksum = 0
    data_ID = 0
    data_Sequence = 1
    payload_body = b'abcdefghijklmnopqrstuvwabcdefghi'
    dst_addr = socket.gethostbyname(host)
    time_list = []
    log("正在 Ping {0} [{1}] 具有 32 字节的数据:".format(host, dst_addr))
    for i in range(0, 4):
        icmp_packet = request_ping(data_type, data_code, data_checksum, data_ID, data_Sequence + i, payload_body)
        send_request_ping_time, rawsocket, addr = raw_socket(dst_addr, icmp_packet)
        times = reply_ping(send_request_ping_time, rawsocket, data_Sequence + i)
        if times > 0:
            t = int(times * 1000)
            time_list.append(t)
            log("来自 {0} 的回复: 字节=32 时间={1}ms".format(addr, t))
            time.sleep(0.7)
        else:
            log("请求超时。")

    if len(time_list) > 0:
        average_time = sum(time_list) / len(time_list)
        log(f"Ping {host} 平均延迟={average_time}")
        return average_time
    return None
