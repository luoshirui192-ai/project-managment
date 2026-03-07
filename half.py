import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights

# ====================== 半成品：只有基础犬种库 ======================
DOG_BREED_ENCYCLOPEDIA = {
    "golden retriever": {
        "name": "金毛寻回犬",
        "intro": "性格温顺，无攻击性，非常适合家庭。"
    },
    "labrador retriever": {
        "name": "拉布拉多",
        "intro": "智商高，温顺，常用作工作犬。"
    },
    "pembroke welsh corgi": {
        "name": "柯基",
        "intro": "小短腿，性格活泼，很受欢迎。"
    },
    "siberian husky": {
        "name": "哈士奇",
        "intro": "精力旺盛，性格跳脱，有点调皮。"
    }
}

# ====================== 模型加载（半成品） ======================
def init_model():
    weights = ResNet50_Weights.DEFAULT
    model = resnet50(weights=weights)
    model.eval()
    class_names = weights.meta["categories"]
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    return model, preprocess, class_names

# ====================== 识别函数（半成品） ======================
def recognize_dog(img_path, model, preprocess, class_names):
    img = Image.open(img_path).convert("RGB")
    img_tensor = preprocess(img).unsqueeze(0)

    with torch.no_grad():
        output = model(img_tensor)
    idx = torch.argmax(output).item()
    pred = class_names[idx].lower()

    # 简单匹配
    for key in DOG_BREED_ENCYCLOPEDIA:
        if key in pred:
            return img, DOG_BREED_ENCYCLOPEDIA[key]

    return img, {"name": "未知犬种", "intro": f"模型识别结果：{pred}"}

# ====================== GUI 界面 ======================
class DogApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("犬种识别 - 未完整完成版")
        self.geometry("800x500")
        self.model, self.preprocess, self.class_names = init_model()
        self.img_path = None

        # 按钮
        self.btn1 = ctk.CTkButton(self, text="选择图片", command=self.open_img)
        self.btn1.pack(pady=10)

        self.btn2 = ctk.CTkButton(self, text="开始识别", command=self.run_recog)
        self.btn2.pack(pady=10)

        # 图片显示
        self.img_label = ctk.CTkLabel(self, text="等待图片...", width=300, height=300)
        self.img_label.pack(pady=10)

        # 结果
        self.result_label = ctk.CTkLabel(self, text="结果：", font=("Arial", 16))
        self.result_label.pack(pady=5)

    def open_img(self):
        path = filedialog.askopenfilename()
        if path:
            self.img_path = path
            img = Image.open(path).resize((300, 300))
            self.photo = ImageTk.PhotoImage(img)
            self.img_label.configure(image=self.photo, text="")

    def run_recog(self):
        if not self.img_path:
            messagebox.showwarning("提示", "请先选图片")
            return
        img, info = recognize_dog(self.img_path, self.model, self.preprocess, self.class_names)
        self.result_label.configure(text=f"{info['name']}\n{info['intro']}")

if __name__ == "__main__":
    app = DogApp()
    app.mainloop()