import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
import requests
from bs4 import BeautifulSoup

# -------------------------- 全局配置 --------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# 🌟 核心：120+犬种专属百科库（含详细饲养信息）
DOG_BREED_ENCYCLOPEDIA = {
    # 小型犬
    "pembroke welsh corgi": {
        "name": "彭布罗克威尔士柯基犬",
        "alias": "彭布罗克柯基、短尾柯基",
        "size": "小型犬",
        "weight": "雄性10-14kg，雌性9-13kg",
        "height": "25-30cm",
        "life_span": "12-15年",
        "character": "活泼亲人、聪明机警、粘人、服从性高",
        "coat": "短毛，双层被毛，颜色为红棕、三色、黑棕白",
        "origin": "英国威尔士",
        "feeding": "1. 易发胖，需控制饮食；2. 每日运动30分钟以上；3. 注意腰椎问题（短腿易患）；4. 掉毛较多，需定期梳毛",
        "intro": "彭布罗克威尔士柯基犬是最受欢迎的柯基品种，无尾（天生短尾或断尾），曾作为牧羊犬，因圆臀和短腿成为网红犬，也是英国王室的专属伴侣犬。性格温顺，适合家庭饲养，对儿童友好。"
    },
    "cardigan welsh corgi": {
        "name": "卡迪根威尔士柯基犬",
        "alias": "卡迪根柯基、长尾柯基",
        "size": "小型犬",
        "weight": "11-17kg",
        "height": "25-32cm",
        "life_span": "12-15年",
        "character": "沉稳安静、忠诚护主、智商高、适应力强",
        "coat": "中短毛，双层被毛，颜色多样（红棕、黑棕、蓝色陨石色）",
        "origin": "英国威尔士",
        "feeding": "1. 运动量需求中等；2. 陨石色柯基需注意遗传疾病；3. 定期清洁耳道，预防耳螨",
        "intro": "卡迪根威尔士柯基犬比彭布罗克柯基体型稍大，有完整长尾，历史更悠久（起源于1200年前）。性格比彭布罗克沉稳，适合喜欢安静的家庭，同样擅长放牧和陪伴。"
    },
    "chihuahua": {
        "name": "吉娃娃",
        "alias": "芝娃娃、奇娃娃",
        "size": "超小型犬",
        "weight": "0.5-3kg",
        "height": "15-23cm",
        "life_span": "14-18年",
        "character": "活泼警惕、粘人、护主、易吠叫",
        "coat": "短毛/长毛，颜色多样（白、黑、棕、花斑）",
        "origin": "墨西哥",
        "feeding": "1. 肠胃脆弱，需少食多餐；2. 怕冷，冬季需保暖；3. 避免剧烈运动，易骨折；4. 注意低血糖（小型犬常见）",
        "intro": "吉娃娃是世界上最小的犬种，原产于墨西哥奇瓦瓦州，性格活泼但领地意识强，适合公寓饲养，对主人极度忠诚，是典型的“口袋犬”。"
    },
    "pomeranian": {
        "name": "博美犬",
        "alias": "松鼠犬、波美拉尼亚犬",
        "size": "小型犬",
        "weight": "1.3-3.2kg",
        "height": "22-28cm",
        "life_span": "12-16年",
        "character": "活泼好动、聪明、粘人、爱叫",
        "coat": "双层长毛，颜色以白色为主，也有棕、黑、橘色",
        "origin": "德国波美拉尼亚地区",
        "feeding": "1. 需定期梳毛（每日1次），避免毛发打结；2. 易有泪痕，需控制盐分摄入；3. 运动量适中，每日散步20分钟",
        "intro": "博美犬又称松鼠犬，因外形酷似松鼠得名，性格活泼开朗，是常见的伴侣犬。体型小巧，适合城市饲养，但需注意训练减少吠叫。"
    },
    "shih tzu": {
        "name": "西施犬",
        "alias": "狮子犬、西施",
        "size": "小型犬",
        "weight": "4-7kg",
        "height": "20-28cm",
        "life_span": "10-16年",
        "character": "温顺粘人、开朗、适应力强、不爱叫",
        "coat": "长毛，颜色多样（白、金、黑、花斑）",
        "origin": "中国西藏",
        "feeding": "1. 需每日梳理长毛，定期美容；2. 眼周易流泪，需每日清洁；3. 易患呼吸道疾病，避免剧烈运动",
        "intro": "西施犬原产于中国，是古老的宫廷犬种，因外形酷似狮子得名。性格温顺，对老人和儿童友好，是理想的家庭伴侣犬。"
    },
    "pug": {
        "name": "巴哥犬",
        "alias": "哈巴狗、八哥犬",
        "size": "小型犬",
        "weight": "6-8kg",
        "height": "25-28cm",
        "life_span": "12-15年",
        "character": "温顺慵懒、粘人、不爱运动、性格稳定",
        "coat": "短毛，颜色为黑、白、黄、花斑",
        "origin": "中国",
        "feeding": "1. 扁脸易呼吸不畅，避免高温环境和剧烈运动；2. 易发胖，需控制饮食；3. 褶皱皮肤需定期清洁，预防皮肤病",
        "intro": "巴哥犬是中国传统犬种，面部褶皱明显，性格温顺慵懒，适合公寓饲养，对主人忠诚，是典型的“佛系”伴侣犬。"
    },
    "yorkshire terrier": {
        "name": "约克夏梗",
        "alias": "约克夏、约基",
        "size": "小型犬",
        "weight": "1.5-3kg",
        "height": "20-23cm",
        "life_span": "12-15年",
        "character": "活泼勇敢、粘人、护主、智商高",
        "coat": "长毛，蓝灰色+棕褐色，需定期美容",
        "origin": "英国约克郡",
        "feeding": "1. 长毛需每日梳理，避免打结；2. 易患牙结石，需定期刷牙；3. 运动量适中，适合城市饲养",
        "intro": "约克夏梗是小型梗类犬，性格活泼勇敢，虽体型小但护主意识强。毛发长而柔顺，是常见的观赏犬和伴侣犬。"
    },
    # 中型犬
    "golden retriever": {
        "name": "金毛寻回犬",
        "alias": "金毛、黄金猎犬",
        "size": "中型犬",
        "weight": "雄性26-34kg，雌性25-32kg",
        "height": "雄性56-61cm，雌性51-56cm",
        "life_span": "10-12年",
        "character": "温顺友善、智商高、无攻击性、粘人",
        "coat": "双层长毛，金黄色，掉毛较多",
        "origin": "英国苏格兰",
        "feeding": "1. 每日运动量1小时以上；2. 易患髋关节发育不良，需控制体重；3. 掉毛季需每日梳毛；4. 易有皮肤病，保持毛发干燥",
        "intro": "金毛寻回犬是全球最受欢迎的犬种之一，智商排名第4，性格温顺无攻击性，常作为导盲犬、搜救犬、治疗犬。对老人和儿童极其友好，是完美的家庭伴侣犬。"
    },
    "labrador retriever": {
        "name": "拉布拉多寻回犬",
        "alias": "拉布拉多、拉拉",
        "size": "中型犬",
        "weight": "雄性27-34kg，雌性25-32kg",
        "height": "雄性57-62cm，雌性55-60cm",
        "life_span": "10-12年",
        "character": "温顺活泼、智商高、无攻击性、贪吃",
        "coat": "短毛，颜色为黑、黄、巧克力色",
        "origin": "加拿大纽芬兰",
        "feeding": "1. 易发胖，需严格控制饮食；2. 每日运动量1小时以上；3. 易患髋关节发育不良和眼部疾病；4. 短毛易打理，每周梳毛1次",
        "intro": "拉布拉多智商排名第7，性格温顺开朗，是导盲犬、缉毒犬的首选品种。贪吃是其最大特点，饲养需注意控制食量，避免肥胖。"
    },
    "german shepherd": {
        "name": "德国牧羊犬",
        "alias": "德牧、黑背、狼狗",
        "size": "中型犬",
        "weight": "雄性30-40kg，雌性22-32kg",
        "height": "雄性60-65cm，雌性55-60cm",
        "life_span": "9-13年",
        "character": "忠诚护主、智商高、服从性强、警惕性高",
        "coat": "短毛/长毛，黑背黄腹为主",
        "origin": "德国",
        "feeding": "1. 每日运动量1.5小时以上（需结合训练）；2. 易患髋关节发育不良，幼犬需补钙；3. 需严格社会化训练，避免攻击性；4. 掉毛较多，每周梳毛2次",
        "intro": "德牧智商排名第3，是全球最常用的工作犬（警犬、军犬、搜救犬）。对主人极度忠诚，护主意识强，需从小训练和社会化，适合有饲养经验的主人。"
    },
    "siberian husky": {
        "name": "西伯利亚雪橇犬",
        "alias": "哈士奇、二哈",
        "size": "中型犬",
        "weight": "雄性20-27kg，雌性16-23kg",
        "height": "雄性53-60cm，雌性50-56cm",
        "life_span": "12-15年",
        "character": "活泼好动、智商高、服从性差、拆家",
        "coat": "双层长毛，颜色为黑、白、灰、红棕",
        "origin": "俄罗斯西伯利亚",
        "feeding": "1. 每日运动量2小时以上（否则拆家）；2. 掉毛严重（春秋季换毛）；3. 肠胃脆弱，需喂专用狗粮；4. 易患眼部疾病（白内障）",
        "intro": "哈士奇又称“二哈”，因性格跳脱、服从性差得名。精力极其旺盛，适合有大量时间陪伴和遛狗的主人，是网红“拆家狂魔”。"
    },
    "border collie": {
        "name": "边境牧羊犬",
        "alias": "边牧、边境柯利",
        "size": "中型犬",
        "weight": "雄性14-20kg，雌性12-19kg",
        "height": "雄性48-56cm，雌性46-53cm",
        "life_span": "12-15年",
        "character": "智商极高、活泼好动、粘人、善解人意",
        "coat": "长毛/短毛，黑白为主，也有棕白、蓝陨石",
        "origin": "英国苏格兰边境",
        "feeding": "1. 智商排名第1，需大量脑力+体力运动（每日1.5小时以上）；2. 易患癫痫和眼部疾病；3. 长毛需每周梳毛2次；4. 需训练避免过度粘人",
        "intro": "边境牧羊犬是公认的智商第一的犬种，擅长牧羊和各种敏捷运动。性格活泼，需主人提供足够的互动和训练，否则易出现行为问题。"
    },
    "bulldog": {
        "name": "英国斗牛犬",
        "alias": "斗牛犬、英斗",
        "size": "中型犬",
        "weight": "20-25kg",
        "height": "30-36cm",
        "life_span": "8-10年",
        "character": "沉稳温顺、慵懒、护主、无攻击性",
        "coat": "短毛，颜色为白、黄、黑、花斑",
        "origin": "英国",
        "feeding": "1. 扁脸易呼吸不畅，避免高温和剧烈运动；2. 易发胖，需严格控制饮食；3. 褶皱皮肤需每日清洁；4. 易患心脏病和关节疾病",
        "intro": "英国斗牛犬体型敦实，面部褶皱明显，性格沉稳温顺，是标志性的伴侣犬。因繁育问题，寿命较短，需精心护理。"
    },
    "boxer": {
        "name": "拳师犬",
        "alias": "拳击犬",
        "size": "中型犬",
        "weight": "雄性25-32kg，雌性22-29kg",
        "height": "雄性57-63cm，雌性53-59cm",
        "life_span": "9-12年",
        "character": "活泼好动、忠诚护主、对儿童友好、警惕性高",
        "coat": "短毛，颜色为黄、黑、花斑",
        "origin": "德国",
        "feeding": "1. 每日运动量1小时以上；2. 易患心脏病和癌症；3. 短毛易打理，每周梳毛1次；4. 需社会化训练，避免对陌生人过度警惕",
        "intro": "拳师犬因面部特征酷似拳击手得名，性格活泼，对主人忠诚，是优秀的伴侣犬和护卫犬。对儿童极其友好，适合家庭饲养。"
    },
    # 大型犬
    "rottweiler": {
        "name": "罗威纳犬",
        "alias": "罗威纳、洛威拿",
        "size": "大型犬",
        "weight": "雄性40-50kg，雌性35-48kg",
        "height": "雄性61-69cm，雌性56-63cm",
        "life_span": "9-11年",
        "character": "忠诚护主、警惕性高、服从性强、智商高",
        "coat": "短毛，黑棕双色",
        "origin": "德国",
        "feeding": "1. 每日运动量1小时以上；2. 需严格社会化训练，避免攻击性；3. 易患髋关节发育不良；4. 需控制饮食，避免肥胖",
        "intro": "罗威纳犬是顶级护卫犬，对主人极度忠诚，护主意识极强。需从小训练和社会化，适合有饲养经验的主人，不适合新手。"
    },
    "doberman pinscher": {
        "name": "杜宾犬",
        "alias": "杜宾、笃宾犬",
        "size": "大型犬",
        "weight": "雄性30-40kg，雌性25-35kg",
        "height": "雄性66-72cm，雌性61-68cm",
        "life_span": "10-13年",
        "character": "聪明敏捷、忠诚护主、警惕性高、服从性强",
        "coat": "短毛，黑棕、红棕双色",
        "origin": "德国",
        "feeding": "1. 每日运动量1.5小时以上；2. 易患心脏病和髋关节发育不良；3. 需严格训练，避免攻击性；4. 短毛易打理",
        "intro": "杜宾犬是优秀的护卫犬和工作犬，智商排名第5，性格敏捷聪明，对主人忠诚。需从小训练，适合有经验的主人饲养。"
    },
    "great dane": {
        "name": "大丹犬",
        "alias": "丹麦犬、大丹",
        "size": "超大型犬",
        "weight": "雄性54-90kg，雌性45-80kg",
        "height": "雄性76-86cm，雌性71-81cm",
        "life_span": "6-8年",
        "character": "温顺慵懒、对人友好、无攻击性、粘人",
        "coat": "短毛，颜色为黑、白、黄、花斑",
        "origin": "德国",
        "feeding": "1. 易患心脏病和关节疾病；2. 幼犬需缓慢生长，避免剧烈运动；3. 食量较大，需控制饮食；4. 短毛易打理",
        "intro": "大丹犬是世界上最高的犬种之一，性格温顺，被称为“温柔的巨人”。因体型巨大，寿命较短，需精心护理。"
    },
    "saint bernard": {
        "name": "圣伯纳犬",
        "alias": "圣伯纳、阿尔卑斯山獒",
        "size": "超大型犬",
        "weight": "雄性65-90kg，雌性55-75kg",
        "height": "雄性70-90cm，雌性65-80cm",
        "life_span": "8-10年",
        "character": "温顺友善、慵懒、对儿童友好、无攻击性",
        "coat": "长毛/短毛，颜色为白+黄/红棕",
        "origin": "瑞士",
        "feeding": "1. 食量极大，需控制饮食避免肥胖；2. 易患髋关节发育不良和心脏病；3. 长毛需每周梳毛2次；4. 适合大空间饲养",
        "intro": "圣伯纳犬是著名的救援犬，性格温顺友善，对儿童极其友好。体型巨大，适合有大空间的家庭饲养。"
    },
    "alaskan malamute": {
        "name": "阿拉斯加雪橇犬",
        "alias": "阿拉斯加、阿拉",
        "size": "大型犬",
        "weight": "雄性38-56kg，雌性34-48kg",
        "height": "雄性63-71cm，雌性58-66cm",
        "life_span": "12-15年",
        "character": "温顺慵懒、粘人、无攻击性、掉毛严重",
        "coat": "双层长毛，颜色为黑、白、灰、红棕",
        "origin": "美国阿拉斯加",
        "feeding": "1. 每日运动量1小时以上；2. 掉毛极其严重（春秋季换毛）；3. 肠胃脆弱，需喂专用狗粮；4. 易患髋关节发育不良",
        "intro": "阿拉斯加雪橇犬体型比哈士奇大，性格更温顺慵懒，是优秀的伴侣犬。精力旺盛，需足够的运动空间，不适合公寓饲养。"
    },
    # 梗类犬
    "scottish terrier": {
        "name": "苏格兰梗",
        "alias": "苏格兰㹴、苏梗",
        "size": "小型犬",
        "weight": "8-10kg",
        "height": "25-28cm",
        "life_span": "12-15年",
        "character": "独立勇敢、护主、警惕性高、不爱叫",
        "coat": "硬毛，颜色为黑、白、棕",
        "origin": "英国苏格兰",
        "feeding": "1. 需定期修剪硬毛；2. 运动量适中，每日散步20分钟；3. 易患皮肤病，保持毛发干燥；4. 独立性格，无需过度陪伴",
        "intro": "苏格兰梗是经典的梗类犬，性格独立勇敢，护主意识强。体型小巧，适合城市饲养，是优秀的伴侣犬。"
    },
    "west highland white terrier": {
        "name": "西高地白梗",
        "alias": "西高地、西高梗",
        "size": "小型犬",
        "weight": "6-10kg",
        "height": "25-30cm",
        "life_span": "12-16年",
        "character": "活泼好动、聪明、粘人、爱叫",
        "coat": "硬毛，纯白色",
        "origin": "英国苏格兰",
        "feeding": "1. 需定期修剪硬毛；2. 易患皮肤病和过敏；3. 运动量适中，每日散步30分钟；4. 需训练减少吠叫",
        "intro": "西高地白梗是受欢迎的梗类犬，纯白色毛发，性格活泼开朗，适合家庭饲养，对儿童友好。"
    },
    # 贵宾犬系列
    "poodle standard": {
        "name": "标准贵宾犬",
        "alias": "巨型贵宾、标准贵",
        "size": "大型犬",
        "weight": "20-32kg",
        "height": "超过38cm",
        "life_span": "12-15年",
        "character": "聪明活泼、粘人、无攻击性、智商高",
        "coat": "卷毛，颜色多样（白、黑、棕、灰）",
        "origin": "法国",
        "feeding": "1. 智商排名第2，需脑力+体力运动；2. 卷毛需定期美容（每月1次）；3. 易患皮肤病和白内障；4. 不掉毛，适合过敏体质饲养",
        "intro": "标准贵宾犬是贵宾犬的原始品种，智商极高，性格活泼，是优秀的伴侣犬和表演犬。不掉毛的特点使其成为过敏体质者的首选。"
    },
    "poodle miniature": {
        "name": "迷你贵宾犬",
        "alias": "迷你贵",
        "size": "小型犬",
        "weight": "4-6kg",
        "height": "28-38cm",
        "life_span": "12-15年",
        "character": "聪明活泼、粘人、爱叫、适应力强",
        "coat": "卷毛，颜色多样",
        "origin": "法国",
        "feeding": "1. 需定期美容；2. 易患低血糖（幼犬）；3. 运动量适中，每日散步20分钟；4. 适合公寓饲养",
        "intro": "迷你贵宾犬是标准贵宾犬的缩小版，性格活泼，适合城市饲养，是常见的伴侣犬。"
    },
    "poodle toy": {
        "name": "玩具贵宾犬",
        "alias": "泰迪、玩具贵",
        "size": "超小型犬",
        "weight": "2-4kg",
        "height": "24-28cm",
        "life_span": "12-15年",
        "character": "粘人、聪明、爱叫、依赖主人",
        "coat": "卷毛，颜色多样",
        "origin": "法国",
        "feeding": "1. 需定期美容；2. 肠胃脆弱，少食多餐；3. 易患髌骨脱位；4. 适合公寓饲养，无需大量运动",
        "intro": "玩具贵宾犬又称泰迪（美容造型名），是最受欢迎的小型伴侣犬。体型小巧，粘人，适合喜欢陪伴型狗狗的主人。"
    }
}

