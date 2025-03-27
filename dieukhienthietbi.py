from tkinter  import *
import paho.mqtt.client as mqtt

# Khai báo thông tin broker và topic
pub = "A" #chủ đề gửi thông tin đến esp
sub = "A_tt"# chủ đề nhận thông tin từ esp
pub1 = "T"# chủ đề quạt
sub1 = "T_tt"#

broker_address = "9ba9df8b51f04323ae32907b8d102e89.s1.eu.hivemq.cloud"
port = 8883 
username = "tuananhc"
password = "Abc123456789"

# Kết nối đến HiveMQ broker
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # Sử dụng API mới
client.username_pw_set(username, password)#kết nối tk mk trước rồi mới đến địa chỉ và cổng
client.tls_set()  # Kết nối bảo mật SSL/TLS
client.connect(broker_address, port)
client.subscribe(sub)
client.subscribe(pub)
client.subscribe(sub1)
client.subscribe(pub1)

# Biến trạng thái
is_on = False  # Trạng thái hiện tại của nút nhấn

# Xử lý khi nhận tin nhắn từ MQTT được gủi từ esp
def on_message(client, userdata, message):
    global is_on
    msg = message.payload.decode("utf-8")
    if msg == "Den Bat":
        on_button.config(image=on)
        is_on = True
    elif msg == "Den Tat" :
        on_button.config(image=off)
        is_on = False 
    window.update()
    print(f"[Nhận từ MQTT] Tin nhắn: {msg}")  # Debug
client.message_callback_add(sub, on_message)

def on_message1(client, userdata, message):
    msg = message.payload.decode("utf-8")
    if msg == "Muc_0":
        change_color()
        button_muc0.config(bg="orange")
    if msg == "Muc_1":
        change_color()
        button_muc1.config(bg="orange") 
    if msg == "Muc_2":
        change_color()
        button_muc2.config(bg="orange")
    if msg == "Muc_3":
        change_color()
        button_muc3.config(bg="orange")    
    window.update()
   
client.message_callback_add(sub1, on_message1)  # Gán hàm xử lý tin nhắn

#khơi tạo GUI(khung giao diện điều khiển)
window = Tk()
window.title('giao diện điều khiển')
window.geometry('500x300+400+300')#khung dài(x) * rộng (y), vị trí x = 400 y=300

# Hàng 1: Tiêu đề chính
label_title = Label(window, text="Điều khiển thiết bị", fg="Blue", font=("Helvetica", 18, "bold"))
label_title.pack(pady=10)

# Hàng 2: Tiêu đề điều khiển bóng đèn
my_label = Label(window, text = "Bật tắt bóng đèn", fg="Green", font= ("Helvetica", 18))
my_label.pack()

#gắn hình ảnh nút nhấn vào khung và xử lý nút nhấn giao diện điều khiển hàng 3
on = PhotoImage(file= "images_button/on.png")
off = PhotoImage(file = "images_button/off.png")
def switch():
    global is_on
    if is_on:
        on_button.config(image = off)
        is_on = False
        client.publish(pub, "0")  # Gửi lệnh "0" đến ESP32 thông qua topic S
    else:
        on_button.config(image = on)
        is_on = True
        client.publish(pub, "1") # Gửi lệnh "1" đến ESP32 thông qua topic S
    print(f"[Nút nhấn] Trạng thái: {'on' if is_on else 'off'}")  # Debug

on_button = Button(window, image= off, bd = 0, command= switch)
on_button.pack(pady=5)

# Hàng 4: Tiêu đề điều khiển quạt
label_quat = Label(window, text="Điều khiển quạt", fg="Green", font=("Helvetica", 18))
label_quat.pack(pady=10)

# Hàng 5: 4 nút điều khiển quạt
def change_color():
    button_muc0.config(bg="white")
    button_muc1.config(bg="white")
    button_muc2.config(bg="white")
    button_muc3.config(bg="white")


def switch1(level, button):
    change_color()
    button.config(bg= "orange")
    client.publish(pub1, str(level))
    print(f"[MQTT] gửi tín hiệu: Quạt mức {level}") 

button_muc0 = Button(window, text="Mức 1", width=10, height=2, command=lambda: switch1(96, button_muc0))
button_muc1 = Button(window, text="Mức 2", width=10, height=2, command=lambda: switch1(168, button_muc1))
button_muc2 = Button(window, text="Mức 3", width=10, height=2, command=lambda: switch1(255, button_muc2))
button_muc3 = Button(window, text="Tắt Quạt", width=10, height=2, command=lambda: switch1(0, button_muc3))

button_muc0.pack(side=LEFT, padx=5, pady=5) #pad x (padx =5 khoảng cách trái/phải 5 pixel)
button_muc1.pack(side=LEFT, padx=5, pady=5)#pad y (pady = khoảng cách trên dưới)
button_muc2.pack(side=LEFT, padx=5, pady=5)
button_muc3.pack(side=LEFT, padx=5, pady=5)


client.loop_start()
window.mainloop()
