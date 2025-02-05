import random
import json
from datetime import datetime

class AntiDetection:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        
    def generate_webgl_params(self):
        """生成WebGL参数"""
        return {
            "vendor": random.choice(["Google Inc.", "Apple Computer, Inc."]),
            "renderer": random.choice([
                "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
                "ANGLE (AMD Radeon(TM) Graphics Direct3D11 vs_5_0 ps_5_0)",
                "Apple M1"
            ])
        }
    
    def generate_browser_features(self):
        """生成浏览器特征"""
        return {
            "languages": ["en-US", "en"],
            "colorDepth": 24,
            "deviceMemory": random.choice([4, 8, 16]),
            "hardwareConcurrency": random.choice([4, 8, 12, 16]),
            "screenResolution": random.choice([
                [1920, 1080],
                [2560, 1440],
                [1440, 900]
            ]),
            "timezone": random.choice([-480, -420, -360, 0, 60, 120]),
            "platform": random.choice(["Win32", "MacIntel"])
        }

    def generate_mouse_movements(self):
        """生成自然的鼠标移动轨迹"""
        movements = []
        x, y = 0, 0
        for _ in range(random.randint(10, 20)):
            x += random.randint(5, 20)
            y += random.randint(5, 20)
            timestamp = datetime.now().timestamp() * 1000
            movements.append({
                "x": x,
                "y": y,
                "timestamp": timestamp,
                "type": "mousemove"
            })
        return movements

    def randomize_fingerprint(self):
        """生成完整的浏览器指纹"""
        webgl = self.generate_webgl_params()
        features = self.generate_browser_features()
        
        return {
            "userAgent": random.choice(self.user_agents),
            "webgl": webgl,
            "features": features,
            "canvas": self.generate_canvas_hash(),
            "fonts": self.generate_font_list(),
            "audio": self.generate_audio_fingerprint(),
            "mouseMovements": self.generate_mouse_movements()
        }
    
    def generate_canvas_hash(self):
        """生成Canvas指纹"""
        return random.choice([
            "2674858385",
            "3674858395",
            "1674858375"
        ])
    
    def generate_font_list(self):
        """生成字体列表"""
        common_fonts = [
            "Arial", "Helvetica", "Times New Roman", 
            "Courier New", "Verdana", "Georgia"
        ]
        return random.sample(common_fonts, random.randint(4, 6))
    
    def generate_audio_fingerprint(self):
        """生成音频指纹"""
        return {
            "hash": f"{random.randint(1000000, 9999999)}",
            "oscillator": random.uniform(0.1, 0.9),
            "dynamicsCompressor": random.uniform(0.2, 0.8)
        } 