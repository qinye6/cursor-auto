import random

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        
    def add_proxy(self, proxy):
        """添加代理"""
        if self.validate_proxy(proxy):
            self.proxies.append(proxy)
            
    def rotate_proxy(self):
        """轮换代理"""
        if self.proxies:
            self.current_proxy = random.choice(self.proxies)
        return self.current_proxy 