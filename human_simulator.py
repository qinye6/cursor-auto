import time
import random
import asyncio
from datetime import datetime
from typing import Tuple, List, Optional

class HumanSimulator:
    def __init__(self, browser):
        self.browser = browser
        
    async def natural_typing(self, element, text):
        """模拟人类输入"""
        for char in text:
            await element.type(char)
            # 随机延迟模拟人类输入速度
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
    async def natural_scroll(self):
        """模拟自然滚动"""
        scroll_height = await self.browser.evaluate('document.body.scrollHeight')
        current_position = 0
        while current_position < scroll_height:
            step = random.randint(100, 300)
            current_position += step
            await self.browser.evaluate(f'window.scrollTo(0, {current_position})')
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
    async def add_random_delays(self):
        """添加随机延迟"""
        await asyncio.sleep(random.uniform(1, 3))
        
    async def move_mouse_naturally(self, element):
        """自然的鼠标移动"""
        try:
            # 获取元素位置
            box = await element.bounding_box()
            if box:
                # 生成贝塞尔曲线路径点
                points = self.generate_bezier_curve(
                    (0, 0),
                    (box['x'] + box['width']/2, box['y'] + box['height']/2)
                )
                # 执行鼠标移动
                for point in points:
                    await self.browser.mouse.move(point[0], point[1])
                    await asyncio.sleep(random.uniform(0.01, 0.03))
        except Exception as e:
            print(f"鼠标移动出错: {str(e)}")

    def generate_bezier_curve(self, start, end):
        """生成贝塞尔曲线路径"""
        # 控制点
        control1 = (
            start[0] + (end[0] - start[0]) * random.uniform(0.2, 0.4),
            start[1] + (end[1] - start[1]) * random.uniform(0.2, 0.4)
        )
        control2 = (
            start[0] + (end[0] - start[0]) * random.uniform(0.6, 0.8),
            start[1] + (end[1] - start[1]) * random.uniform(0.6, 0.8)
        )
        
        points = []
        steps = 30
        for i in range(steps + 1):
            t = i / steps
            x = (1-t)**3 * start[0] + 3*(1-t)**2 * t * control1[0] + \
                3*(1-t) * t**2 * control2[0] + t**3 * end[0]
            y = (1-t)**3 * start[1] + 3*(1-t)**2 * t * control1[1] + \
                3*(1-t) * t**2 * control2[1] + t**3 * end[1]
            points.append((x, y))
        return points 

    async def random_mouse_movements(self):
        """随机鼠标移动"""
        viewport = await self.browser.viewport_size()
        if viewport:
            for _ in range(random.randint(3, 7)):
                x = random.randint(0, viewport['width'])
                y = random.randint(0, viewport['height'])
                await self.move_mouse_naturally((x, y))
                await asyncio.sleep(random.uniform(0.2, 0.8))

    async def interact_with_page(self):
        """模拟页面交互"""
        # 随机选择文本
        texts = await self.browser.query_selector_all('p, h1, h2, h3')
        if texts:
            text = random.choice(texts)
            await self.move_mouse_naturally(text)
            await text.click()
            
        # 随机滚动
        await self.natural_scroll()
        
        # 模拟选择文本
        if texts:
            text = random.choice(texts)
            await text.evaluate('''(el) => {
                const range = document.createRange();
                range.selectNodeContents(el);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
            }''')
        
        await asyncio.sleep(random.uniform(1, 3))
        
        # 取消选择
        await self.browser.evaluate('window.getSelection().removeAllRanges()') 