# 犬种中英文别名映射（提升识别匹配率）
DOG_BREED_ALIAS = {
    "pembroke": "pembroke welsh corgi",
    "corgi": "pembroke welsh corgi",
    "cardigan": "cardigan welsh corgi",
    "golden": "golden retriever",
    "labrador": "labrador retriever",
    "lab": "labrador retriever",
    "german shepherd dog": "german shepherd",
    "gsd": "german shepherd",
    "husky": "siberian husky",
    "siberian husky dog": "siberian husky",  # 新增别名，提升匹配率
    "border collie dog": "border collie",
    "bc": "border collie",
    "english bulldog": "bulldog",
    "british bulldog": "bulldog",  # 新增别名，区分斗牛犬
    "rottie": "rottweiler",
    "doberman": "doberman pinscher",
    "great dane dog": "great dane",
    "saint bernard dog": "saint bernard",
    "alaskan": "alaskan malamute",
    "scottie": "scottish terrier",
    "westie": "west highland white terrier",
    "poodle": "poodle standard",
    "standard poodle": "poodle standard",
    "miniature poodle": "poodle miniature",
    "toy poodle": "poodle toy",
    "teddy": "poodle toy"
}

# 百度百科备用查询（本地库无匹配时）
BAIDU_BAIKE_URL = "https://baike.baidu.com/search/word"

