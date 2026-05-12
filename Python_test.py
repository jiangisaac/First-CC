import os
import threading
from queue import Queue
import time

live_ip = []
queue = Queue()

def ping_ip(ip):
    # Windows 只发1个包，超时500毫秒，足够响应
    cmd = f"ping -n 1 -w 500 {ip} > nul"
    if os.system(cmd) == 0:
        print(f"✅ 在线：{ip}")
        live_ip.append(ip)
    else:
        print(f"❌ 离线：{ip}")

def worker():
    while not queue.empty():
        ip = queue.get()
        ping_ip(ip)
        # 每个线程稍微停顿一下，不要猛跑
        time.sleep(0.05)
        queue.task_done()

def main():
    print("===== 局域网IP慢速稳定扫描 =====")
    prefix = input("输入IP前缀 例如 192.168.1 : ").strip()

    for i in range(1, 255):
        queue.put(f"{prefix}.{i}")

    print("\n开始扫描...稍等片刻\n")

    # 关键：线程调低，不疯狂并发，避免判超时
    thread_num = 8
    for _ in range(thread_num):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    queue.join()

    print("\n===== 在线IP汇总 =====")
    for ip in live_ip:
        print(f"✅ 在线：{ip}")

if __name__ == "__main__":
    main()