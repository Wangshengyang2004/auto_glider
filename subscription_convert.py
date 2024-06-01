import yaml
import json
import hydra
import subprocess
from omegaconf import DictConfig
from loguru import logger
import os
BASE_CONFIG = """
# Verbose mode, print logs
verbose=True  #允许打印日志
listen=:8443  #监听端口

strategy=rr   #节点选择策略
"""
def parse_config(array: list):
    ss = []
    # {'name': '泰国', 'type': 'ss', 'server': 'xxx.cn', 'port': 123, 'cipher': 'chacha20-ietf-poly1305', 'password': 'password', 'udp': True}
    vmess = []
    # { name: '香港', type: vmess, server: 'xxx.cn', port: 123, uuid: ac005860, alterId: 0, cipher: auto, udp: true }
    for node in array:
        if node['type'] == 'ss':
            node = f"{node['type']}://{node['cipher']}:{node['password']}@{node['server']}:{node['port']}#{node['name']}"
            ss.append(node)
        elif node['type'] == 'vmess':
            node = f"{node['type']}://none:{node['uuid']}@{node['server']}:{node['port']}?alterID={node['alterId']}"
            vmess.append(node)
    for node in ss:
        print(f'forward={node}')
    print('-------------------')
    for node in vmess:
        print(f'forward={node}')
    return ss, vmess

@hydra.main(config_path="./config", config_name="urls", version_base="1.2")
def main(cfg: DictConfig):
    try:
        os.remove("glider.config")
    except FileNotFoundError:
        logger.info("No glider.config file found. Skipping")

    logger.info(f"Config:\n{cfg.urls}")
    urls = cfg.urls
    first_time = True
    for url in urls:
        subprocess.run(f'curl -o ./clash.yaml {url}', shell=True)
        with open('clash.yaml', 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            list_array = config['proxies']
            ss, vmess = parse_config(list_array)
        os.remove('clash.yaml')
        with open("glider.config", "a", encoding='utf-8') as f:
            if first_time:
                f.write(BASE_CONFIG)
                first_time = False
            for node in ss:
                f.write(f"forward={node}\n")
            for node in vmess:
                f.write(f"forward={node}\n")
            f.write("\n")
if __name__ == '__main__':
    main()