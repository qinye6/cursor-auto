from PIL import Image
import os

def create_ico(png_path, ico_path):
    """将PNG转换为ICO"""
    img = Image.open(png_path)
    img.save(ico_path, format='ICO', sizes=[(256, 256)])

def create_icns(png_path, icns_path):
    """将PNG转换为ICNS"""
    img = Image.open(png_path)
    img.save(icns_path, format='ICNS')

if __name__ == "__main__":
    # 确保assets目录存在
    os.makedirs("assets", exist_ok=True)
    
    # 转换图标
    source_png = "assets/icon.png"  # 源PNG文件
    create_ico(source_png, "assets/icon.ico")
    create_icns(source_png, "assets/icon.icns") 