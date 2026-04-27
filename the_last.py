import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
import threading
import warnings
warnings.filterwarnings("ignore")

# 从独立数据模块导入犬种数据库（方便扩充）
from dog_data import DOG_BREED_DATABASE, ALIAS_MAP


# ==============================================
# 全局配置 (常量定义)
# ==============================================
APP_VERSION = "v4.0"
APP_TITLE = f"🐶 智能犬种识别系统 {APP_VERSION}"
WINDOW_SIZE = "1200x800"
MIN_WINDOW_SIZE = (1000, 650)
CONFIDENCE_THRESHOLD = 0.001
TOP_K_PREDICTIONS = 6


# ==============================================
# 模型加载
# ==============================================
def load_model():
    try:
        weights = ResNet50_Weights.DEFAULT
        model = resnet50(weights=weights)
        model.eval()

        if torch.backends.mps.is_available():
            device = torch.device("mps")
            device_info = "Apple MPS (Mac芯片加速)"
        elif torch.cuda.is_available():
            device = torch.device("cuda")
            device_info = "NVIDIA CUDA (GPU加速)"
        else:
            device = torch.device("cpu")
            device_info = "CPU (通用模式)"

        model = model.to(device)
        print(f"✅ 模型加载成功，使用设备：{device_info}")

        preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        class_names = weights.meta["categories"]
        return model, preprocess, class_names, device
    except Exception as e:
        messagebox.showerror("模型加载失败", f"错误信息：{str(e)}\n请检查PyTorch和TorchVision是否安装正确")
        return None, None, None, None


# ==============================================
# 识别核心
# ==============================================
def normalize_breed_label(label):
    clean_label = re.sub(r"\(.*?\)|\d+", "", label)
    clean_label = clean_label.replace("_", " ")
    clean_label = re.sub(r"[,/;:-]+", " ", clean_label)
    clean_label = re.sub(r"\s+", " ", clean_label)
    return clean_label.strip().lower()


def format_breed_label(label):
    clean_label = normalize_breed_label(label)
    if not clean_label:
        return "未知犬种"
    return " ".join(word.capitalize() for word in clean_label.split())


def build_fallback_breed_info(raw_label):
    display_label = format_breed_label(raw_label)
    return {
        "name": f"（{display_label}）",
        "alias": f"模型标签：{display_label}",
        "type": "待确认", "size_desc": "百科待补充", "adaptability": "★★★☆☆",
        "height": "待补充", "weight": "待补充", "life_span": "待补充",
        "character": "模型已经识别出疑似犬种，但当前百科库暂未收录该犬种的详细资料。",
        "appearance": f"模型识别标签为 {display_label}，建议结合图片外观继续确认。",
        "origin": "待补充",
        "history": "当前版本的犬类百科尚未覆盖该犬种，后续可继续扩充资料库。",
        "feeding": "可先参考常规科学养犬原则：按体型喂食、定期驱虫、保证运动和饮水。",
        "health": "不同犬种常见疾病差异较大，建议咨询宠物医生或补充该犬种百科数据。",
        "care": "建议根据毛发长度、体型和活动量进行日常护理，并补充该犬种专属信息。",
        "feature": "本次结果来自模型识别，但属于百科未收录犬种，因此先展示模型结果供你参考。",
        "suit_crowd": "待补充"
    }


def predict_image(img_path, model, preprocess, classes, device):
    try:
        img = Image.open(img_path).convert("RGB")
        input_tensor = preprocess(img).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            top_probs, top_indices = torch.topk(probabilities, TOP_K_PREDICTIONS)

        matched_results = []
        fallback_results = []
        seen_labels = set()

        for i in range(TOP_K_PREDICTIONS):
            idx = top_indices[0][i].item()
            prob = top_probs[0][i].item()
            if prob < CONFIDENCE_THRESHOLD:
                continue
            raw_class_name = classes[idx]
            normalized_label = normalize_breed_label(raw_class_name)
            if not normalized_label or normalized_label in seen_labels:
                continue
            seen_labels.add(normalized_label)

            breed = find_breed(raw_class_name)
            if breed:
                matched_results.append({
                    "name": breed["name"], "prob": prob,
                    "info": dict(breed), "is_fallback": False,
                    "raw_class": raw_class_name
                })
            else:
                fallback_info = build_fallback_breed_info(raw_class_name)
                fallback_results.append({
                    "name": fallback_info["name"], "prob": prob,
                    "info": fallback_info, "is_fallback": True,
                    "raw_class": raw_class_name
                })

        final_results = matched_results if matched_results else fallback_results
        return sorted(final_results, key=lambda x: -x["prob"])
    except Exception as e:
        messagebox.showerror("识别失败", f"图片处理出错：{str(e)}\n请选择清晰的狗狗图片")
        return []


