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
import requests
from io import BytesIO

# ==============================================
# 全局配置 (常量定义)
# ==============================================
APP_VERSION = "v4.0"
APP_TITLE = f"🐶 智能犬种识别系统 {APP_VERSION}"
WINDOW_SIZE = "1200x800"
MIN_WINDOW_SIZE = (1000, 650)
CONFIDENCE_THRESHOLD = 0.001
TOP_K_PREDICTIONS = 6  # 固定显示前6个，和你要的效果一致
IMAGE_CACHE = {}  # 图片缓存，避免重复加载

# ==============================================
# 🔥 超大容量犬种数据库（带图片URL）
# ==============================================
DOG_BREED_DATABASE = {
    "siberian husky": {
        "name": "西伯利亚哈士奇", "alias": "二哈、哈士奇、西伯利亚雪橇犬",
        "type": "中型犬", "size_desc": "精力旺盛型", "adaptability": "★★★☆☆",
        "height": "50～60cm", "weight": "16～27kg", "life_span": "12～15年",
        "character": "活泼、调皮、神经质、无攻击性、爱嚎叫",
        "appearance": "双层长毛、黑白/灰白/红棕、蓝眼/异瞳、立耳",
        "origin": "俄罗斯西伯利亚地区", "history": "曾是极地雪橇犬，负责拉雪橇、运输物资，适应极寒环境",
        "feeding": "每天运动2小时+；肠胃脆弱，需喂专用粮；注意掉毛；禁止喂牛奶、巧克力",
        "health": "白内障、髋关节发育不良、肠胃敏感、皮肤病",
        "care": "定期梳毛（每周2-3次）；训练要有耐心；避免高温环境；定期驱虫",
        "feature": "网红“拆家担当”，表情包大户，智商在线但服从性差，对陌生人友好",
        "suit_crowd": "有大量时间遛狗、喜欢活泼犬种的年轻人，不适合公寓和懒人",
        "img_url": "https://images.unsplash.com/photo-1587302906053-62c99e37778f?w=300&h=200&fit=crop"
    },
    "alaskan malamute": {
        "name": "阿拉斯加雪橇犬", "alias": "阿拉斯加、阿拉、巨型雪橇犬",
        "type": "大型犬", "size_desc": "巨型温柔巨人", "adaptability": "★★★☆☆",
        "height": "58～71cm", "weight": "34～56kg", "life_span": "10～15年",
        "character": "稳重、温顺、忠诚、无攻击性、粘人、不爱嚎叫",
        "appearance": "双层厚毛、灰白/黑白/红棕、体型巨大、立耳、尾巴卷曲",
        "origin": "美国阿拉斯加州", "history": "极地重型雪橇犬，力量惊人，曾帮助人类在极地生存",
        "feeding": "每日运动1.5小时；控制食量防肥胖；海鲜过敏，避免喂食海鲜；补充维生素",
        "health": "肠胃疾病、关节问题、肥胖、眼部疾病",
        "care": "每天梳毛（掉毛严重）；夏天注意降温；适合大空间家庭；定期体检",
        "feature": "体型比哈士奇大，性格更稳重，是完美的家庭护卫犬，对儿童友好",
        "suit_crowd": "有大院子、有时间照顾、喜欢大型犬的家庭",
        "img_url": "https://images.unsplash.com/photo-1598460592787-c70218d9d458?w=300&h=200&fit=crop"
    },
    "border collie": {
        "name": "边境牧羊犬", "alias": "边牧、边境柯利、柯利犬",
        "type": "中型犬", "size_desc": "智商天花板", "adaptability": "★★★★☆",
        "height": "46～56cm", "weight": "12～20kg", "life_span": "12～15年",
        "character": "极聪明、活泼、粘人、善解人意、学习能力超强、服从性高",
        "appearance": "黑白/蓝陨石/红白，长毛/短毛、立耳/半立耳、体型匀称",
        "origin": "英国苏格兰边境", "history": "世界顶级牧羊犬，牧羊效率极高，能快速响应主人指令",
        "feeding": "脑力+体力双重运动；每天1.5小时；不能长期圈养；补充蛋白质",
        "health": "癫痫、眼部疾病、髋关节问题、皮肤过敏",
        "care": "定期训练（避免无聊拆家）；清洁毛发；注意皮肤护理；多互动",
        "feature": "犬类智商排名第一，能听懂上千指令，是工作犬与飞盘犬之王，对人友好",
        "suit_crowd": "喜欢训练犬只、有时间陪伴、有一定饲养经验的人",
        "img_url": "https://images.unsplash.com/photo-1587302906053-62c99e37778f?w=300&h=200&fit=crop"
    },
    "german shepherd": {
        "name": "德国牧羊犬", "alias": "德牧、黑背、狼狗、德国狼犬",
        "type": "中型犬", "size_desc": "万能工作犬", "adaptability": "★★★★☆",
        "height": "55～65cm", "weight": "22～40kg", "life_span": "9～13年",
        "character": "忠诚、勇敢、警惕、护主、服从性高、智商高",
        "appearance": "黑背黄腹、短毛/长毛、体型挺拔、立耳、眼神锐利",
        "origin": "德国", "history": "军警界最主流犬种，参与过一战二战，用于警戒、搜救、缉毒",
        "feeding": "每天运动1.5小时；补钙（幼犬重点）；控制体重；避免过量喂食",
        "health": "髋关节发育不良、胃胀气、皮肤病、关节炎",
        "care": "严格社会化训练（避免攻击性）；梳毛；清洁耳朵；定期驱虫",
        "feature": "“万能工作犬”，警犬、军犬、搜救犬、导盲犬首选，护主意识极强",
        "suit_crowd": "有饲养经验、需要护卫犬、能坚持训练的人，不适合新手",
        "img_url": "https://images.unsplash.com/photo-1587302906053-62c99e37778f?w=300&h=200&fit=crop"
    },
    "golden retriever": {
        "name": "金毛寻回犬", "alias": "金毛、黄金猎犬、大暖男",
        "type": "中型犬", "size_desc": "阳光暖男型", "adaptability": "★★★★★",
        "height": "55～61cm", "weight": "25～34kg", "life_span": "10～12年",
        "character": "温顺、友善、无攻击性、粘人、笑容治愈、对儿童极友好",
        "appearance": "金黄色长毛、垂耳、眼神温柔、体型匀称、尾巴自然下垂",
        "origin": "英国苏格兰", "history": "曾是猎捕水鸟的助手，负责寻回猎物，性格温顺被广泛作为伴侣犬",
        "feeding": "每天运动1小时；防肥胖（易发胖）；防皮肤病；补充卵磷脂",
        "health": "髋关节、心脏病、皮肤病、泪痕",
        "care": "每天梳毛（掉毛严重）；清洁脚掌；注意泪痕；定期洗澡",
        "feature": "三大无攻击性犬之首，家庭宠物首选，导盲犬、搜救犬常客，对陌生人友好",
        "suit_crowd": "家庭、老人、新手，适合公寓和有孩子的家庭",
        "img_url": "https://images.unsplash.com/photo-1558788353-f76d92427f16?w=300&h=200&fit=crop"
    },
    "labrador retriever": {
        "name": "拉布拉多", "alias": "拉拉、拉布拉多寻回犬、吃货犬",
        "type": "中型犬", "size_desc": "乐天派吃货", "adaptability": "★★★★★",
        "height": "55～62cm", "weight": "25～36kg", "life_span": "10～12年",
        "character": "活泼、温顺、贪吃、无攻击性、热情、对人零防备",
        "appearance": "短毛、黑/黄/巧克力色、肌肉发达、垂耳、尾巴粗壮",
        "origin": "加拿大纽芬兰", "history": "渔民助手，拉渔网、寻回落水物品，后成为伴侣犬和工作犬",
        "feeding": "严格控食（贪吃易肥胖）；每天运动1小时；补充钙和维生素",
        "health": "肥胖、关节问题、眼部疾病、髋关节发育不良",
        "care": "短毛易打理（每周梳毛1次）；训练定点如厕；多陪伴（避免孤独）",
        "feature": "性格最稳定的犬种，导盲犬与缉毒犬首选，适合各种人群，无体味",
        "suit_crowd": "家庭、新手、老人、需要工作犬的人，适配各种居住环境",
        "img_url": "https://images.unsplash.com/photo-1593002303866-549216614b61?w=300&h=200&fit=crop"
    },
    "pembroke welsh corgi": {
        "name": "彭布罗克威尔士柯基", "alias": "柯基、短尾柯基、女王犬、短腿基",
        "type": "小型犬", "size_desc": "短腿萌物", "adaptability": "★★★★☆",
        "height": "25～30cm", "weight": "10～14kg", "life_span": "12～15年",
        "character": "活泼、亲人、聪明、粘人、护主、爱撒娇",
        "appearance": "短毛、三色/红棕色、无尾/短尾、短腿、大屁股、立耳",
        "origin": "英国威尔士", "history": "英国王室专属犬种，曾是牧羊犬，负责驱赶牛羊",
        "feeding": "控制食量（易发胖）；防腰椎病（短腿易受伤）；定期梳毛；避免高糖食物",
        "health": "腰椎间盘突出、肥胖、眼疾、皮肤过敏",
        "care": "避免爬楼梯（伤腰椎）；少食多餐；清洁屁股（易沾粪便）；定期剪指甲",
        "feature": "网红短腿犬，臀大腿短，英国女王最爱，适合城市饲养，对儿童友好",
        "suit_crowd": "城市白领、家庭、新手，适合公寓饲养",
        "img_url": "https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?w=300&h=200&fit=crop"
    },
    "shiba inu": {
        "name": "柴犬", "alias": "日本柴犬、小豆柴、秋田犬",
        "type": "中型犬", "size_desc": "微笑柴柴", "adaptability": "★★★★☆",
        "height": "35～41cm", "weight": "8～11kg", "life_span": "12～15年",
        "character": "独立、倔强、聪明、爱干净、表情丰富",
        "appearance": "短毛、赤柴/黑柴/白柴、立耳、三角眼、尾巴卷曲",
        "origin": "日本", "history": "日本本土犬种，曾是狩猎犬，后成为伴侣犬",
        "feeding": "每天运动30分钟；控制食量；定期梳毛；避免高盐食物",
        "health": "过敏、眼部疾病、髋关节问题",
        "care": "定期梳毛；训练要有耐心；适合公寓饲养",
        "feature": "表情包大户，性格独立，不爱粘人，颜值高",
        "suit_crowd": "喜欢安静、有一定饲养经验的人",
        "img_url": "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=300&h=200&fit=crop"
    }
}