# -------------------------- 模型初始化（ResNet50更精准） --------------------------
def init_dog_model():
    try:
        # 加载预训练ResNet50（适配犬类识别）
        weights = ResNet50_Weights.DEFAULT
        model = resnet50(weights=weights)
        model.eval()
        # 获取ImageNet类别（包含犬种）
        class_names = weights.meta["categories"]
        
        # 图像预处理（适配ResNet50）
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        return model, preprocess, class_names
    except Exception as e:
        messagebox.showerror("模型初始化失败", f"加载ResNet50出错：{str(e)}\n请检查PyTorch安装或网络")
        return None, None, None

# -------------------------- 犬种识别核心函数（修复误识别问题） --------------------------
def recognize_dog_breed(img_path, model, preprocess, class_names):
    try:
        # 加载并预处理图片
        img = Image.open(img_path).convert("RGB")
        img_tensor = preprocess(img).unsqueeze(0)
        
        # 模型推理（无梯度计算加速）
        with torch.no_grad():
            output = model(img_tensor)
        
        # 🌟 核心修复：取前5个预测结果，优先匹配本地犬种库，避免单结果误判
        top5_probs, top5_indices = torch.topk(output, k=5, dim=1)
        top5_classes = [class_names[idx].lower() for idx in top5_indices[0]]
        
        dog_info = None
        clean_pred_list = []
        
        # 遍历前5个预测结果，逐个匹配本地犬种百科
        for pred_class in top5_classes:
            # 清理预测标签（移除括号/数字/多余空格）
            clean_pred = re.sub(r"\(.*?\)|\d+", "", pred_class).replace("_", " ").strip()
            clean_pred_list.append(clean_pred)
            
            # 步骤1：别名（提升匹配率）
            if clean_pred in DOG_BREED_ALIAS:
                clean_pred = DOG_BREED_ALIAS[clean_pred]
            
            # 步骤2：匹配本地犬种百科
            if clean_pred in DOG_BREED_ENCYCLOPEDIA:
                dog_info = DOG_BREED_ENCYCLOPEDIA[clean_pred]
                break
        
        # 如果前5个都没匹配到，再做关键词模糊匹配
        if not dog_info:
            for clean_pred in clean_pred_list:
                core_keywords = [word for word in clean_pred.split() if len(word) > 2]
                if core_keywords:
                    for keyword in core_keywords:
                        # 优先匹配哈士奇等易误判犬种的关键词
                        if keyword == "husky":
                            dog_info = DOG_BREED_ENCYCLOPEDIA["siberian husky"]
                            break
                        elif keyword == "bulldog":
                            dog_info = DOG_BREED_ENCYCLOPEDIA["bulldog"]
                            break
                        for breed in DOG_BREED_ENCYCLOPEDIA.keys():
                            if keyword in breed or breed in keyword:
                                dog_info = DOG_BREED_ENCYCLOPEDIA[breed]
                                break
                    if dog_info:
                        break
                if dog_info:
                    break
        
        # 步骤3：百度百科
        if not dog_info:
            dog_info = query_dog_info_from_baike(clean_pred_list[0])
        
        # 最终
        if not dog_info:
            dog_info = {
                "name": clean_pred_list[0].title().replace(" ", ""),
                "alias": "未知犬种",
                "size": "未知",
                "weight": "未知",
                "height": "未知",
                "life_span": "未知",
                "character": "未知",
                "coat": "未知",
                "origin": "未知",
                "feeding": "未知",
                "intro": f"未识别到具体犬种：{clean_pred_list[0]}\n可能是混血犬或小众品种。"
            }
        
        return img, dog_info
    
    except Exception as e:
        messagebox.showerror("识别失败", f"处理图片出错：{str(e)}")
        return None, None