def find_breed(pred_str):
    clean_pred = normalize_breed_label(pred_str)
    if not clean_pred:
        return None
    if clean_pred in DOG_BREED_DATABASE:
        return DOG_BREED_DATABASE[clean_pred]
    if clean_pred in ALIAS_MAP:
        return DOG_BREED_DATABASE[ALIAS_MAP[clean_pred]]
    pred_words = set(clean_pred.split())
    for breed_key, breed_info in DOG_BREED_DATABASE.items():
        breed_words = set(normalize_breed_label(breed_key).split())
        alias_words = set(normalize_breed_label(breed_info["alias"]).split())
        if pred_words & (breed_words | alias_words):
            return breed_info
    return None


# ==============================================
# GUI 主界面
# ==============================================
class DogRecognitionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_WINDOW_SIZE)
        self.configure(bg="#f5f5f5")

        self.model, self.preprocess, self.classes, self.device = load_model()
        if not self.model:
            self.quit()

        self.img_path = None
        self.results = []
        self.original_image = None
        self.display_image = None
        self.selected_idx = None

        self.build_ui()

    # --------------------------------------------------
    # UI 构建
    # --------------------------------------------------
    def build_ui(self):
        # 顶部标题栏
        top_frame = tk.Frame(self, bg="#2c3e50", height=80)
        top_frame.pack(fill="x", side="top", padx=10, pady=10)
        top_frame.pack_propagate(False)
        tk.Label(
            top_frame, text="🐶 智能犬种识别系统",
            font=("微软雅黑", 24, "bold"), bg="#2c3e50", fg="white"
        ).pack(pady=15)

        # 主容器
        main_container = tk.Frame(self, bg="#f5f5f5")
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # 左侧：图片显示
        left_frame = tk.Frame(main_container, bg="white", relief="solid", bd=1, width=550)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        tk.Label(
            left_frame, text="📸 待识别图片（完整显示）",
            font=("微软雅黑", 16, "bold"), bg="white", fg="#333"
        ).pack(pady=10)

        self.img_panel = tk.Label(
            left_frame, bg="#f0f0f0",
            text="请点击「选择图片」加载狗狗照片",
            font=("微软雅黑", 14), fg="#666"
        )
        self.img_panel.pack(fill="both", expand=True, padx=20, pady=10)

        # 右侧：识别结果
        right_frame = tk.Frame(main_container, bg="white", relief="solid", bd=1, width=550)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        tk.Label(
            right_frame, text="📊 识别结果（双击查看详情）",
            font=("微软雅黑", 16, "bold"), bg="white", fg="#333"
        ).pack(pady=(10, 5))

        # 表头
        header_frame = tk.Frame(right_frame, bg="#ecf0f1", height=40)
        header_frame.pack(fill="x", padx=10)
        header_frame.pack_propagate(False)
        for text, width in [("排名", 5), ("犬种名称", 14), ("识别概率（从大到小排序）", 19), ("体型", 8)]:
            tk.Label(
                header_frame, text=text,
                font=("微软雅黑", 11, "bold"),
                bg="#ecf0f1", fg="#2c3e50", width=width
            ).pack(side="left", padx=4)

        # 结果列表（Canvas + 滚动条）
        self.result_container = tk.Frame(right_frame, bg="white", height=500)
        self.result_container.pack(fill="both", expand=True, padx=10, pady=5)
        self.result_container.pack_propagate(False)

        self.result_canvas = tk.Canvas(self.result_container, bg="white", highlightthickness=0)
        self.result_scrollbar = tk.Scrollbar(
            self.result_container, orient="vertical", command=self.result_canvas.yview
        )
        self.result_inner = tk.Frame(self.result_canvas, bg="white")

        self.result_canvas.configure(yscrollcommand=self.result_scrollbar.set)
        self.result_scrollbar.pack(side="right", fill="y")
        self.result_canvas.pack(side="left", fill="both", expand=True)

        self.result_canvas_window = self.result_canvas.create_window(
            (0, 0), window=self.result_inner, anchor="nw"
        )
        self.result_inner.bind(
            "<Configure>",
            lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all"))
        )
        self.result_canvas.bind("<Configure>", self.on_result_canvas_configure)

        # 右键菜单
        self.result_menu = tk.Menu(self, tearoff=0)
        self.result_menu.add_command(label="查看详情", command=self.show_detail_from_menu)

        # 底部按钮栏
        btn_frame = tk.Frame(self, bg="#f5f5f5", height=70)
        btn_frame.pack(fill="x", padx=10, pady=5)
        btn_frame.pack_propagate(False)

        tk.Button(
            btn_frame, text="📁 选择图片", command=self.select_image,
            font=("微软雅黑", 13, "bold"), width=20, height=2,
            bg="#3498db", fg="white", relief="flat", cursor="hand2"
        ).pack(side="left", padx=20, pady=10)

        tk.Button(
            btn_frame, text="🔍 开始识别", command=self.start_recognize,
            font=("微软雅黑", 13, "bold"), width=20, height=2,
            bg="#2ecc71", fg="white", relief="flat", cursor="hand2"
        ).pack(side="left", padx=20, pady=10)

        self.status_label = tk.Label(
            btn_frame, text="✅ 系统就绪 | 请选择狗狗图片",
            font=("微软雅黑", 12), bg="#f5f5f5", fg="#2c3e50"
        )
        self.status_label.pack(side="right", padx=30, pady=10)

    # --------------------------------------------------
    # 图片选择
    # --------------------------------------------------
    def select_image(self):
        path = filedialog.askopenfilename(
            title="选择狗狗照片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        if not path:
            return
        self.img_path = path
        try:
            self.original_image = Image.open(path).convert("RGB")
            self.update_idletasks()
            panel_w = self.img_panel.winfo_width() or 480
            panel_h = self.img_panel.winfo_height() or 400
            display_img = self.original_image.copy()
            display_img.thumbnail((panel_w - 40, panel_h - 40), Image.Resampling.LANCZOS)
            self.display_image = ImageTk.PhotoImage(display_img)
            self.img_panel.config(image=self.display_image, text="", bg="white")
            self.img_panel.image = self.display_image
            self.status_label.config(text=f"✅ 图片已加载 | {os.path.basename(path)}")
            for w in self.result_inner.winfo_children():
                w.destroy()
            self.results = []
        except Exception as e:
            messagebox.showerror("图片加载失败", f"{str(e)}")

    # --------------------------------------------------
    # 识别
    # --------------------------------------------------
    def start_recognize(self):
        if not self.img_path:
            messagebox.showwarning("提示", "请先选择狗狗图片再进行识别！")
            return
        self.status_label.config(text="🔍 正在识别中，请稍候...")
        for w in self.result_inner.winfo_children():
            w.destroy()
        self.result_canvas.yview_moveto(0)
        self.update_idletasks()

        def task():
            try:
                res = predict_image(self.img_path, self.model, self.preprocess, self.classes, self.device)
                self.after(0, self.show_recognition_results, res)
            except Exception as e:
                self.after(0, self.handle_recognition_error, str(e))

        threading.Thread(target=task, daemon=True).start()

    def handle_recognition_error(self, msg):
        self.results = []
        self.selected_idx = None
        self.status_label.config(text="❌ 识别失败")
        messagebox.showerror("识别失败", msg)

    def on_result_canvas_configure(self, event):
        self.result_canvas.itemconfigure(self.result_canvas_window, width=event.width)

    # --------------------------------------------------
    # 展示识别结果
    # --------------------------------------------------
    def show_recognition_results(self, results):
        self.results = results
        if not results:
            self.status_label.config(text="❌ 未识别到有效犬种 | 请更换清晰的狗狗图片")
            return

        self.selected_idx = None

        def get_prob_color(p):
            if p >= 0.8:   return "#27ae60"
            elif p >= 0.5: return "#f39c12"
            elif p >= 0.2: return "#e67e22"
            else:           return "#e74c3c"

        type_colors = {
            "大型犬": "#8e44ad", "中型犬": "#2980b9",
            "小型犬": "#16a085", "超小型犬": "#d35400"
        }

        for idx, item in enumerate(results):
            breed_name = item["name"]
            probability = item["prob"]
            breed_type = item["info"].get("type", "未知")
            row_bg = "#f8f9fa" if idx % 2 == 0 else "white"

            row = tk.Frame(self.result_inner, bg=row_bg, height=60)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            rank_lbl = tk.Label(
                row, text=f"{idx+1}",
                font=("微软雅黑", 16, "bold"),
                bg=row_bg, fg="#2c3e50", width=5
            )
            rank_lbl.pack(side="left", padx=(6, 2), anchor="center")

            name_lbl = tk.Label(
                row, text=breed_name,
                font=("微软雅黑", 13, "bold"),
                bg=row_bg, fg="#2c3e50",
                width=14, anchor="w", wraplength=130, justify="left"
            )
            name_lbl.pack(side="left", padx=5, anchor="center")

            prob_frame = tk.Frame(row, bg=row_bg, width=100)
            prob_frame.pack(side="left", padx=5, anchor="center")
            prob_frame.pack_propagate(False)

            prob_color = get_prob_color(probability)
            tk.Label(
                prob_frame, text=f"{int(probability * 100)}%",
                font=("微软雅黑", 15, "bold"),
                bg=row_bg, fg=prob_color
            ).pack(anchor="center", pady=(4, 2))

            bar_bg = tk.Frame(prob_frame, bg="#e0e0e0", height=6, width=80)
            bar_bg.pack(anchor="center")
            bar_fill_w = max(4, int(80 * probability))
            tk.Frame(bar_bg, bg=prob_color, height=6, width=bar_fill_w).place(x=0, y=0)

            type_color = type_colors.get(breed_type, "#7f8c8d")
            type_lbl = tk.Label(
                row, text=breed_type,
                font=("微软雅黑", 12, "bold"),
                bg=row_bg, fg=type_color, width=8
            )
            type_lbl.pack(side="left", padx=5, anchor="center")

            for widget in [row, rank_lbl, name_lbl, prob_frame, type_lbl]:
                widget.bind("<Button-1>", lambda e, i=idx: self.on_result_click(i))
                widget.bind("<Double-Button-1>", lambda e, i=idx: self.show_detail_from_idx(i))
                widget.bind("<Button-3>", lambda e: self.result_menu.post(e.x_root, e.y_root))

        self.result_canvas.update_idletasks()
        self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all"))

        showing_fallback = all(item.get("is_fallback") for item in results)
        if showing_fallback:
            self.status_label.config(
                text=f"✅ 识别完成 | 百科未收录，已展示 {len(results)} 条模型结果"
            )
        else:
            self.status_label.config(
                text=f"✅ 识别完成 | 共识别到 {len(results)} 个可能犬种（双击查看详情）"
            )

    # --------------------------------------------------
    # 点击 / 详情
    # --------------------------------------------------
    def on_result_click(self, idx):
        self.selected_idx = idx

    def show_detail_from_idx(self, idx):
        if 0 <= idx < len(self.results):
            self.show_detail_window_by_idx(idx)

    def show_detail_from_menu(self):
        if self.selected_idx is None:
            messagebox.showinfo("提示", "请先单击一条识别结果，再查看详情。")
            return
        self.show_detail_window_by_idx(self.selected_idx)

    def show_detail_window_by_idx(self, idx):
        if idx is None or not (0 <= idx < len(self.results)):
            return
        selected_breed = self.results[idx]
        breed_info = selected_breed["info"]
        probability = f"{selected_breed['prob']:.2%}"

        detail_win = tk.Toplevel(self)
        detail_win.title(f"🐾 {breed_info['name']} - 详细信息")
        detail_win.geometry("750x700")
        detail_win.minsize(700, 650)
        detail_win.grab_set()
        detail_win.configure(bg="#f5f5f5")

        # 顶部标题 + 概率徽章
        title_card = tk.Frame(detail_win, bg="white", relief="flat", bd=0)
        title_card.pack(fill="x", padx=15, pady=(15, 10))

        prob_percent = selected_breed["prob"]
        prob_color = "#27ae60" if prob_percent >= 0.5 else "#f39c12" if prob_percent >= 0.2 else "#e74c3c"
        prob_badge = tk.Frame(title_card, bg=prob_color, padx=15, pady=8)
        prob_badge.pack(side="right", padx=10)
        tk.Label(prob_badge, text=f"识别概率 {probability}",
                 font=("微软雅黑", 12, "bold"), bg=prob_color, fg="white").pack()

        tk.Label(title_card, text=f"🐾 {breed_info['name']}",
                 font=("微软雅黑", 22, "bold"), bg="white", fg="#2c3e50").pack(side="left", padx=10)
        tk.Label(title_card, text=f"别名：{breed_info['alias']}",
                 font=("微软雅黑", 11), bg="white", fg="#7f8c8d").pack(side="left", anchor="s", padx=10)

        # 滚动区域
        content_canvas = tk.Canvas(detail_win, bg="#f5f5f5", highlightthickness=0)
        content_scroll = tk.Scrollbar(detail_win, orient="vertical", command=content_canvas.yview)
        content_frame = tk.Frame(content_canvas, bg="#f5f5f5")

        content_canvas.configure(yscrollcommand=content_scroll.set)
        content_scroll.pack(side="right", fill="y")
        content_canvas.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        content_canvas.create_window((0, 0), window=content_frame, anchor="nw")
        content_frame.bind("<Configure>",
            lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all")))

        def add_info_row(parent, label_text, value_text):
            row = tk.Frame(parent, bg="white")
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label_text, font=("微软雅黑", 11, "bold"),
                     bg="white", fg="#34495e", width=10, anchor="w").pack(side="left")
            tk.Label(row, text=value_text, font=("微软雅黑", 11),
                     bg="white", fg="#2c3e50", wraplength=480, justify="left").pack(side="left", fill="x", expand=True)

        # 基本信息 + 身材数据
        row1 = tk.Frame(content_frame, bg="#f5f5f5")
        row1.pack(fill="x", pady=(0, 10))

        card1 = tk.Frame(row1, bg="white", relief="flat", bd=0)
        card1.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tk.Frame(card1, bg="#3498db", padx=12, pady=8).pack(fill="x")
        tk.Label(card1.winfo_children()[0], text="📋 基本信息",
                 font=("微软雅黑", 13, "bold"), bg="#3498db", fg="white").pack(side="left")
        info_content = tk.Frame(card1, bg="white", padx=15, pady=12)
        info_content.pack(fill="x")
        add_info_row(info_content, "狗狗体型", breed_info["type"])

        type_colors_map = {"大型犬": "#8e44ad", "中型犬": "#2980b9",
                           "小型犬": "#16a085", "超小型犬": "#d35400"}
        type_color = type_colors_map.get(breed_info["type"], "#7f8c8d")
        tag_row = tk.Frame(info_content, bg="white")
        tag_row.pack(fill="x", pady=2)
        tk.Label(tag_row, text="类型标签：", font=("微软雅黑", 11, "bold"),
                 bg="white", fg="#34495e", width=10, anchor="w").pack(side="left")
        tag_badge = tk.Frame(tag_row, bg=type_color, padx=8, pady=3)
        tag_badge.pack(side="left")
        tk.Label(tag_badge, text=breed_info["size_desc"],
                 font=("微软雅黑", 10, "bold"), bg=type_color, fg="white").pack()

        add_info_row(info_content, "性格特点", breed_info["character"])
        star_row = tk.Frame(info_content, bg="white")
        star_row.pack(fill="x", pady=2)
        tk.Label(star_row, text="好养活指数", font=("微软雅黑", 11, "bold"),
                 bg="white", fg="#34495e", width=10, anchor="w").pack(side="left")
        adapt_desc = {
            "★★★☆☆": "一般好养，适合有经验的铲屎官",
            "★★★★☆": "比较好养，新手也能试试",
            "★★★★★": "超级好养，新手友好"
        }.get(breed_info["adaptability"], "一般")
        tk.Label(star_row, text=breed_info["adaptability"] + " " + adapt_desc,
                 font=("微软雅黑", 11), bg="white", fg="#27ae60").pack(side="left")

        card2 = tk.Frame(row1, bg="white", relief="flat", bd=0)
        card2.pack(side="right", fill="both", expand=True, padx=(5, 0))
        body_hdr = tk.Frame(card2, bg="#9b59b6", padx=12, pady=8)
        body_hdr.pack(fill="x")
        tk.Label(body_hdr, text="📏 身材数据",
                 font=("微软雅黑", 13, "bold"), bg="#9b59b6", fg="white").pack(side="left")
        body_content = tk.Frame(card2, bg="white", padx=15, pady=12)
        body_content.pack(fill="x")
        add_info_row(body_content, "成年身高", breed_info["height"])
        add_info_row(body_content, "成年体重", breed_info["weight"])
        add_info_row(body_content, "平均寿命", breed_info["life_span"])

        def make_card(parent, color, title, side="left"):
            f = tk.Frame(parent, bg="white", relief="flat", bd=0)
            f.pack(side=side, fill="both", expand=True,
                   padx=(0, 5) if side == "left" else (5, 0))
            hdr = tk.Frame(f, bg=color, padx=12, pady=8)
            hdr.pack(fill="x")
            tk.Label(hdr, text=title, font=("微软雅黑", 13, "bold"),
                     bg=color, fg="white").pack(side="left")
            body = tk.Frame(f, bg="white", padx=15, pady=12)
            body.pack(fill="x")
            return body

        row2 = tk.Frame(content_frame, bg="#f5f5f5")
        row2.pack(fill="x", pady=(0, 10))
        c3 = make_card(row2, "#e67e22", "🐕 性格和长相", "left")
        add_info_row(c3, "性格脾气", breed_info["character"])
        add_info_row(c3, "外表模样", breed_info["appearance"])
        c4 = make_card(row2, "#1abc9c", "🌍 来历故事", "right")
        add_info_row(c4, "出生地", breed_info["origin"])
        add_info_row(c4, "历史背景", breed_info["history"])

        row3 = tk.Frame(content_frame, bg="#f5f5f5")
        row3.pack(fill="x", pady=(0, 10))
        c5 = make_card(row3, "#e74c3c", "🍖 喂养方式", "left")
        tk.Label(c5, text=breed_info["feeding"], font=("微软雅黑", 11),
                 bg="white", fg="#2c3e50", wraplength=330, justify="left").pack(fill="x")
        c6 = make_card(row3, "#f39c12", "🏥 健康护理", "right")
        add_info_row(c6, "常见毛病", breed_info["health"])
        add_info_row(c6, "护理要点", breed_info["care"])

        row4 = tk.Frame(content_frame, bg="#f5f5f5")
        row4.pack(fill="x", pady=(0, 10))
        c7 = make_card(row4, "#2ecc71", "✨ 特别之处", "left")
        tk.Label(c7, text=breed_info["feature"], font=("微软雅黑", 11),
                 bg="white", fg="#2c3e50", wraplength=330, justify="left").pack(fill="x")
        c8 = make_card(row4, "#34495e", "👨‍👩‍👧‍👦 适合人群", "right")
        tk.Label(c8, text=breed_info["suit_crowd"], font=("微软雅黑", 11),
                 bg="white", fg="#2c3e50", wraplength=330, justify="left").pack(fill="x")

        # 关闭按钮
        btn_frame = tk.Frame(content_frame, bg="#f5f5f5", pady=10)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="关闭", command=detail_win.destroy,
                  font=("微软雅黑", 12), bg="#95a5a6", fg="white",
                  padx=30, pady=8, relief="flat", cursor="hand2").pack()


# ==============================================
# 启动
# ==============================================
if __name__ == "__main__":
    app = DogRecognitionApp()
    app.mainloop()
