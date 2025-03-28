from PIL import Image, ImageDraw

def create_speed_icon():
    # 256x256 boyutunda transparan bir resim oluştur
    size = (256, 256)
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Koyu arka plan dairesi
    draw.ellipse([(0, 0), (256, 256)], fill='#1B1E2B')
    
    # Yeşil hız göstergesi yayı
    draw.arc([(30, 30), (226, 226)], 180, 360, fill='#00FF9F', width=20)
    
    # Mavi ikinci yay
    draw.arc([(50, 50), (206, 206)], 180, 300, fill='#00E5FF', width=15)
    
    # Merkez nokta
    draw.ellipse([(108, 108), (148, 148)], fill='#00FF9F')
    
    # Farklı boyutlarda icon kaydet
    image.save('speedtest.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

if __name__ == "__main__":
    create_speed_icon()