# ==============================================
# 别名映射
# ==============================================
ALIAS_MAP = {
    "husky": "siberian husky", "siberian": "siberian husky",
    "alaskan": "alaskan malamute", "malamute": "alaskan malamute",
    "border": "border collie", "bc": "border collie",
    "german shepherd dog": "german shepherd", "gsd": "german shepherd",
    "alsatian": "german shepherd",
    "golden": "golden retriever", "retriever": "golden retriever",
    "lab": "labrador retriever", "labrador": "labrador retriever",
    "corgi": "pembroke welsh corgi", "pembroke": "pembroke welsh corgi",
    "shiba": "shiba inu", "柴犬": "shiba inu"
}

# ==============================================
# 图片加载工具
# ==============================================
def load_breed_image(url, size=(150, 80)):
    """加载犬种图片，带缓存"""
    cache_key = url or f"placeholder-{size[0]}x{size[1]}"
    if cache_key in IMAGE_CACHE:
        return IMAGE_CACHE[cache_key]
    try:
        if not url:
            raise ValueError("empty image url")
        response = requests.get(url, timeout=2)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img.thumbnail(size, Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        IMAGE_CACHE[cache_key] = tk_img
        return tk_img
    except Exception:
        placeholder = Image.new("RGB", size, color="#f0f0f0")
        tk_placeholder = ImageTk.PhotoImage(placeholder)
        IMAGE_CACHE[cache_key] = tk_placeholder
        return tk_placeholder

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
    """统一清洗模型标签，提升匹配成功率"""
    clean_label = re.sub(r"\(.*?\)|\d+", "", label)
    clean_label = clean_label.replace("_", " ")
    clean_label = re.sub(r"[,/;:-]+", " ", clean_label)
    clean_label = re.sub(r"\s+", " ", clean_label)
    return clean_label.strip().lower()


def format_breed_label(label):
    """把模型标签整理成便于展示的格式"""
    clean_label = normalize_breed_label(label)
    if not clean_label:
        return "未知犬种"
    return " ".join(word.capitalize() for word in clean_label.split())


def build_fallback_breed_info(raw_label):
    """当百科库未收录该犬种时，生成可展示的兜底信息"""
    display_label = format_breed_label(raw_label)
    return {
        "name": f"待补充犬种（{display_label}）",
        "alias": f"模型标签：{display_label}",
        "type": "待确认",
        "size_desc": "百科待补充",
        "adaptability": "★★★☆☆",
        "height": "待补充",
        "weight": "待补充",
        "life_span": "待补充",
        "character": "模型已经识别出疑似犬种，但当前百科库暂未收录该犬种的详细资料。",
        "appearance": f"模型识别标签为 {display_label}，建议结合图片外观继续确认。",
        "origin": "待补充",
        "history": "当前版本的犬类百科尚未覆盖该犬种，后续可继续扩充资料库。",
        "feeding": "可先参考常规科学养犬原则：按体型喂食、定期驱虫、保证运动和饮水。",
        "health": "不同犬种常见疾病差异较大，建议咨询宠物医生或补充该犬种百科数据。",
        "care": "建议根据毛发长度、体型和活动量进行日常护理，并补充该犬种专属信息。",
        "feature": "本次结果来自模型识别，但属于百科未收录犬种，因此先展示模型结果供你参考。",
        "suit_crowd": "待补充",
        "img_url": "",
        "raw_label": display_label
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
                breed_info = dict(breed)
                matched_results.append({
                    "name": breed_info["name"],
                    "prob": prob,
                    "info": breed_info,
                    "is_fallback": False,
                    "raw_class": raw_class_name
                })
            else:
                fallback_info = build_fallback_breed_info(raw_class_name)
                fallback_results.append({
                    "name": fallback_info["name"],
                    "prob": prob,
                    "info": fallback_info,
                    "is_fallback": True,
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
# GUI 主界面（最终修复版：带图片+完美布局）
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
        self.row_images = []  # 保存图片引用，防止被GC回收

        self.build_ui()

    def build_ui(self):
        # 顶部标题栏
        top_frame = tk.Frame(self, bg="#2c3e50", height=80)
        top_frame.pack(fill="x", side="top", padx=10, pady=10)
        top_frame.pack_propagate(False)

        title_label = tk.Label(
            top_frame, text="🐶 智能犬种识别系统",
            font=("微软雅黑", 24, "bold"), bg="#2c3e50", fg="white"
        )
        title_label.pack(pady=15)

        # 主容器：左右分栏（Frame+pack，彻底解决布局问题）
        main_container = tk.Frame(self, bg="#f5f5f5")
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # 左侧：图片显示
        left_frame = tk.Frame(main_container, bg="white", relief="solid", bd=1, width=550)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        img_title = tk.Label(
            left_frame, text="📸 待识别图片（完整显示）",
            font=("微软雅黑", 16, "bold"), bg="white", fg="#333"
        )
        img_title.pack(pady=10)

        self.img_panel = tk.Label(
            left_frame, bg="#f0f0f0", text="请点击「选择图片」加载狗狗照片",
            font=("微软雅黑", 14), fg="#666"
        )
        self.img_panel.pack(fill="both", expand=True, padx=20, pady=10)

        # 右侧：识别结果
        right_frame = tk.Frame(main_container, bg="white", relief="solid", bd=1, width=550)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        res_title = tk.Label(
            right_frame, text="📊 识别结果（双击查看详情）",
            font=("微软雅黑", 16, "bold"), bg="white", fg="#333"
        )
        res_title.pack(pady=(10, 5))

        # 表头（和你要的效果完全对齐）
        header_frame = tk.Frame(right_frame, bg="#ecf0f1", height=40)
        header_frame.pack(fill="x", padx=10)
        header_frame.pack_propagate(False)
        
        # 表头列宽完全匹配
        tk.Label(header_frame, text="排名", font=("微软雅黑", 11, "bold"), 
                bg="#ecf0f1", fg="#2c3e50", width=6).pack(side="left", padx=(5, 0))
        tk.Label(header_frame, text="犬种图片", font=("微软雅黑", 11, "bold"), 
                bg="#ecf0f1", fg="#2c3e50", width=18).pack(side="left", padx=5)
        tk.Label(header_frame, text="犬种名称", font=("微软雅黑", 11, "bold"), 
                bg="#ecf0f1", fg="#2c3e50", width=12).pack(side="left", padx=5)
        tk.Label(header_frame, text="识别概率", font=("微软雅黑", 11, "bold"), 
                bg="#ecf0f1", fg="#2c3e50", width=10).pack(side="left", padx=5)
        tk.Label(header_frame, text="体型", font=("微软雅黑", 11, "bold"), 
                bg="#ecf0f1", fg="#2c3e50", width=8).pack(side="left", padx=5)

        # 结果表格容器（带滚动条，固定高度）
        self.result_container = tk.Frame(right_frame, bg="white", height=500)
        self.result_container.pack(fill="both", expand=True, padx=10, pady=5)
        self.result_container.pack_propagate(False)

        self.result_canvas = tk.Canvas(self.result_container, bg="white", highlightthickness=0)
        self.result_scrollbar = tk.Scrollbar(self.result_container, orient="vertical",
                                            command=self.result_canvas.yview)
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

        select_btn = tk.Button(
            btn_frame, text="📁 选择图片", command=self.select_image,
            font=("微软雅黑", 13, "bold"), width=20, height=2,
            bg="#3498db", fg="white", relief="flat", cursor="hand2"
        )
        select_btn.pack(side="left", padx=20, pady=10)

        run_btn = tk.Button(
            btn_frame, text="🔍 开始识别", command=self.start_recognize,
            font=("微软雅黑", 13, "bold"), width=20, height=2,
            bg="#2ecc71", fg="white", relief="flat", cursor="hand2"
        )
        run_btn.pack(side="left", padx=20, pady=10)

        self.status_label = tk.Label(
            btn_frame, text="✅ 系统就绪 | 请选择狗狗图片",
            font=("微软雅黑", 12), bg="#f5f5f5", fg="#2c3e50"
        )
        self.status_label.pack(side="right", padx=30, pady=10)

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
            panel_width = self.img_panel.winfo_width()
            panel_height = self.img_panel.winfo_height()
            display_size = (panel_width - 40, panel_height - 40)
            display_img = self.original_image.copy()
            display_img.thumbnail(display_size, Image.Resampling.LANCZOS)

            self.display_image = ImageTk.PhotoImage(display_img)
            self.img_panel.config(image=self.display_image, text="", bg="white")
            setattr(self.img_panel, "image", self.display_image)

            self.status_label.config(text=f"✅ 图片已加载 | 路径：{os.path.basename(path)}")
            # 清空旧结果
            for widget in self.result_inner.winfo_children():
                widget.destroy()
            self.row_images.clear()
            self.results = []

        except Exception as e:
            messagebox.showerror("图片加载失败", f"错误信息：{str(e)}\n请选择格式正确的图片")
            self.original_image = None
            self.display_image = None

    def start_recognize(self):
        if not self.img_path:
            messagebox.showwarning("提示", "请先选择狗狗图片再进行识别！")
            return

        self.status_label.config(text="🔍 正在识别中，请稍候...")
        for widget in self.result_inner.winfo_children():
            widget.destroy()
        self.row_images.clear()
        self.result_canvas.yview_moveto(0)
        self.update_idletasks()

        def recognition_task():
            try:
                res = predict_image(self.img_path, self.model, self.preprocess, self.classes, self.device)
                self.after(0, self.show_recognition_results, res)
            except Exception as e:
                self.after(0, self.handle_recognition_error, str(e))

        threading.Thread(target=recognition_task, daemon=True).start()

    def handle_recognition_error(self, error_message):
        self.results = []
        self.selected_idx = None
        self.status_label.config(text="❌ 识别失败 | 请查看错误提示")
        messagebox.showerror("识别失败", f"图片处理出错：{error_message}\n请尝试更换图片或检查模型环境。")

    def on_result_canvas_configure(self, event):
        self.result_canvas.itemconfigure(self.result_canvas_window, width=event.width)

    def show_recognition_results(self, results):
        self.results = results
        if not results:
            self.status_label.config(text="❌ 未识别到有效犬种 | 请更换清晰的狗狗图片")
            return

        self.selected_idx = None
        showing_fallback = all(item.get("is_fallback") for item in results)

        # 概率颜色梯度
        def get_prob_color(prob):
            if prob >= 0.8:
                return "#27ae60"
            elif prob >= 0.5:
                return "#f39c12"
            elif prob >= 0.2:
                return "#e67e22"
            else:
                return "#e74c3c"

        for idx, item in enumerate(results):
            breed_name = item["name"]
            probability = item['prob']
            prob_text = f"{int(probability * 100)}%"
            breed_type = item['info'].get('type', '未知')
            breed_img_url = item['info'].get('img_url', "")

            row_bg = "#f8f9fa" if idx % 2 == 0 else "white"
            row = tk.Frame(self.result_inner, bg=row_bg, height=90)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            rank_label = tk.Label(row, text=f"{idx+1}", font=("微软雅黑", 16, "bold"),
                                  bg=row_bg, fg="#2c3e50", width=6)
            rank_label.pack(side="left", padx=(5, 0), anchor="center", fill="y")

            img_label = tk.Label(row, bg=row_bg)
            img_label.pack(side="left", padx=5, anchor="center", fill="y")
            breed_img = load_breed_image(breed_img_url, size=(150, 80))
            img_label.config(image=breed_img)
            setattr(img_label, "image", breed_img)
            self.row_images.append(breed_img)

            name_label = tk.Label(row, text=breed_name, font=("微软雅黑", 14, "bold"),
                                  bg=row_bg, fg="#2c3e50", width=12, anchor="w")
            name_label.pack(side="left", padx=5, anchor="center", fill="y")

            prob_color = get_prob_color(probability)
            prob_label = tk.Label(row, text=prob_text, font=("微软雅黑", 14, "bold"),
                                  bg=row_bg, fg=prob_color, width=10)
            prob_label.pack(side="left", padx=5, anchor="center", fill="y")

            type_colors = {"大型犬": "#8e44ad", "中型犬": "#2980b9",
                           "小型犬": "#16a085", "超小型犬": "#d35400"}
            type_color = type_colors.get(breed_type, "#7f8c8d")
            type_label = tk.Label(row, text=breed_type, font=("微软雅黑", 14, "bold"),
                                  bg=row_bg, fg=type_color, width=8)
            type_label.pack(side="left", padx=5, anchor="center", fill="y")

            for widget in [rank_label, img_label, name_label, prob_label, type_label, row]:
                widget.bind("<Button-1>", lambda e, i=idx: self.on_result_click(i))
                widget.bind("<Double-Button-1>", lambda e, i=idx: self.show_detail_from_idx(i))
                widget.bind("<Button-3>", lambda e: self.result_menu.post(e.x_root, e.y_root))

        self.result_canvas.update_idletasks()
        self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all"))

        if showing_fallback:
            self.status_label.config(text=f"✅ 识别完成 | 当前百科未收录该犬种，已展示 {len(results)} 条模型识别结果")
        else:
            self.status_label.config(text=f"✅ 识别完成 | 共识别到 {len(results)} 个可能犬种（双击查看详情）")

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

        # 顶部标题
        title_card = tk.Frame(detail_win, bg="white", relief="flat", bd=0)
        title_card.pack(fill="x", padx=15, pady=(15, 10))

        prob_percent = selected_breed['prob']
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

        # 信息行辅助函数
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

        # 基本信息卡片
        card1 = tk.Frame(row1, bg="white", relief="flat", bd=0)
        card1.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        info_header = tk.Frame(card1, bg="#3498db", padx=12, pady=8)
        info_header.pack(fill="x")
        tk.Label(info_header, text="📋 狗狗基本信息", font=("微软雅黑", 13, "bold"),
                bg="#3498db", fg="white").pack(side="left")
        
        info_content = tk.Frame(card1, bg="white", padx=15, pady=12)
        info_content.pack(fill="x")
        
        type_colors = {"大型犬": "#8e44ad", "中型犬": "#2980b9", 
                     "小型犬": "#16a085", "超小型犬": "#d35400"}
        type_color = type_colors.get(breed_info['type'], "#7f8c8d")
        
        add_info_row(info_content, "狗狗体型", breed_info['type'])
        
        type_tag = tk.Frame(info_content, bg="white")
        type_tag.pack(fill="x", pady=2)
        tk.Label(type_tag, text="类型标签：", font=("微软雅黑", 11, "bold"),
                bg="white", fg="#34495e", width=10, anchor="w").pack(side="left")
        type_badge = tk.Frame(type_tag, bg=type_color, padx=8, pady=3)
        type_badge.pack(side="left")
        tk.Label(type_badge, text=breed_info['size_desc'], 
                font=("微软雅黑", 10, "bold"), bg=type_color, fg="white").pack()
        
        add_info_row(info_content, "性格特点", breed_info['character'])
        
        star_row = tk.Frame(info_content, bg="white")
        star_row.pack(fill="x", pady=2)
        tk.Label(star_row, text="好养活指数", font=("微软雅黑", 11, "bold"),
                bg="white", fg="#34495e", width=10, anchor="w").pack(side="left")
        adaptability_desc = {
            "★★★☆☆": "一般好养，适合有经验的铲屎官",
            "★★★★☆": "比较好养，新手也能试试",
            "★★★★★": "超级好养，新手友好"
        }.get(breed_info['adaptability'], "一般")
        tk.Label(star_row, text=breed_info['adaptability'] + " " + adaptability_desc,
                font=("微软雅黑", 11), bg="white", fg="#27ae60").pack(side="left")

        # 身体数据卡片
        card2 = tk.Frame(row1, bg="white", relief="flat", bd=0)
        card2.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        body_header = tk.Frame(card2, bg="#9b59b6", padx=12, pady=8)
        body_header.pack(fill="x")
        tk.Label(body_header, text="📏 狗狗身材数据", font=("微软雅黑", 13, "bold"),
                bg="#9b59b6", fg="white").pack(side="left")
        
        body_content = tk.Frame(card2, bg="white", padx=15, pady=12)
        body_content.pack(fill="x")
        
        add_info_row(body_content, "成年身高", breed_info['height'])
        add_info_row(body_content, "成年体重", breed_info['weight'])
        add_info_row(body_content, "平均寿命", breed_info['life_span'])

        # 性格外貌 + 起源历史
        row2 = tk.Frame(content_frame, bg="#f5f5f5")
        row2.pack(fill="x", pady=(0, 10))

        card3 = tk.Frame(row2, bg="white", relief="flat", bd=0)
        card3.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        char_header = tk.Frame(card3, bg="#e67e22", padx=12, pady=8)
        char_header.pack(fill="x")
        tk.Label(char_header, text="🐕 狗狗性格和长相", font=("微软雅黑", 13, "bold"),
                bg="#e67e22", fg="white").pack(side="left")
        
        char_content = tk.Frame(card3, bg="white", padx=15, pady=12)
        char_content.pack(fill="x")
        
        add_info_row(char_content, "性格脾气", breed_info['character'])
        add_info_row(char_content, "外表模样", breed_info['appearance'])

        card4 = tk.Frame(row2, bg="white", relief="flat", bd=0)
        card4.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        origin_header = tk.Frame(card4, bg="#1abc9c", padx=12, pady=8)
        origin_header.pack(fill="x")
        tk.Label(origin_header, text="🌍 狗狗的来历故事", font=("微软雅黑", 13, "bold"),
                bg="#1abc9c", fg="white").pack(side="left")
        
        origin_content = tk.Frame(card4, bg="white", padx=15, pady=12)
        origin_content.pack(fill="x")
        
        add_info_row(origin_content, "出生地", breed_info['origin'])
        add_info_row(origin_content, "历史背景", breed_info['history'])

        # 喂养 + 健康护理
        row3 = tk.Frame(content_frame, bg="#f5f5f5")
        row3.pack(fill="x", pady=(0, 10))

        card5 = tk.Frame(row3, bg="white", relief="flat", bd=0)
        card5.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        feed_header = tk.Frame(card5, bg="#e74c3c", padx=12, pady=8)
        feed_header.pack(fill="x")
        tk.Label(feed_header, text="🍖 怎么喂养狗狗", font=("微软雅黑", 13, "bold"),
                bg="#e74c3c", fg="white").pack(side="left")
        
        feed_content = tk.Frame(card5, bg="white", padx=15, pady=12)
        feed_content.pack(fill="x")
        
        tk.Label(feed_content, text=breed_info['feeding'], font=("微软雅黑", 11),
                bg="white", fg="#2c3e50", wraplength=330, justify="left").pack(fill="x")

        card6 = tk.Frame(row3, bg="white", relief="flat", bd=0)
        card6.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        health_header = tk.Frame(card6, bg="#f39c12", padx=12, pady=8)
        health_header.pack(fill="x")
        tk.Label(health_header, text="🏥 健康和日常护理", font=("微软雅黑", 13, "bold"),
                bg="#f39c12", fg="white").pack(side="left")
        
        health_content = tk.Frame(card6, bg="white", padx=15, pady=12)
        health_content.pack(fill="x")
        
        add_info_row(health_content, "常见毛病", breed_info['health'])
        add_info_row(health_content, "护理要点", breed_info['care'])

        # 特色 + 适合人群
        row4 = tk.Frame(content_frame, bg="#f5f5f5")
        row4.pack(fill="x", pady=(0, 10))

        card7 = tk.Frame(row4, bg="white", relief="flat", bd=0)
        card7.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        feature_header = tk.Frame(card7, bg="#2ecc71", padx=12, pady=8)
        feature_header.pack(fill="x")
        tk.Label(feature_header, text="✨ 这狗狗有什么特别的", font=("微软雅黑", 13, "bold"),
                bg="#2ecc71", fg="white").pack(side="left")
        
        feature_content = tk.Frame(card7, bg="white", padx=15, pady=12)
        feature_content.pack(fill="x")
        
        tk.Label(feature_content, text=breed_info['feature'], font=("微软雅黑", 11),
                bg="white", fg="#2c3e50", wraplength=330, justify="left").pack(fill="x")

        card8 = tk.Frame(row4, bg="white", relief="flat", bd=0)
        card8.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        suit_header = tk.Frame(card8, bg="#34495e", padx=12, pady=8)
        suit_header.pack(fill="x")
        tk.Label(suit_header, text="👨‍👩‍👧‍👦 谁适合养这种狗", font=("微软雅黑", 13, "bold"),
                bg="#34495e", fg="white").pack(side="left")
        
        suit_content = tk.Frame(card8, bg="white", padx=15, pady=12)
        suit_content.pack(fill="x")
        
        tk.Label(suit_content, text=breed_info['suit_crowd'], font=("微软雅黑", 11),
                bg="white", fg="#2c3e50", wraplength=330, justify="left").pack(fill="x")

        # 关闭按钮
        btn_frame = tk.Frame(content_frame, bg="#f5f5f5", pady=10)
        btn_frame.pack(fill="x")
        
        close_btn = tk.Button(btn_frame, text="关闭", command=detail_win.destroy,
                             font=("微软雅黑", 12), bg="#95a5a6", fg="white",
                             padx=30, pady=8, relief="flat", cursor="hand2")
        close_btn.pack()

# ==============================================
# 启动程序
# ==============================================
if __name__ == "__main__":
    app = DogRecognitionApp()
    app.mainloop()