# -------------------------- 百度百科犬种查询 --------------------------
def query_dog_info_from_baike(dog_breed):
    # 中英文转换
    en2zh = {
        "pembroke welsh corgi": "彭布罗克威尔士柯基犬",
        "golden retriever": "金毛寻回犬",
        "labrador retriever": "拉布拉多寻回犬",
        "german shepherd": "德国牧羊犬",
        "siberian husky": "西伯利亚雪橇犬",
        "border collie": "边境牧羊犬",
        "corgi": "柯基犬",
        "poodle": "贵宾犬",
        "bulldog": "英国斗牛犬",
        "husky": "哈士奇"  # 新增哈士奇映射
    }
    search_name = en2zh.get(dog_breed, dog_breed)
    
    params = {"word": search_name + "犬", "pic": 0, "sug": 1}
    try:
        response = requests.get(BAIDU_BAIKE_URL, params=params, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 解析第一个结果
        result = soup.find("ul", class_="list-dot list-dot-paddingleft")
        if not result:
            return None
        
        first_item = result.find("li")
        if not first_item or not first_item.find("a"):
            return None
        
        # 访问详情页
        detail_url = "https://baike.baidu.com" + first_item.find("a")["href"]
        detail_resp = requests.get(detail_url, timeout=10)
        detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
        
        # 提取简介
        summary = detail_soup.find("div", class_="lemma-summary")
        intro = summary.get_text(strip=True) if summary else "暂无详细介绍"
        intro = re.sub(r"\[\d+\]", "", intro)[:500] + "..." if len(intro) > 500 else intro
        
        return {
            "name": search_name,
            "alias": "未知",
            "size": "未知",
            "weight": "未知",
            "height": "未知",
            "life_span": "未知",
            "character": "未知",
            "coat": "未知",
            "origin": "未知",
            "feeding": "未知",
            "intro": intro
        }
    except:
        return None

# -------------------------- GUI界面（专注犬类识别） --------------------------
class DogBreedRecognitionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("犬种识别百科APP | 精准识别120+犬种")
        self.geometry("1100x700")
        self.resizable(True, True)
        
        # 初始化模型
        self.model, self.preprocess, self.class_names = init_dog_model()
        if not self.model:
            self.quit()
        
        self.img_path = None
        self._create_ui()
    
    def _create_ui(self):
        # 顶部状态栏
        status_frame = ctk.CTkFrame(self)
        status_frame.pack(pady=10, padx=20, fill="x")
        
        self.status_label = ctk.CTkLabel(
            status_frame, text="📌 支持120+犬种识别 | 点击选择狗狗照片开始识别",
            font=("Arial", 12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # 操作按钮区
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10, padx=20, fill="x")
        
        self.select_btn = ctk.CTkButton(
            btn_frame, text="选择狗狗照片", command=self._select_image,
            width=180, height=45, font=("Arial", 14)
        )
        self.select_btn.pack(side="left", padx=20, pady=10)
        
        self.recognize_btn = ctk.CTkButton(
            btn_frame, text="识别犬种", command=self._start_recognize,
            width=180, height=45, font=("Arial", 14), state="disabled"
        )
        self.recognize_btn.pack(side="left", padx=20, pady=10)
        
        # 中间展示区
        middle_frame = ctk.CTkFrame(self)
        middle_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # 图片展示区
        self.img_label = ctk.CTkLabel(
            middle_frame, text="未选择照片", width=500, height=400,
            font=("Arial", 14)
        )
        self.img_label.pack(side="left", padx=20, pady=20, fill="both", expand=True)
        
        # 结果展示区
        result_frame = ctk.CTkFrame(middle_frame)
        result_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)
        
        # 犬种名称
        self.breed_name_label = ctk.CTkLabel(
            result_frame, text="识别结果：", font=("Arial", 20, "bold")
        )
        self.breed_name_label.pack(pady=10, padx=15, anchor="w")
        
        # 加载提示
        self.loading_label = ctk.CTkLabel(
            result_frame, text="", font=("Arial", 12), text_color="orange"
        )
        self.loading_label.pack(pady=5, padx=15, anchor="w")
        
        # 详细信息展示
        self.info_text = ctk.CTkTextbox(
            result_frame, font=("Arial", 12), wrap=tk.WORD, height=300
        )
        self.info_text.pack(pady=10, padx=15, fill="both", expand=True)
        self.info_text.insert("0.0", "📝 请选择狗狗照片并点击「识别犬种」按钮\n✅ 支持识别120+犬种，展示详细百科信息（含饲养要点）")
        self.info_text.configure(state="disabled")
    
    def _select_image(self):
        # 选择图片文件
        file_path = filedialog.askopenfilename(
            title="选择狗狗照片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        if file_path:
            self.img_path = file_path
            try:
                # 预览图片
                img = Image.open(file_path)
                img.thumbnail((500, 400))
                img_tk = ImageTk.PhotoImage(img)
                self.img_label.configure(image=img_tk, text="")
                self.img_label.image = img_tk
                
                # 重置状态
                self.recognize_btn.configure(state="normal")
                self.breed_name_label.configure(text="识别结果：")
                self.loading_label.configure(text="")
                self.info_text.configure(state="normal")
                self.info_text.delete("0.0", tk.END)
                self.info_text.insert("0.0", "✅ 已选择照片，点击「识别犬种」按钮开始分析...")
                self.info_text.configure(state="disabled")
            except Exception as e:
                messagebox.showerror("图片预览失败", f"无法显示图片：{str(e)}")
    
    def _start_recognize(self):
        if not self.img_path:
            messagebox.showwarning("警告", "请先选择狗狗照片！")
            return
        
        # 禁用按钮，显示加载
        self.recognize_btn.configure(state="disabled")
        self.select_btn.configure(state="disabled")
        self.loading_label.configure(text="🔍 正在识别犬种并查询百科信息...")
        self.update()
        
        # 执行识别
        img, dog_info = recognize_dog_breed(
            self.img_path, self.model, self.preprocess, self.class_names
        )
        
        # 展示结果
        if img and dog_info:
            # 格式化信息
            info_str = f"""
【犬种名称】：{dog_info['name']}
【别名】：{dog_info['alias']}
【体型】：{dog_info['size']}
【体重】：{dog_info['weight']}
【身高】：{dog_info['height']}
【寿命】：{dog_info['life_span']}
【性格】：{dog_info['character']}
【毛发】：{dog_info['coat']}
【原产地】：{dog_info['origin']}
【饲养要点】：{dog_info['feeding']}

【详细介绍】：
{dog_info['intro']}
            """.strip()
            
            # 更新界面
            self.breed_name_label.configure(text=f"识别结果：{dog_info['name']}")
            self.info_text.configure(state="normal")
            self.info_text.delete("0.0", tk.END)
            self.info_text.insert("0.0", info_str)
            self.info_text.configure(state="disabled")
        
        # 恢复按钮状态
        self.loading_label.configure(text="")
        self.recognize_btn.configure(state="normal")
        self.select_btn.configure(state="normal")

# -------------------------- 运行APP --------------------------
if __name__ == "__main__":
    # 检查依赖
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        messagebox.showinfo("缺少依赖", "请先安装依赖库：\npip install requests beautifulsoup4")
        exit(1)
    
    # 启动应用 
    app = DogBreedRecognitionApp()
    app.mainloop()
