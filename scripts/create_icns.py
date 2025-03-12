from PIL import Image
import os

def create_icns():
    # 讀取原始圖標
    ico_path = 'src/resources/clip_clip_icon.ico'
    icns_path = 'src/resources/clip_clip_icon.icns'
    
    # 創建臨時目錄
    os.makedirs('iconset', exist_ok=True)
    
    # 打開圖像
    img = Image.open(ico_path)
    
    # 創建不同尺寸的圖像
    sizes = [(16,16), (32,32), (64,64), (128,128), (256,256), (512,512), (1024,1024)]
    
    for size in sizes:
        resized = img.resize(size)
        resized.save(f'iconset/icon_{size[0]}x{size[0]}.png')
    
    # 使用 iconutil 創建 .icns 文件
    os.system('iconutil -c icns iconset -o ' + icns_path)
    
    # 清理臨時文件
    os.system('rm -rf iconset')

if __name__ == '__main__':
    create_icns() 