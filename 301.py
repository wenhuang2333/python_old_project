import pygame
import random
import math
import sys
import os

#————————————————
#打包指令pyinstaller --onefile --noconsole --add-data "C:\Users\zhans\PycharmProjects\pythonProject\fire_and_water;fire_and_water" --icon "C:\Users\zhans\PycharmProjects\pythonProject\fire_and_water\1.ico" 301.py
#第二打包指令pyinstaller --onefile --noconsole --add-data "C:\\Users\\zhans\\PycharmProjects\\pythonProject\\fire_and_water;fire_and_water" --icon "C:\\Users\\zhans\\PycharmProjects\\pythonProject\\fire_and_water\\1.ico" 301.py
#————————————————
# ----------------------------
# 获取资源的绝对路径
# ----------------------------

def resource_path(relative_path):

    try:
        # 打包后的资源路径
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境中的资源路径
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# ----------------------------
# 窗口设置
# ----------------------------

#?昔人已乘黄鹤去

#425500
# ----------------------------
# 全局常量设置
# ----------------------------
SCREEN_WIDTH = 1665
SCREEN_HEIGHT = 850

# 玩家手牌尺寸（用于手牌显示）
HAND_CARD_WIDTH = 174
HAND_CARD_HEIGHT = 268
# 出牌展示尺寸
PLAYED_CARD_WIDTH = 147
PLAYED_CARD_HEIGHT = 248

CARD_HOVER_SCALE = 1.2

MAX_HAND_SIZE = 16
CARD_SPACING = HAND_CARD_WIDTH-25

BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_Y = SCREEN_HEIGHT - HAND_CARD_HEIGHT - 100

INITIAL_DEAL_DELAY = 100  #初始发牌时每张牌之间的延迟
COMPUTER_DELAY = 1800  #电脑出牌后的等待时间，保持2100毫秒让玩家有足够时间观察。
EFFECT_DURATION = 1200  #一般效果（如伤害数字）的显示时间，设为2000毫秒即2秒。
#adjust
# 交换按钮（放在 skip 按钮下方）
SWAP_BUTTON_RECT = pygame.Rect(50, BUTTON_Y + BUTTON_HEIGHT + 10, BUTTON_WIDTH, BUTTON_HEIGHT)
#- self
# ----------------------------
# 图片路径映射
# ----------------------------
image_path_mapping = {
    "火杀": resource_path("./fire_and_water/fireK.png"),
    "水杀": resource_path("./fire_and_water/waterK.png"),
    "火盾": resource_path("./fire_and_water/fireD.png"),
    "水盾": resource_path("./fire_and_water/waterD.png"),
    "火源": resource_path("./fire_and_water/fire.png"),
    "水源": resource_path("./fire_and_water/water.png"),
    "时源": resource_path("./fire_and_water/timer.png"),
    "序源": resource_path("./fire_and_water/order_.png"),
    "火刃": resource_path("./fire_and_water/FK.png"),
    "水刃": resource_path("./fire_and_water/WK.png"),
    "动如脱兔": resource_path("./fire_and_water/fast.png"),
    "迅疾如风": resource_path("./fire_and_water/wind.png"),
    "乘如白驹": resource_path("./fire_and_water/get_time.png"),
    "此刻永恒": resource_path("./fire_and_water/GETTIME.png"),
    "熵增": resource_path("./fire_and_water/ORDER.png"),
    "索取": resource_path("./fire_and_water/regive.png"),
    "更多的索取": resource_path("./fire_and_water/more_regive.png"),
    "自我燃烧": resource_path("./fire_and_water/burn.png"),
    "自我淹没": resource_path("./fire_and_water/flood.png"),
    "以退为进": resource_path("./fire_and_water/back_go.png"),
    "background": resource_path("./fire_and_water/background.png")
}
reverse_card_name_mapping = {
    "fireK": "火杀",
    "waterK": "水杀",
    "fireD": "火盾",
    "waterD": "水盾",
    "fire": "火源",
    "water": "水源",
    "order": "序源",
    "timer": "时源",
    "FK": "火刃",
    "WK": "水刃",
    "fast": "动如脱兔",
    "wind": "迅疾如风",
    "get_time": "乘如白驹",
    "GETTIME": "此刻永恒",
    "ORDER": "熵增",
    "regive": "索取",
    "REGIVE": "更多的索取",
    "burn": "自我燃烧",
    "flood": "自我淹没",
    "back_go": "以退为进"
}
#self.player_moves
# 电脑牌图片路径
COMPUTER_IMAGE_PATH = resource_path("./fire_and_water/computer.png")

# ----------------------------
# 牌名映射（中文转英文缩写）zip
# ----------------------------
card_name_mapping = {
    "火杀": "fireK",
    "水杀": "waterK",
    "火盾": "fireD",
    "水盾": "waterD",
    "火源": "fire",
    "水源": "water",
    "序源": "order",  # 序源：回复2HP并随机删除一张牌
    "时源": "timer",
    "火刃": "FK",
    "水刃": "WK",
    "动如脱兔": "fast",
    "迅疾如风": "wind",
    "乘如白驹": "get_time",  # 增加2次出手
    "此刻永恒": "GETTIME",  # 增加4次出手
    "熵增": "ORDER",  # 双方各获得2张牌
    "索取": "regive",
    "更多的索取": "REGIVE",
    "自我燃烧": "burn",
    "自我淹没": "flood",
    "以退为进": "back_go"
}
#if self.popup_message and pygame.time.get_ticks() - self.popup_start_time
#victory
# ----------------------------
# 卡牌类型及权重（更新后的权重）
# ----------------------------
card_types = [
    ("火杀", 65),
    ("水杀", 65),
    ("火盾", 25),
    ("水盾", 25),
    ("火源", 16),
    ("水源", 16),
    ("序源", 8),
    ("时源", 5),
    ("火刃", 28),
    ("水刃", 28),
    ("动如脱兔", 1),
    ("迅疾如风", 0.5),
    ("乘如白驹", 2),
    ("此刻永恒", 0.5),
    ("熵增", 5),
    ("索取", 12),
    ("更多的索取", 6),
    ("自我燃烧", 15),
    ("自我淹没", 15),#12),
    ("以退为进", 5)
]
card_types_middle_and_easy = [
    ("火杀", 70),
    ("水杀", 70),
    ("火盾", 50),
    ("水盾", 50),
    ("火源", 40),
    ("水源", 40),
    ("序源", 8),
    ("时源", 10),
    ("火刃", 0),
    ("水刃", 0),
    ("动如脱兔", 10),
    ("迅疾如风", 1),
    ("乘如白驹", 5),
    ("此刻永恒", 2),
    ("熵增", 25),
    ("索取", 35),
    ("更多的索取", 20),
    ("自我燃烧", 0),
    ("自我淹没", 38),#12),
    ("以退为进", 0)
]
card_types_hard_computer = [
    ("火杀", 70),
    ("水杀", 65),
    ("火盾", 37),
    ("水盾", 30),
    ("火源", 14),
    ("水源", 14),
    ("序源", 8),
    ("时源", 5),
    ("火刃", 35),
    ("水刃", 32),
    ("动如脱兔", 5),
    ("迅疾如风", 2),
    ("乘如白驹", 0.5),
    ("此刻永恒", 0.1),
    ("熵增", 8),
    ("索取", 15),
    ("更多的索取", 8),
    ("自我燃烧", 18),
    ("自我淹没", 12),#12),
    ("以退为进", 8)
]
card_types_hardest = [
    ("火杀", 100),
    ("水杀", 120),
    ("火盾", 35),
    ("水盾", 40),
    ("火源", 28),
    ("水源", 34),
    ("序源", 8),
    ("时源", 12),
    ("火刃", 32),
    ("水刃", 42),
    ("动如脱兔", 10),
    ("迅疾如风", 5),
    ("乘如白驹", 6),
    ("此刻永恒", 1),
    ("熵增", 5),
    ("索取", 14),
    ("更多的索取", 7),
    ("自我燃烧", 28),
    ("自我淹没", 18),#12),
    ("以退为进", 2)
]
card_types_hardest_computer = [
    ("火杀", 85),
    ("水杀", 45),
    ("火盾", 45),
    ("水盾", 40),
    ("火源", 14),
    ("水源", 13),
    ("序源", 8),
    ("时源", 1),
    ("火刃", 0),
    ("水刃", 0),
    ("动如脱兔", 1),
    ("迅疾如风", 0.5),
    ("乘如白驹", 1),
    ("此刻永恒", 50),
    ("熵增", 10),
    ("索取", 35),
    ("更多的索取", 15),
    ("自我燃烧", 25),
    ("自我淹没", 10),#12),
    ("以退为进", 4)
]

# ----------------------------
# 全局预加载字典和变量
# ----------------------------
preloaded_images = {}
computer_image = None


# ----------------------------
# 辅助函数：加载图片，若失败则返回填充颜色的 Surface
# ----------------------------
def get_card_color(name):
    if name in {"火杀", "火盾", "火刃", "火源", "自我燃烧"}:
        return 255, 0, 0
    elif name in {"水杀", "水盾", "水刃", "水源", "自我淹没"}:
        return 0, 0, 139
    elif name in {"熵增", "序源", "时源", "乘如白驹", "此刻永恒"}:
        return 0, 0, 0
    elif name in {"动如脱兔", "迅疾如风"}:
        return 224, 255, 255
    else:
        return 255, 255, 255

#Computer
# ----------------------------
# 角色类
# ----------------------------
class Role:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.speed = 0
        self.FK = False
        self.WK = False
        self.FD = False
        self.WD = False
        self.fire_attach = False
        self.water_attach = False
        # 修改：当血量低于20时，濒死状态应为 True
        self.DEAD = self.hp <= 21
        self.burn_bonus = False#自我燃烧判定
        # 新增：用于水杀延迟治疗
        self.delayed_heal = 0
        self.delayed_heal_round = 0

    def update_status(self):
        # 当 hp < 20 时认为处于濒死状态
        self.DEAD = self.hp <= 21

    def reset_on_my_turn(self):
        self.FK = False
        self.WK = False
        self.FD = False
        self.WD = False


# ----------------------------
# 卡牌类
# ----------------------------
class Card:
    def __init__(self, name):
        self.original_name = name
        self.name = card_name_mapping.get(name, name)
        img = preloaded_images.get(name)
        if img is not None:
            self.image = img.copy()
        else:
            self.image = pygame.Surface((HAND_CARD_WIDTH, HAND_CARD_HEIGHT))
            self.image.fill(get_card_color(name))
            font = pygame.font.SysFont("arial", 50)
            text_color = (255, 255, 255) if get_card_color(name) == (0, 0, 0) else (0, 0, 0)
            text = font.render(self.name, True, text_color)
            self.image.blit(text, (5, 5))
        self.image = pygame.transform.smoothscale(self.image, (HAND_CARD_WIDTH, HAND_CARD_HEIGHT))
        self.rect = self.image.get_rect()

    def draw(self, screen, pos, hovered=False):
        if hovered:
            scale = CARD_HOVER_SCALE
            new_width = int(HAND_CARD_WIDTH * scale)
            new_height = int(HAND_CARD_HEIGHT * scale)
            scaled_image = pygame.transform.smoothscale(self.image, (new_width, new_height))
            rect = scaled_image.get_rect(center=(pos[0] + HAND_CARD_WIDTH // 2, pos[1] + HAND_CARD_HEIGHT // 2))
            screen.blit(scaled_image, rect.topleft)
            return rect
        else:
            screen.blit(self.image, pos)
            rect = self.image.get_rect(topleft=pos)
            return rect


# ----------------------------
# 发牌函数
# ----------------------------
def deal_card(side="player"):
    if game.hardest:
        if side == "computer":
            cards, weights = zip(*card_types_hardest_computer)
        else:
            cards, weights = zip(*card_types_hardest)
    elif game.hard:
        if side=="computer":
            cards,weights=zip(*card_types_hard_computer)
        else:
            cards,weights=zip(*card_types)
    elif game.easy or game.middle:
        if side=="computer":
            cards,weights=zip(*card_types_middle_and_easy)
        else:
            cards,weights=zip(*card_types)
    else:
        cards, weights = zip(*card_types)

    chosen_name = random.choices(cards, weights=weights)[0]
    return Card(chosen_name)


# ----------------------------
# 电脑牌图片加载
# ----------------------------
def get_computer_card_image():
    if computer_image is not None:
        img = computer_image.copy()
    else:
        img = pygame.Surface((HAND_CARD_WIDTH, HAND_CARD_HEIGHT))
        img.fill((50, 50, 50))
        font = pygame.font.SysFont("arial", 50)
        text = font.render("COMPUTER", True, (255, 255, 255))
        img.blit(text, (5, 5))
    img = pygame.transform.smoothscale(img, (HAND_CARD_WIDTH, HAND_CARD_HEIGHT))
    return img


# ----------------------------
# 对策卡效果处理
# ----------------------------
player_turn_flag=0
computer_turn_flag=0

def process_card_effect(card, attacker, defender, game=None):

    if game.hardest:
        if attacker.name=="Computer":
            attacker.hp+=0.5
    print(f"当前颜色{game.damage_color},{game.heal_indicator_color}")
    game.turn_count += 1
    game.damage_indicator = None
    game.heal_indicator = None
    game.damage = 0
    game.heal = 0
    if attacker.name == "Player":
        game.have_played = True  # 玩家出牌后标记为 True
        game.front_computer_queue.clear()
        game.front_computer_queue_name.clear()
    elif attacker.name == "computer":
        game.have_played = False

    # 速度判定：若攻击者速度低，则有 (defender.speed - attacker.speed)% 概率使本次攻击伤害为 0
    speed_diff = max(defender.speed - attacker.speed, 0)
    speed_fail = (speed_diff > 0 and random.uniform(0, 100) < speed_diff)
    extra_text = ""

    if card.name == "fireK":
        flag = 0
        if speed_fail:
            flag = 2
            damage = 0
            game.show_card_effect_image(resource_path("fire_and_water/wind_text.png"), (1050, 250))
            print(f"{attacker.name}'s {card.name} nullified by speed difference (c = {speed_diff}%)")
            if game is not None:
                game.show_damage_text(damage, "被逃了！")
                if attacker.name == "Player":
                    game.show_popup("1", (0, 255, 0))
                else:
                    game.show_popup("2", (0, 255, 0))
                if flag == 2:
                    game.show_card_effect_image(resource_path("fire_and_water/what_speed_text.png"), (50, 250))
        else:
            #dealing
            damage = 1
            if game.hardest and attacker.name=="Computer":
                print("当前回合本该是电脑")
                damage+=4
                if attacker.fire_attach:
                    damage += 3
            if attacker.FK:
                print(f"火刃加成前的伤害为{damage}")
                if (attacker.name=="Computer" and game.hardest==False) or game.hardest==False :
                    damage += 4

                    if attacker.fire_attach:
                        damage += 3

                elif attacker.name=="Player" and game.hardest==True:
                    damage+=6
                    if attacker.fire_attach:
                        damage+=5
                attacker.FK = False
                print(f"火刃加成后的伤害为{damage}")
            if attacker.FD:
                print(f"火盾加成前的伤害为{damage}")
                if attacker.name=="Player" and game.hardest==True:
                    damage+=6
                else:
                    print("火盾加成")
                    damage += 4
                print(f"火盾加成后的伤害为{damage}")
            if attacker.hp<=21:
                damage += 5
            if attacker.burn_bonus:
                damage += 2
                attacker.burn_bonus = False
            if defender.water_attach:
                defender.water_attach = False
                defender.fire_attach = False
                damage += 2
                flag = 1
                if flag == 1:
                    #Player in DEAD state
                    game.show_card_effect_image(resource_path("fire_and_water/fireK_text1.png"), (1050, 250))
            else:
                if not defender.fire_attach:
                    defender.fire_attach = True
            if defender.FD:
                defender.FD = False
                damage = 0
                game.show_damage_text(damage, "被盾了！")
                flag = 3
                if flag == 3:
                    game.show_card_effect_image(resource_path("fire_and_water/noproblem_text.png"), (50, 250))
        defender.hp -= damage
        print(f"{attacker.name} uses {card.name} dealing {damage} damage")
        if game is not None and damage > 0:
            game.damage += damage
            game.show_damage_text(damage, "火！")
            if extra_text == "":
                if flag == 0:
                    game.show_card_effect_image(resource_path("fire_and_water/fireK_text2.png"), (1050, 250))
        defender.update_status()
    elif card.name == "waterK":
        flag = 0
        flag1=0
        damage = 0
        if speed_fail:
            flag = 2
            game.show_card_effect_image(resource_path("fire_and_water/wind_text.png"), (1050, 250))
            print(f"{attacker.name}'s {card.name} nullified by speed difference (c = {speed_diff}%)")
            if game is not None:
                game.show_damage_text(damage, "被逃了！")
                if attacker.name == "Player":
                    game.show_popup("1", (0, 255, 0))
                else:
                    game.show_popup("2", (0, 255, 0))
                if flag == 2:
                    game.show_card_effect_image(resource_path("fire_and_water/what_speed_text.png"), (50, 250))
        else:
            damage = 1
            heal_val = 0
            if game.hardest==True and attacker.name=="Computer":
                damage+=2
                if attacker.water_attach:
                    flag1+=1
            #
            # 只有当己方同时处于水刃和水附着状态时，才会记录恢复效果
            if attacker.WK:
                if (attacker.name=="Computer" and game.hardest==False) or game.hardest==False :
                    print("水刃已经到达")
                    damage+=2
                    if attacker.water_attach:
                        flag1 += 1

                elif attacker.name=="Player" and game.hardest:
                    print("当前为玩家水刃情况============")
                    damage+=3
                    if attacker.water_attach:
                        flag+=2
                attacker.WK = False

            if attacker.WD:
                if attacker.name=="Player" and game.hardest==True:
                    heal_val+=4
                    damage+=3
                else:
                    damage+=2
                    heal_val += 3
                print("水盾已经到达")
            if defender.fire_attach:
                defender.fire_attach = False
                defender.water_attach = False
                damage += 3
                flag = 1
                if game is not None:

                    game.show_damage_text(damage, "水！")
                    if extra_text == "":
                        # if flag==1:
                        game.show_card_effect_image(resource_path("fire_and_water/waterK_text1.png"), (1050, 250))

            else:
                if not defender.water_attach:
                    defender.water_attach = True
            # 濒死增益：如果己方 hp < 3，则额外加 2，并直接额外恢复本次伤害（记录为 n）
            if attacker.hp<=21:
                print("濒死已经到达")
                damage += 2
                # 直接额外回复等于本次伤害的 HP
                flag1+=1
                print(f"{attacker.name} in DEAD state: additional {damage} HP restored immediately")

            if defender.WD:
                defender.WD = False
                damage = 0
                game.show_damage_text(damage,"被盾了！")
                flag=3
                if flag==3:
                    game.show_card_effect_image(resource_path("fire_and_water/noproblem_text.png"),(50,250))
            heal_val+=damage*flag1
            print(f"当前水杀伤害为{damage},治愈量应为{heal_val}")
            if heal_val > 0:
                attacker.hp += heal_val

                print(f"{attacker.name} gains immediate healing of {heal_val} from waterK")
            defender.hp -= damage
            print(f"{attacker.name} uses {card.name} dealing {damage} damage")
            if game is not None and damage>0 and heal_val>0:
                game.show_damage_and_heal(damage, heal_val, "水！")
            if game is not None and damage > 0:
                if extra_text == "":
                    if flag==0:
                        game.show_card_effect_image(resource_path("fire_and_water/utilize_text.png"),(1050,250))
                    print(114514)
            if game is not None:
                game.show_damage_text(damage,  extra_text)
                if heal_val > 0:
                    game.show_heal(heal_val)
                    game.show_card_effect_image(resource_path("fire_and_water/delicious_text.png"),(50,250))
            game.damage += damage
            game.heal += heal_val
            defender.update_status()
    elif card.name == "fireD":  # 打出后显示"见我灭汝之焰!"
        attacker.FD = True
        print(f"{attacker.name} uses {card.name}, FD set true")
        if game is not None:
            game.show_card_effect_image(resource_path("fire_and_water/fireD_text.png"),(1050,250))
    elif card.name == "waterD":  # 打出后显示"见我涸汝之泽!"
        attacker.WD = True
        print(f"{attacker.name} uses {card.name}, WD set true")
        if game is not None:
            game.show_card_effect_image(resource_path("fire_and_water/waterD_text.png"),(1050,250))
    elif card.name == "fire":  # 打出后显示”以此火源昭众生“
        # 火源：回复1点HP；若自身 fire_attach 为 True，则额外回复1点并取消 fire_attach
        heal = 1
        if attacker.fire_attach:
            heal += 1
            attacker.fire_attach = False
        if game.hardest and attacker.name=="Player":
            heal+=2
        game.heal += heal
        attacker.hp += heal
        print(f"{attacker.name} uses {card.name} healing {heal}")
        if game is not None:
            game.show_heal(heal)
            game.show_card_effect_image(resource_path("fire_and_water/fire_text.png"), (1050, 250))
    elif card.name == "water":  # 打出后显示“以此水源濯众尘”
        # 水源：回复1点HP；若自身 water_attach 为 True，则额外回复2点，但不取消 water_attach
        heal = 1
        if attacker.water_attach:
            heal += 2
        if game.hardest and attacker.name=="Player":
            heal+=2
        attacker.hp += heal
        game.heal += heal
        print(f"{attacker.name} uses {card.name} healing {heal}")
        if game is not None:
            game.show_heal(heal)
            game.show_card_effect_image(resource_path("fire_and_water/water_text.png"), (1050, 250))
    elif card.name == "FK":#打出后显示“以阳焱洗刃！”
        attacker.FK = True
        print(f"{attacker.name} uses {card.name}, FK set true")
        if game is not None:
            game.show_card_effect_image(resource_path("fire_and_water/FK_text.png"),(1050,250))
    elif card.name == "WK":#打出后显示“以凝渊沉铭！”
        attacker.WK = True
        print(f"{attacker.name} uses {card.name}, WK set true")
        if game is not None:
            game.show_card_effect_image(resource_path("fire_and_water/WK_text.png"),(1050,250))
    elif card.name == "fast":#打出后显示“天下武功！”
        attacker.speed += 10
        print(f"{attacker.name} uses {card.name}, SPD increased by 2 to {attacker.speed}")
        if game is not None:
            game.show_card_effect_image(resource_path("fire_and_water/fast_text.png"),(1050,250))
    elif card.name == "wind":#打出后显示“唯快不破！”
        attacker.speed += 20      #——————————————————————————————————————————————————————————————————————————————————————修改处
        print(f"{attacker.name} uses {card.name}, SPD increased by 5 to {attacker.speed}")
        if game is not None:
            game.show_card_effect_image(resource_path("fire_and_water/wind_text.png"),(1050,250))
    elif card.name == "regive":#打出后显示“请你大方一点”
        if game is not None:
            if defender == game.computer and len(game.computer_hand) > 0:
                stolen = game.computer_hand.pop(0)
                game.player_hand.append(stolen)
                print(f"{attacker.name} uses {card.name} to take opponent's first card: {stolen.name}")
            elif defender == game.player and len(game.player_hand) > 0:
                stolen = game.player_hand.pop(0)
                game.computer_hand.append(stolen)
                print(f"{attacker.name} uses {card.name} to take opponent's first card: {stolen.name}")
            game.show_card_effect_image(resource_path("fire_and_water/regive_text.png"),(1050,250))
    elif card.name == "REGIVE":#打出后显示“请你务必再大方一点”
        if game is not None:
            if defender == game.computer and len(game.computer_hand) > 0:
                stolen = game.computer_hand.pop(0)
                game.player_hand.append(stolen)
                extra = deal_card()
                game.player_hand.append(extra)
                print(f"{attacker.name} uses {card.name} to take opponent's card and extra {extra.name}")
            elif defender == game.player and len(game.player_hand) > 0:
                stolen = game.player_hand.pop(0)
                game.computer_hand.append(stolen)
                extra = deal_card()
                game.computer_hand.append(extra)
                print(f"{attacker.name} uses {card.name} to take opponent's card and extra {extra.name}")
            game.show_card_effect_image(resource_path("fire_and_water/more_regive_text.png"),(1050,250))
    elif card.name == "order":#打出后显示“秩序诞生……”
        # 序源：回复自身2点HP，并删除己方牌堆中的第一张牌（若有）
        #电脑免疫这样的效果
        heal=2
        if game.hardest and attacker.name=="Player":
            heal+=2
        attacker.hp += heal
        game.show_heal(heal)
        game.heal += heal
        if game is not None:
            if attacker.name == "Player" and len(game.player_hand) > 0:
                removed = game.player_hand.pop(-1)#random.randint(0, len(game.player_hand))-2)
                print(f"{attacker.name} uses {card.name}: healed 2 HP and removed first card {removed.name}")
            elif attacker.name == "Computer" and len(game.computer_hand) > 0:
                print(f"{attacker.name} uses {card.name}: healed 2 HP ")
            else:
                print(f"{attacker.name} uses {card.name}: healed 2 HP, but hand is empty")
        else:
            print(f"{attacker.name} uses {card.name}: healed 2 HP (no card removed)")
        game.show_card_effect_image(resource_path("fire_and_water/order__text.png"),(1050,250))
    elif card.name == "ORDER":#打出后显示“这是时间的尽头……”
        if game is not None:
            for _ in range(2):
                if game.animating_card is None:
                    game.start_animating_card("player")
                else:
                    game.player_hand.append(deal_card())
                game.computer_hand.append(deal_card())
                game.adjust_hand(game.computer_hand, "Computer")
            print(f"{attacker.name} uses {card.name}: both sides gain 2 new cards")
            game.show_card_effect_image(resource_path("fire_and_water/ORDER_text.png"),(1050,250))
    elif card.name == "back_go":  # "君子报仇，十年！......"
        if attacker.name == "Player":

            print(f"{attacker.name} uses {card.name}: Player will gain 1 extra move next turn")
            # 从玩家手牌中移除卡牌

            game.player_hand.remove(card)
            print("需要结束当前回合")
            print("是否结束？==============")
        elif attacker.name=="computer":
            print("电脑成功使用backgo")
            game.pending_extra_moves_for_computer = 1
            print("!!!!!!!!!!!!!!!!!!!1成功+1")
            print(f"{attacker.name} uses {card.name}: Computer will gain 1 extra move next turn")

            # 从电脑手牌中移除卡牌
            if card in game.computer_hand:
                game.computer_hand.remove(card)
        game.show_card_effect_image(resource_path("fire_and_water/back_go_text.png"), (1050, 250))
    elif card.name == "burn":#打出后显示“我以我血！……”
        if attacker.water_attach:
            attacker.water_attach = False
            attacker.fire_attach = False
            attacker.burn_bonus=True
        else:
            attacker.fire_attach = True
            attacker.burn_bonus = True

        print(f"{attacker.name} uses {card.name}: fire_attach set true, burn bonus activated")
        if game is not None:
            game.show_card_effect_image(resource_path("fire_and_water/burn_text.png"),(1050,250))
    elif card.name == "flood":#打出后显示“滔天于我之内！
        heal=1
        if game.hardest and attacker.name=="Player":
            heal+=2
        if attacker.fire_attach:
            attacker.fire_attach = False
            attacker.water_attach = False
        else:
            attacker.water_attach = True
        attacker.hp += heal
        game.heal += heal
        print(f"{attacker.name} uses {card.name}: water_attach set true, healed 1 HP")
        if game is not None:
            if game.hardest and attacker.name=="Player":
                game.show_heal(3)
            else:
                game.show_heal(1)
        game.show_card_effect_image(resource_path("fire_and_water/flood_text.png"),(1050,250))
    elif card.name == "timer":#打出后显示“时间回应了我！”
        extra_moves = 1
        n = game.player_moves
        game.player_moves += extra_moves
        heal_val = 2 * n
        if game.hardest and attacker.name=="Player":
            heal_val*=2
        if attacker.name=="Computer":
            game.computer.hp+=2
            game.show_heal(2)
            game.end_computer_turn()
        else:
            attacker.hp += heal_val

            game.heal += heal_val
            print(f"{attacker.name} uses {card.name}: gains 1 move and heals {heal_val} HP")
            if game is not None:
                game.show_heal(heal_val)
                game.show_card_effect_image(resource_path("fire_and_water/timer_text.png"),(1050,300))
            if game.current_turn == "player":
                if len(game.player_hand)==1:
                    print("no man!")
                else:
                    game.end_player_turn()  # 强制结束玩家回合
            elif game.current_turn == "computer":
                game.end_computer_turn()  # 强制结束电脑回合
    elif card.name == "get_time":#打出后显示“纵使光阴如梭”
        if game is not None and attacker.name == "Player":
            game.player_moves += 3
            print(f"{attacker.name} uses {card.name}: gains 2 extra moves")
        elif game is not None and attacker.name == "computer":
            game.pending_extra_moves_for_computer = 2
            print(f"{attacker.name} uses {card.name}: Computer will gain 2 extra moves next turn")
            game.end_computer_turn()
        if game is not None:
            game.show_card_effect_image(resource_path("fire_and_water/get_time_text.png"),(1050,250))
    elif card.name == "GETTIME":#打出后显示“岁月如我心漫长”
        if game is not None and attacker.name == "Player":
            game.player_moves += 4
            print(f"{attacker.name} uses {card.name}: gains 4 extra moves")
        elif game is not None and attacker.name == "computer":
            game.pending_extra_moves_for_computer = 4
            print(f"{attacker.name} uses {card.name}: Computer will gain 4 extra moves next turn")
            game.end_computer_turn()
        if game is not None:
            game.show_card_effect_image(resource_path("fire_and_water/GETTIME_text.png"),(1050,250))
    else:
        print(f"{attacker.name} uses {card.name} (effect not implemented)")
    # 在卡牌效果处理完毕后，统一移除卡牌
    if game is not None:
        if attacker.name == "Player" and card in game.player_hand:
            game.player_hand.remove(card)  # 从玩家手牌中移除
        elif attacker.name == "Computer" and card in game.computer_hand:
            game.computer_hand.remove(card)  # 从电脑手牌中移除

    # 更新状态
    attacker.update_status()
    defender.update_status()


# ----------------------------
# 辅助函数：查找手牌中指定卡牌索引
# ----------------------------
def get_hand_index_from_card(hand, card):
    for i, c in enumerate(hand):
        if c == card:
            return i
    return None


# ----------------------------
# 电脑出牌决策
# ----------------------------
#出伤的排列组合
LWJJ = {
    # 火系组合
    "fire_attack": {
        "required_cards": ["fireK", "FK", "fireD", "burn"],
        "priority": 1,
        "damage_table": {
            1: [(["fireK"], 1)],
            2: [
                (["fireK", "water"], 3),  # 对方水附着
                (["fireK", "fireD"], 5),  # 火盾
                (["fireK", "burn"], 6),   # 濒死状态
                (["fireK", "FK"], 5),     # 火刃
            ],
            3: [
                (["fireK", "water", "fireD"], 7),  # 火盾 + 对方水附着
                (["fireK", "water", "burn"], 8),   # 濒死状态 + 对方水附着
                (["fireK", "fireD", "burn"], 10),  # 火盾 + 濒死状态
                (["fireK", "FK", "water"], 7),     # 火刃 + 对方水附着
                (["fireK", "FK", "fireD"], 9),     # 火刃 + 火盾
                (["fireK", "FK", "burn"], 10),     # 火刃 + 濒死状态
                (["fireK", "FK", "burn"], 7),      # 火刃 + 自我燃烧
            ],
            4: [
                (["fireK", "water", "fireD", "burn"], 12),  # 火盾 + 濿死状态 + 对方水附着
                (["fireK", "FK", "water", "fireD"], 11),    # 火刃 + 火盾 + 对方水附着
                (["fireK", "FK", "water", "burn"], 12),     # 火刃 + 濿死状态 + 对方水附着
                (["fireK", "FK", "fireD", "burn"], 14),     # 火刃 + 火盾 + 濿死状态
                (["fireK", "FK", "burn", "water"], 9),      # 火刃 + 自我燃烧 + 对方水附着
                (["fireK", "FK", "burn", "fireD"], 11),     # 火刃 + 自我燃烧 + 火盾
                (["fireK", "FK", "fire", "water"], 10),     # 火刃 + 预先火附着 + 对方水附着
                (["fireK", "FK", "fire", "fireD"], 12),     # 火刃 + 预先火附着 + 火盾
            ],
            5: [
                (["fireK", "FK", "water", "fireD", "burn"], 16),  # 火刃 + 火盾 + 濿死状态 + 对方水附着
                (["fireK", "FK", "burn", "water", "fireD"], 13),  # 火刃 + 自我燃烧 + 火盾 + 对方水附着
                (["fireK", "FK", "burn", "water", "fireD"], 14),  # 火刃 + 自我燃烧 + 濿死状态 + 对方水附着
                (["fireK", "FK", "burn", "fireD", "burn"], 16),   # 火刃 + 自我燃烧 + 火盾 + 濿死状态
                (["fireK", "FK", "fire", "water", "fireD"], 14),  # 火刃 + 预先火附着 + 火盾 + 对方水附着
                (["fireK", "FK", "fire", "water", "burn"], 15),   # 火刃 + 预先火附着 + 濿死状态 + 对方水附着
                (["fireK", "FK", "fire", "fireD", "burn"], 17),   # 火刃 + 预先火附着 + 火盾 + 濿死状态
                (["fireK", "FK", "fire", "burn", "water"], 12),   # 火刃 + 预先火附着 + 自我燃烧 + 对方水附着
                (["fireK", "FK", "fire", "burn", "fireD"], 14),   # 火刃 + 预先火附着 + 自我燃烧 + 火盾
            ],
            6: [
                (["fireK", "FK", "burn", "water", "fireD", "burn"], 18),  # 火刃 + 自我燃烧 + 火盾 + 濿死状态 + 对方水附着
                (["fireK", "FK", "fire", "water", "fireD", "burn"], 19),  # 火刃 + 预先火附着 + 火盾 + 濿死状态 + 对方水附着
                (["fireK", "FK", "fire", "burn", "water", "fireD"], 16),  # 火刃 + 预先火附着 + 自我燃烧 + 火盾 + 对方水附着
                (["fireK", "FK", "fire", "burn", "water", "fireD"], 21),  # 火刃 + 预先火附着 + 自我燃烧 + 火盾 + 濿死状态 + 对方水附着
            ]
        }
},
"water_attack": {
    "required_cards": ["waterK", "WK", "waterD", "flood"],
    "priority": 2,
    "heal_table": {
        1: [(["waterK"], (1, 0))],  # 基础伤害 1，无治疗
        2: [(["waterK", "WK"], (3, 3))],  # 水刃，伤害 3，治疗 3
        3: [
            (["waterK", "WK", "water"], (3, 3)),  # 水刃 + 水附着，伤害 3，治疗 3
            (["waterK", "WK", "flood"], (3, 6)),  # 水刃 + 自我淹没，伤害 3，治疗 6
            (["waterK", "WK", "waterD"], (3, 3)),  # 水刃 + 水盾，伤害 3，治疗 3
            (["waterK", "WK", "burn"], (5, 10)),  # 水刃 + 濒死状态，伤害 5，治疗 10
            (["waterK", "WK", "fire"], (6, 6)),  # 水刃 + 对方火附着，伤害 6，治疗 6
        ],
        4: [
            (["waterK", "WK", "water", "waterD"], (3, 6)),  # 水刃 + 水附着 + 水盾，伤害 3，治疗 6
            (["waterK", "WK", "water", "flood"], (3, 9)),  # 水刃 + 水附着 + 自我淹没，伤害 3，治疗 9
            (["waterK", "WK", "water", "burn"], (5, 15)),  # 水刃 + 水附着 + 濒死状态，伤害 5，治疗 15
            (["waterK", "WK", "water", "fire"], (6, 12)),  # 水刃 + 水附着 + 对方火附着，伤害 6，治疗 12
            (["waterK", "WK", "flood", "waterD"], (3, 9)),  # 水刃 + 自我淹没 + 水盾，伤害 3，治疗 9
            (["waterK", "WK", "flood", "burn"], (5, 20)),  # 水刃 + 自我淹没 + 濒死状态，伤害 5，治疗 20
            (["waterK", "WK", "flood", "fire"], (6, 18)),  # 水刃 + 自我淹没 + 对方火附着，伤害 6，治疗 18
            (["waterK", "WK", "burn", "waterD"], (5, 15)),  # 水刃 + 濒死状态 + 水盾，伤害 5，治疗 15
            (["waterK", "WK", "burn", "fire"], (8, 32)),  # 水刃 + 濒死状态 + 对方火附着，伤害 8，治疗 32
            (["waterK", "WK", "fire", "waterD"], (6, 18)),  # 水刃 + 对方火附着 + 水盾，伤害 6，治疗 18
        ],
        5: [
            (["waterK", "WK", "water", "flood", "waterD"], (3, 12)),  # 水刃 + 水附着 + 自我淹没 + 水盾，伤害 3，治疗 12
            (["waterK", "WK", "water", "flood", "burn"], (5, 25)),  # 水刃 + 水附着 + 自我淹没 + 濒死状态，伤害 5，治疗 25
            (["waterK", "WK", "water", "flood", "fire"], (6, 24)),  # 水刃 + 水附着 + 自我淹没 + 对方火附着，伤害 6，治疗 24
            (["waterK", "WK", "water", "burn", "waterD"], (5, 20)),  # 水刃 + 水附着 + 濒死状态 + 水盾，伤害 5，治疗 20
            (["waterK", "WK", "water", "burn", "fire"], (8, 40)),  # 水刃 + 水附着 + 濒死状态 + 对方火附着，伤害 8，治疗 40
            (["waterK", "WK", "water", "fire", "waterD"], (6, 27)),  # 水刃 + 水附着 + 对方火附着 + 水盾，伤害 6，治疗 27
            (["waterK", "WK", "flood", "burn", "waterD"], (5, 25)),  # 水刃 + 自我淹没 + 濒死状态 + 水盾，伤害 5，治疗 25
            (["waterK", "WK", "flood", "burn", "fire"], (8, 48)),  # 水刃 + 自我淹没 + 濒死状态 + 对方火附着，伤害 8，治疗 48
            (["waterK", "WK", "flood", "fire", "waterD"], (6, 36)),  # 水刃 + 自我淹没 + 对方火附着 + 水盾，伤害 6，治疗 36
            (["waterK", "WK", "burn", "fire", "waterD"], (8, 48)),  # 水刃 + 濒死状态 + 对方火附着 + 水盾，伤害 8，治疗 48
        ],
        6: [
            (["waterK", "WK", "water", "flood", "burn", "waterD"], (5, 30)),  # 水刃 + 水附着 + 自我淹没 + 濒死状态 + 水盾，伤害 5，治疗 30
            (["waterK", "WK", "water", "flood", "burn", "fire"], (8, 64)),  # 水刃 + 水附着 + 自我淹没 + 濒死状态 + 对方火附着，伤害 8，治疗 64
            (["waterK", "WK", "water", "flood", "fire", "waterD"], (6, 45)),  # 水刃 + 水附着 + 自我淹没 + 对方火附着 + 水盾，伤害 6，治疗 45
            (["waterK", "WK", "water", "burn", "fire", "waterD"], (8, 60)),  # 水刃 + 水附着 + 濒死状态 + 对方火附着 + 水盾，伤害 8，治疗 60
            (["waterK", "WK", "flood", "burn", "fire", "waterD"], (8, 60)),  # 水刃 + 自我淹没 + 濒死状态 + 对方火附着 + 水盾，伤害 8，治疗 60
        ],
        7: [
            (["waterK", "WK", "water", "flood", "burn", "fire", "waterD"], (8, 72)),  # 水刃 + 水附着 + 自我淹没 + 濒死状态 + 对方火附着 + 水盾，伤害 8，治疗 72
            ]
        }
    }
}

def easy(computer_hand):
    ans=[]
    if computer_hand:
        for card in computer_hand:
            if card.name == "fireK":
                ans.append(card.name)
                return ans
            elif card.name == "waterK":
                ans.append(card.name)
                return ans
            elif card.name in ["fireD", "waterD"]:
                ans.append(card.name)
                return ans
        card=computer_hand[0]
        ans.append(card.name)
        return ans
    else:
        return []

def middle(hand,computer,player,game):
    ans=[]
    # 统计电脑手牌中每种牌的数量
    card_counts = {}
    for card in hand:
        card_counts[card.name] = card_counts.get(card.name, 0) + 1

    # 牌总数
    total_card = 0
    for i, j in card_counts.items():
        total_card += j
    # 重新获取电脑和玩家的状态
    # 获取玩家和电脑的状态
    player_fire_attach = player.fire_attach
    player_water_attach = player.water_attach
    computer_fire_attach = computer.fire_attach
    computer_water_attach = computer.water_attach
    player_FD = game.player.FD
    player_WD = game.player.WD
    computer_speed=computer.speed
    player_speed=player.speed
    if hand:
        if (player_FD and player_WD) or(card_counts.get("fireK",0==0) and card_counts.get("waterK",0)==0):
            for i in hand:
                if i.name=="fast" or i.name=="wind":
                    ans.append(i.name)
                elif i.name=="regive" or i.name=="REGIVE":
                    ans.append(i.name)
                elif i.name=="ORDER":
                    ans.append(i.name)
                elif i.name=="get_time" or i.name=="GETTIME":
                    ans.append(i.name)
                elif i.name=="water" or i.name=="fire" or i.name=="timer" or i.name=="order" or i.name=="flood":
                    ans.append(i.name)
                elif i.name=="waterD" or i.name=="fireD":
                    ans.append(i.name)
                else:
                    card = hand[0]
                    ans.append(card.name)
                    return ans
        elif player_WD or (card_counts.get("fireK",0)>0 and card_counts.get("waterK",0)==0) or(card_counts.get("fireK",0)>0 and player_water_attach):
            for i in hand:
                if i.name=="fireK":
                    ans.append(i.name)
                else:
                    card = hand[0]
                    ans.append(card.name)
                    return ans
        elif player_FD or (card_counts.get("waterK", 0) > 0 and card_counts.get("fireK", 0) == 0) or (
                card_counts.get("waterK", 0) > 0 and player_fire_attach):
            for i in hand:
                if i.name=="waterK":
                    ans.append(i.name)
                else:
                    card = hand[0]
                    ans.append(card.name)
                    return ans
        else:
            card = hand[0]
            ans.append(card.name)
            return ans
    else:
        return []



def get_first_card_index(computer_hand, card_name):
    """
    获取某种牌在牌堆中的第一个索引。

    参数:
        hand (list): 牌堆（玩家或电脑的手牌列表）
        card_name (str): 要查找的牌的名称（如 "火杀"、"水杀" 等）

    返回:
        int: 牌的索引（如果找到），否则返回 -1
    """
    for index, card in enumerate(computer_hand):
        if card.name == card_name:
            return index
    return -1  # 如果没有找到该牌，返回 -1


def get_all_card_indices(computer_hand, card_name):
    """
    获取某种牌在牌堆中的所有索引。

    参数:
        hand (list): 牌堆（玩家或电脑的手牌列表）
        card_name (str): 要查找的牌的名称（如 "火杀"、"水杀" 等）

    返回:
        list: 所有匹配牌的索引列表（如果没有找到，返回空列表）
    """
    return [index for index, card in enumerate(computer_hand) if card.name == card_name]

def rlw(lst:list):
    seen = set()  # 创建一个空集合，用于存储已经出现过的元素
    result = []  # 创建一个空列表，用于存储去重后的结果
    for item in lst:
        if item not in seen:  # 如果当前元素不在集合中
            seen.add(item)  # 将当前元素添加到集合中
            result.append(item)  # 将当前元素添加到结果列表中
    return result

def computer_choose_card(computer_hand, computer, player, game):
    if game.hard==False:
        if game.hardest==False:
            return
    elif game.hardest==False:
        if game.hard==False:
            return
    # 统计电脑手牌中每种牌的数量
    computer_hand = game.computer_hand
    card_counts = {}
    for card in computer_hand:
        card_counts[card.name] = card_counts.get(card.name, 0) + 1

    # 牌总数
    total_card = 0
    for i, j in card_counts.items():
        total_card += j
    # 重新获取电脑和玩家的状态
    # 获取玩家和电脑的状态

    player_fire_attach = player.fire_attach
    player_water_attach = player.water_attach
    computer_fire_attach = computer.fire_attach
    computer_water_attach = computer.water_attach
    player_FD = game.player.FD
    player_WD = game.player.WD
    computer_speed=computer.speed
    player_speed=player.speed
    """优化后的电脑出牌决策函数"""
    print(f"[DEBUG] 电脑手牌: {[c.name for c in computer_hand]}")

    # ==================== 基础校验 ====================
    if len(computer_hand) < 3:
        print("手牌不足3张，跳过回合")
        return []

    # ==================== 状态分析 ====================
    card_counts = {c.name: 0 for c in computer_hand}
    for card in computer_hand:
        card_counts[card.name] += 1

    player_status = {
        'hp': player.hp,
        'fire_attach': player.fire_attach,
        'water_attach': player.water_attach,
        'FD': player.FD,
        'WD': player.WD,
        'speed': player.speed
    }
    computer_status = {
        'hp': computer.hp,
        'fire_attach': computer.fire_attach,
        'water_attach': computer.water_attach,
        'FD': computer.FD,
        'WD': computer.WD,
        'speed': computer.speed
    }

    # ==================== 单次出牌决策 ====================
    def single_play():
        """你的单次出牌逻辑封装"""
        if card_counts.get("GETTIME",0)>0 and len(computer_hand)>=5:
            return ["GETTIME"]
        if card_counts.get("get_time",0)>0 and len(computer_hand)>=3:
            return ["get_time"]
        # 攻击策略（经过安全校验）
        if player_status['FD'] and player_status['WD']:
            print("玩家双盾激活，停止攻击")
        elif (player_status['speed'] - computer_status['speed']) >= 75:
            print("速度差过大，停止攻击")
        elif player_FD and card_counts.get("fireK",0)>0 and card_counts.get("waterK",0)==0:
            print("不适合火杀出牌")
        elif player_WD and card_counts.get("fireK",0)==0 and card_counts.get("waterK",0)>0:
            print("不适合水杀出牌")
        else:
            if player_FD and card_counts.get("waterK",0)>0:
                return ["waterK"]
            if player_WD and card_counts.get("fireK",0)>0:
                return ["fireK"]
            if player_WD==False and player_fire_attach and card_counts.get("waterK",0)>0:
                return ["waterK"]
            if player_FD==False and player_water_attach and card_counts.get("fireK",0)>0:
                return ["fireK"]
            else:
                # 构建安全攻击列表（排除单独刃牌）
                attack_cards = [c for c in computer_hand
                                if c.name in ["fireK", "waterK"]
                                and not (c.name in ["FK", "WK"] and
                                         not any(card.name in ["fireK", "waterK"] for card in computer_hand))
                                ]
                if attack_cards:
                    return [attack_cards[0].name]  # 取第一个可用攻击牌


        for card in computer_hand:
            if card.name in ["regive", "REGIVE"] and game.player_hand:
                return [card.name]

        # 速度增益
        if card_counts.get("fast", 0) > 0 or card_counts.get("wind", 0) > 0 and computer_speed-player_speed<=80:
            for card in computer_hand:
                if card.name in ["fast", "wind"]:
                    return [card.name]

        # 默认防御
        shield_cards = [c for c in computer_hand if c.name in ["fireD", "waterD"]]
        if shield_cards:
            return [random.choice(shield_cards).name]
        elif computer_water_attach:
            for card in computer_hand:
                if card.name=="flood":
                    return [card.name]


        # 群体增益
        if card_counts.get("ORDER", 0) > 0:
            return [next(c.name for c in computer_hand if c.name == "ORDER")]

        # 防御策略
        if (game.hard and computer_status['hp'] <= 80)or(game.hardest and computer_status['hp']<=160):
            heal_cards = ["water", "fire", "timer", "order", "flood"]
            for card in computer_hand:
                if card.name in heal_cards:
                    return [card.name]

        if card_counts.get("fire",0)>0 and computer_fire_attach:
            for card in computer_hand:
                if card.name =="fire":
                    return[card.name]
        if card_counts.get("water",0)>0 and computer_water_attach:
            for card in computer_hand:
                if card.name =="water":
                    return[card.name]
        heal_cards = ["water", "fire", "timer", "order", "flood"]
        for card in computer_hand:
            if card.name in heal_cards:
                return [card.name]






        return []  # 无有效牌

    # ==================== 组合出牌决策 ====================

    def combo_play():
        """组合出牌逻辑（多出手）"""
        # 检测有效组合
        fire_combo = (
                any(c.name == "fireK" for c in computer_hand) and
                any(c.name in ["fireD", "burn", "FK"] for c in computer_hand)
        )
        water_combo = (
                any(c.name == "waterK" for c in computer_hand) and
                any(c.name in ["waterD", "flood", "WK"] for c in computer_hand)
        )
        fire_and_water_go=(
            any(c.name=="fireK" for c in computer_hand) and
            any(c.name == "waterK" for c in computer_hand)
        )
        play_order = []

        if fire_combo and player_FD==False:
            print("激活火系组合")
            # 非杀牌优先
            support = [c for c in computer_hand if c.name in ["fireD", "burn", "FK"]]
            kill = next(c for c in computer_hand if c.name == "fireK")
            play_order = support + [kill]
        elif water_combo and player_WD==False:
            print("激活水系组合")
            support = [c for c in computer_hand if c.name in ["waterD", "flood", "WK"]]
            kill = next(c for c in computer_hand if c.name == "waterK")
            play_order = support + [kill]
        elif fire_and_water_go and player_WD==False and player_FD==False:
            if player_fire_attach==False and player_water_attach==False:
                for card4 in computer_hand:
                    if (card4.name=="fireK" or card4.name=="waterK")and len(play_order)<=2:
                        play_order.append(card4)
            elif player_water_attach:
                for card4 in computer_hand:
                    if card4.name=="fireK":
                        play_order.append(card4)
                for card4 in computer_hand:
                    if card4.name=="waterK":
                        play_order.append(card4)
            elif player_fire_attach:
                for card4 in computer_hand:
                    if card4.name=="waterK":
                        play_order.append(card4)
                for card4 in computer_hand:
                    if card4.name=="fireK":
                        play_order.append(card4)



        # 修改后的去重逻辑：基于卡牌名称去重并保留顺序
        seen = set()
        play_order3 = []
        for card in play_order:
            if card.name not in seen:
                seen.add(card.name)
                play_order3.append(card.name)

        # 验证组合有效性
        if len(play_order3) >= 2:
            print(f"当前去重后的出牌决策队列：{play_order3}")
            op = 1  # 开始打补丁
            if "flood" in play_order3:
                print("开始打补丁")
                for i in play_order3:
                    if i == "WK" and computer_water_attach==False:
                        print("找到了，可以不补丁")
                        op = 0
                if op == 1:
                    print("补丁成功")
                    play_order3.remove("flood")
            return play_order3
        return []


    # ==================== 决策执行 ====================
    # 优先尝试组合出牌
    combo_cards = combo_play()
    if combo_cards:
        print(f"组合出牌序列: {[c for c in combo_cards]}")
        return combo_cards

    # 单次出牌
    single_card = single_play()
    if single_card:
        print(f"单次出牌: {single_card[0]}")
        return single_card

    print("无有效出牌策略，跳过回合")
    return combo_cards if combo_cards else single_card if single_card else []

def computer_extra_active_card(n:int,computer,player,game,fake:list):
    if game.hard==False:
        if game.hardest==False:
            return
    elif game.hardest==False:
        if game.hard==False:
            return
    if fake is None:
        return []
    if n==0:
        return fake
    fake.pop(-1)
    ex=n
    print("！！！电脑获取了被动出手数！！！")
    # 获取玩家和电脑的状态
    player_hp = player.hp
    computer_hp = computer.hp
    player_fire_attach = player.fire_attach
    player_water_attach = player.water_attach
    computer_fire_attach = computer.fire_attach
    computer_water_attach = computer.water_attach
    player_FD = game.player.FD
    player_WD = game.player.WD
    player_DEAD = player.DEAD
    computer_DEAD = computer.DEAD
    computer_speed = computer.speed
    player_speed = player.speed
    computer_hand=game.computer_hand
    card_counts = {}
    for card in computer_hand:
        card_counts[card.name] = card_counts.get(card.name, 0) + 1

    # 牌总数
    total_card = 0
    for i, j in card_counts.items():
        total_card += j
    ans=[]
    fire=[]
    water=[]
    for i in computer_hand:
        if i.name=="fireK" or i.name=="FK" or i.name=="burn":
            fire.append(i.name)
        elif i.name=="water" or i.name=="WK":
            water.append(i.name)
    if n==2:
        if player_WD:
            if card_counts.get("fireK",0)>0 and len(ans)<=2:
                if card_counts.get("FK",0)>0 and len(ans)<=2:
                    ans.append("FK")
                if card_counts.get("burn",0)>0 and len(ans)<=2:
                    ans.append("burn")
                if card_counts.get("fireD",0)>0 and len(ans)<=2:
                    ans.append("fireD")
                else:
                    for i in computer_hand:
                        if len(ans) == 2:
                            break
                        if i.name in fire or i.name in ans:
                            continue
                        ans.append(i.name)
                ans.append("fireK")
            else:
                for i in computer_hand:
                    if len(ans) == 2:
                        break
                    if i.name in fire or i.name in ans:
                        continue
                    ans.append(i.name)
        elif player_FD:
            if card_counts.get("waterK", 0) > 0 and len(ans)<=2:
                if card_counts.get("WK", 0) > 0 and len(ans)<=2:
                    ans.append("WK")
                if card_counts.get("flood", 0) > 0 and len(ans)<=2:
                    ans.append("flood")
                if card_counts.get("waterD", 0) > 0 and len(ans)<=2:
                    ans.append("waterD")
                else:
                    for i in computer_hand:
                        if len(ans) == 2:
                            break
                        if i.name in water or i.name in ans:
                            continue
                        ans.append(i.name)
                ans.append("waterK")
            else:
                for i in computer_hand:
                    if len(ans) == 2:
                        break
                    if i.name in fire or i.name in ans:
                        continue
                    ans.append(i.name)
        elif player_WD and player_FD:
            for i in computer_hand:
                if len(ans)==2:
                    break
                if i.name in fire or i.name in ans or i.name in water:
                    continue
                ans.append(i.name)
        else:
            for i in computer_hand:
                if len(ans)==2:
                    break
                ans.append(i.name)
    elif n==3:
        if player_WD:
            if card_counts.get("fireK", 0) > 0 and len(ans) <= 3:
                if card_counts.get("FK", 0) > 0 and len(ans) <= 3:
                    ans.append("FK")
                if card_counts.get("burn", 0) > 0 and len(ans) <= 3:
                    ans.append("burn")
                if card_counts.get("fireD", 0) > 0 and len(ans) <= 3:
                    ans.append("fireD")
                else:
                    for i in computer_hand:
                        if len(ans) == 3:
                            break
                        if i.name in fire or i.name in ans:
                            continue
                        ans.append(i.name)
                ans.append("fireK")
            else:
                for i in computer_hand:
                    if len(ans) == 3:
                        break
                    if i.name in fire or i.name in ans:
                        continue
                    ans.append(i.name)
        elif player_FD:
            if card_counts.get("waterK", 0) > 0 and len(ans) <= 3:
                if card_counts.get("WK", 0) > 0 and len(ans) <= 3:
                    ans.append("WK")
                if card_counts.get("flood", 0) > 0 and len(ans) <= 3:
                    ans.append("flood")
                if card_counts.get("waterD", 0) > 0 and len(ans) <= 3:
                    ans.append("waterD")
                else:
                    for i in computer_hand:
                        if len(ans) == 3:
                            break
                        if i.name in water or i.name in ans:
                            continue
                        ans.append(i.name)
                ans.append("waterK")
            else:
                for i in computer_hand:
                    if len(ans) == 3:
                        break
                    if i.name in fire or i.name in ans:
                        continue
                    ans.append(i.name)
        elif player_WD and player_FD:
            for i in computer_hand:
                if len(ans) == 3:
                    break
                if i.name in fire or i.name in ans or i.name in water:
                    continue
                ans.append(i.name)
        else:
            for i in computer_hand:
                if len(ans) == 3:
                    break
                ans.append(i.name)
    elif n==4:
        if player_FD:
            if card_counts.get("fireK",0)>0 and len(ans)<=4:
                if card_counts.get("FK",0)>0 and len(ans)<=4:
                    ans.append("FK")
                if card_counts.get("burn",0)>0 and len(ans)<=4:
                    ans.append("burn")
                if card_counts.get("fireD",0)>0 and len(ans)<=4:
                    ans.append("fireD")
                else:
                    for i in computer_hand:
                        if len(ans) == 4:
                            break
                        if i.name in fire or i.name in ans:
                            continue
                        ans.append(i.name)
                ans.append("fireK")
            else:
                for i in computer_hand:
                    if len(ans) == 4:
                        break
                    if i.name in fire or i.name in ans:
                        continue
                    ans.append(i.name)
        elif player_WD:
            if card_counts.get("waterK", 0) > 0 and len(ans)<=4:
                if card_counts.get("WK", 0) > 0 and len(ans)<=4:
                    ans.append("WK")
                if card_counts.get("flood", 0) > 0 and len(ans)<=4:
                    ans.append("flood")
                if card_counts.get("waterD", 0) > 0 and len(ans)<=4:
                    ans.append("waterD")
                else:
                    for i in computer_hand:
                        if len(ans) == 4:
                            break
                        if i.name in fire or i.name in ans:
                            continue
                        ans.append(i.name)
                ans.append("waterK")
            else:
                for i in computer_hand:
                    if len(ans) == 4:
                        break
                    if i.name in fire or i.name in ans:
                        continue
                    ans.append(i.name)
        elif player_WD and player_FD:
            for i in computer_hand:
                if len(ans)==4:
                    break
                if i.name in fire or i.name in ans or i.name in water:
                    continue
                ans.append(i.name)
        elif card_counts.get("fireK",0)>0 and card_counts.get("waterK",0)>0:
            ans.append("fireK")
            ans.append("waterK")
            for i in computer_hand:
                if len(ans)==2:
                    break
                if i.name in fire or i.name in ans or i.name in water:
                    continue
                ans.append(i.name)
        else:
            for i in computer_hand:
                if len(ans)==4:
                    break
                if (i.name in fire) or (i.name in ans) or (i.name in water):
                    continue
                ans.append(i.name)
    if "fireK" in ans:
        ans.remove("fireK")
        ans.append("fireK")
    elif "waterK" in ans:
        ans.remove("waterK")
        ans.append("waterK")
    if len(ans)<n and card_counts.get("timer",0)>0:
        ans.append("timer")
    if "get_time" in ans and len(game.computer_hand)<2:
        ans.remove("get_time")
    if "GETTIME" in ans and len(game.computer_hand)<5:
        ans.remove("GETTIME")
    if "back_go" in ans:
        ans.remove("back_go")


    ans.append(ex)
    return ans





def computer_consume_cards(game, protected: list, n: int):
    if game.hard==False:
        if game.hardest==False:
            return
    elif game.hardest==False:
        if game.hard==False:
            return
    if game.hardest==True:
        op=len(protected)
        actual=protected
        actual.append(op)
        return actual
    """
    优化后的电脑消耗卡牌逻辑函数。
    根据受保护的卡牌列表和需要的额外出手次数，消耗多余的卡牌。

    参数:
        game: 游戏对象，包含电脑手牌等信息。
        protected: 受保护的卡牌列表（核心组合牌）。
        n: 需要获取的额外出手次数（通常为组合牌长度减1）。

    返回:
        实际消耗的卡牌数量。
    """
    consume_count = 0
    hand=game.computer_hand
    check_hand={}
    for i in hand:
        check_hand[i.name]=check_hand.get(i.name, 0) + 1
        print(f"当前收集的是{i.name}牌，有{check_hand[i.name]}张")
    print(f"当前所需要获取的额外出手数为 {n - 1}")
    # 初始化日志和计数器
    print("\n=== 开始消耗卡牌 ===")
    #边际效应情况
    #杀——盾，火；盾，刃；火刃
    fire_check={"fireK":1,"FK":1,"burn":1,"FD":1}
    water_check={"waterK":1,"WK":1,"flood":1,"WD":1}
    if len(hand)==3 and ((check_hand.get("fireK",0)>0 and check_hand.get("FK",0)>0 and check_hand.get("burn",0)>0) or (check_hand.get("fireK",0)>0 and check_hand.get("FK",0)>0 and check_hand.get("fireD",0)>0) or (check_hand.get("fireK",0)>0 and check_hand.get("fireD",0)>0 and check_hand.get("burn",0)>0)):
        print("开始三张式火杀边际效应")
        if check_hand.get("fireK",0)>0:
            if check_hand.get("FK",0)>0 and check_hand.get("burn",0)>0:
                print("此移除自我燃烧")
                for card in hand:
                    if card.name=="burn":
                        hand.remove(card)
                consume_count+=1
                protected.remove("burn")
                actual_queue=protected
                actual_queue.append(consume_count)
                return actual_queue
            elif check_hand.get("FK",0)>0 and check_hand.get("fireD",0)>0:
                print("此移除火刃")
                for card in hand:
                    if card.name=="FK":
                        hand.remove(card)
                consume_count+=1
                protected.remove("FK")
                actual_queue=protected
                actual_queue.append(consume_count)
                return actual_queue
            elif check_hand.get("burn",0)>0 and check_hand.get("fireD",0)>0:
                print("此移除自我燃烧")
                for card in hand:
                    if card.name=="burn":
                        hand.remove(card)
                consume_count+=1
                protected.remove("burn")
                actual_queue=protected
                actual_queue.append(consume_count)
                return actual_queue
    elif len(hand)==3 and ((check_hand.get("waterK",0)>0 and check_hand.get("WK",0)>0 and check_hand.get("flood",0)>0) or (check_hand.get("waterK",0)>0 and check_hand.get("WK",0)>0 and check_hand.get("waterD",0)>0) or (check_hand.get("waterK",0)>0 and check_hand.get("waterD",0)>0 and check_hand.get("flood",0)>0)):
        print("开始三张式水杀边际效应")
        if check_hand.get("waterK",0)>0:
            if check_hand.get("WK",0)>0 and check_hand.get("flood",0)>0:
                print("此移除自我淹没")
                for card in hand:
                    if card.name=="flood":
                        hand.remove(card)
                consume_count+=1
                protected.remove("flood")
                actual_queue=protected
                actual_queue.append(consume_count)
                return actual_queue
            elif check_hand.get("WK",0)>0 and check_hand.get("waterD",0)>0:
                print("此移除水刃")
                for card in hand:
                    if card.name=="waterK":
                        hand.remove(card)
                consume_count+=1
                protected.remove("waterK")
                actual_queue=protected
                actual_queue.append(consume_count)
                return actual_queue
            elif check_hand.get("flood",0)>0 and check_hand.get("waterD",0)>0:
                print("此移除自我淹没")
                for card in hand:
                    if card.name=="flood":
                        hand.remove(card)
                consume_count+=1
                protected.remove("flood")
                actual_queue=protected
                actual_queue.append(consume_count)
                return actual_queue


    elif len(hand)==4 and ((check_hand.get("fireK",0)>0 and check_hand.get("FK",0)>0 and check_hand.get("burn",0)>0) or (check_hand.get("fireK",0)>0 and check_hand.get("FK",0)>0 and check_hand.get("fireD",0)>0) or (check_hand.get("fireK",0)>0 and check_hand.get("fireD",0)>0 and check_hand.get("burn",0)>0)):
        print("开始火杀边际效应==========================")
        if check_hand.get("fireK",0)>0:
            for i,j in check_hand.items():
                if  fire_check.get(i,0)==0:
                    for card in hand:
                        if card.name==i:
                            print(f"不可承受之边际效用的重，移除卡牌{i}")
                            hand.remove(card)
                            if check_hand.get("burn",0)>0 and "burn" in protected:
                                protected.remove("burn")
                            elif check_hand.get("FK",0)>0 and "FK" in protected:
                                protected.remove("FK")
                            consume_count+=1

                            print(f"===总计小号{consume_count}张牌===\n")
                            print(f"消耗后的出牌决策为{[c for c in protected]}")
                            actual_queue=protected
                            actual_queue.append(consume_count)
                            return actual_queue
            for i, j in check_hand.items():
                if i in protected and j>1 :
                    for card in hand:
                        if card.name==i:
                            print(f"不可承受之边际效用的重，移除卡牌{i}")
                            hand.remove(card)
                            #总之优先打出火刃和火杀
                            if check_hand.get("burn",0)>0 and "burn" in protected:#pro:火杀，火盾,hand:火杀，火刃，火盾
                                if card.name != "fireK":
                                    protected.remove(i)
                                else:
                                    protected.remove("burn")
                            elif check_hand.get("fireD",0)>0 and "fireD" in protected:
                                if card.name != "fireK":
                                    protected.remove(i)
                                else:
                                    protected.remove("fireK")
                        consume_count+=1
                        # 返回实际消耗的卡牌数量
                        print(f"=== 总计消耗 {consume_count} 张牌 ===\n")
                        print(f"当前出牌决策{[c for c in protected]}")
                        actual_queue = protected
                        actual_queue.append(consume_count)
                        return actual_queue

    elif len(protected)==3 and len(hand)==4 and ((check_hand.get("waterK",0)>0 and check_hand.get("WK",0)>0  and check_hand.get("waterD",0)>0 )or (check_hand.get("waterK",0)>0 and check_hand.get("WK",0)>0 and check_hand.get("flood",0)>0) or (check_hand.get("waterK",0)>0 and check_hand.get("waterD",0)>0 and check_hand.get("flood",0)>0)):
            print("==========进入水杀三种四张边际效应========")
            for i,j in check_hand.items():
                if  water_check.get(i,0)==0:
                    for card in hand:
                        if card.name==i:
                            print(f"不可承受之边际效用的重，移除卡牌{i}")
                            hand.remove(card)
                            if check_hand.get("flood",0)>0 and "flood" in protected:
                                protected.remove("flood")
                            elif check_hand.get("Water",0)>0 and "waterD" in protected:
                                protected.remove("waterD")
                                consume_count+=1
                            print(f"===总计消耗{consume_count}张牌===\n")
                            print(f"消耗后的出牌决策为{[c for c in protected]}")
                            actual_queue=protected
                            actual_queue.append(consume_count)
                            return actual_queue
            for i, j in check_hand.items():
                if i in protected and j>1:
                    for card in hand:
                        if card.name==i:
                            print(f"不可承受之边际效用的重，移除卡牌{i}")
                            hand.remove(card)
                            #总之优先打出水杀
                            if check_hand.get("flood", 0) > 0 and "flood" in protected:
                                if card.name != "waterK":
                                    protected.remove(i)
                                else:
                                    protected.remove("flood")
                            elif check_hand.get("waterD", 0) > 0 and "waterD" in protected:
                                if card.name != "waterK":
                                    protected.remove(i)
                                else:
                                    protected.remove("waterD")
                        consume_count += 1
                        # 返回实际消耗的卡牌数量
                        print(f"=== 总计消耗 {consume_count} 张牌 ===\n")
                        print(f"当前出牌决策{[c for c in protected]}")
                        actual_queue = protected
                        actual_queue.append(consume_count)
                        return actual_queue
    elif len(hand) == 5 and (check_hand.get("fireK", 0) > 0 and check_hand.get("FK", 0) > 0 and check_hand.get("burn", 0) > 0
            and check_hand.get("fireD",0)>0) :
        if check_hand.get("fireK", 0) > 0:
            for i, j in check_hand.items():
                if  fire_check.get(i,0)==0:
                    for card in hand:
                        if card.name==i:
                            print(f"不可承受之边际效用的重，移除卡牌{i}和一张相对低效率牌")
                            hand.remove(card)
                            if check_hand.get("burn",0)>0 and "burn" in protected:
                                hand.remove("burn")
                                protected.remove("burn")
                            elif check_hand.get("FK",0)>0 and "FK" in protected:
                                protected.remove("FK")
                            consume_count+=2
                            print(f"===总计小号{consume_count}张牌===\n")
                            print(f"消耗后的出牌决策为{[c for c in protected]}")
                            actual_queue=protected
                            actual_queue.append(consume_count)
                            return actual_queue
            for i, j in check_hand.items():
                if i in fire_check and j > 1:
                    for card ,card1 in hand:
                        card1.name="burn"
                        if card.name == i:
                            print(f"不可承受之边际效用的重，移除卡牌一张{i}和一张自我燃烧")
                            hand.remove(card)
                            hand.remove(card1)
                            protected.remove("burn")
                        consume_count += 2
                        # 返回实际消耗的卡牌数量
                        print(f"=== 总计消耗 {consume_count} 张牌 ===\n")
                        print(f"当前出牌决策{[c for c in protected]}")
                        actual_queue = protected
                        actual_queue.append(consume_count)
                        return actual_queue
    elif len(hand) == 5 and (check_hand.get("waterK",0)>0 and check_hand.get("WK",0)>0 and check_hand.get("waterD",0)>0 and check_hand.get("flood",0)>0):
        if check_hand.get("waterK", 0) > 0:
            for i, j in check_hand.items():
                if  water_check.get(i,0)==0:
                    for card in hand:
                        if card.name==i:
                            print(f"不可承受之边际效用的重，移除卡牌{i}和一张相对低效率牌")
                            hand.remove(card)
                            if check_hand.get("flood",0)>0 and "flood" in protected:
                                hand.remove("flood")
                                protected.remove("flood")
                            elif check_hand.get("waterD",0)>0 and "waterD" in protected:
                                protected.remove("waterD")
                            consume_count+=2
                            print(f"===总计小号{consume_count}张牌===\n")
                            print(f"消耗后的出牌决策为{[c for c in protected]}")
                            actual_queue=protected
                            actual_queue.append(consume_count)
                            return actual_queue
            for i, j in check_hand.items():
                if  i in water_check and j > 1:
                    for card ,card1 in hand:
                        card1.name="flood"
                        if card.name == i:
                            print(f"不可承受之边际效用的重，移除卡牌一张{i}和一张自我燃淹没")
                            hand.remove(card)
                            hand.remove(card1)
                            protected.remove("flood")
                        consume_count += 2
                        # 返回实际消耗的卡牌数量
                        print(f"=== 总计消耗 {consume_count} 张牌 ===\n")
                        print(f"当前出牌决策{[c for c in protected]}")
                        actual_queue = protected
                        actual_queue.append(consume_count)
                        return actual_queue
    #非边际效应情况
    else:
        # 统计手牌中每种卡牌的数量
        card_counts = {}
        for card in game.computer_hand:
            card_counts[card.name] = card_counts.get(card.name, 0) + 1

        # 计算可消耗的卡牌数量
        # 对于受保护的卡牌，最多只能消耗 (总数 - 1) 张
        # 对于非受保护的卡牌，可以消耗全部
        deconsume = {}
        for name, count in card_counts.items():
            if name in protected:
                deconsume[name] = max(count - 1, 0)  # 确保至少保留一张受保护的卡牌
            else:
                deconsume[name] = count  # 非受保护的卡牌可以全部消耗

        # 计算总可消耗的卡牌数量
        consume_total = sum(deconsume.values())

        # 如果总可消耗卡牌数量不足以支持组合牌，动态调整受保护的卡牌列表
        required = n - 1  # 需要消耗的卡牌数量
        while consume_total < required and protected:
            # 移除一个受保护的卡牌，简化组合
            removed = protected.pop(0)
            print(f"⚠️ 资源不足，自动移除组合牌 {removed}")

            # 重新计算可消耗的卡牌数量
            deconsume = {name: (count - 1 if name in protected else count)
                         for name, count in card_counts.items()}
            consume_total = sum(deconsume.values())

        # 如果没有足够的卡牌可以消耗，直接返回
        if consume_total < required:
            print(f"⚠️ 警告：卡牌不足，无法完成消耗")
            return [0]
        # 开始消耗卡牌
        consumable = [c for c in game.computer_hand
                      if (c.name not in protected) or  # 非受保护的卡牌
                      (c.name in protected and card_counts[c.name] > 1)]  # 受保护的卡牌，且有多余

        # 按优先级消耗卡牌
        # 优先消耗非受保护的卡牌，其次消耗多余的受保护卡牌
        while len(consumable) > 0 and consume_count < required:
            # 优先消耗非受保护的卡牌
            for card in consumable[:]:  # 使用副本遍历，避免修改列表时出错
                if card.name not in protected:
                    # 消耗卡牌
                    idx = game.computer_hand.index(card)
                    removed = game.computer_hand.pop(idx)
                    consume_count += 1
                    print(f"消耗 {removed.name} (剩余手牌: {len(game.computer_hand)})")
                    pygame.time.delay(500)  # 添加延迟，模拟动画效果
                    consumable.remove(card)  # 从可消耗列表中移除
                    if consume_count >= required:
                        break

            # 如果没有非受保护的卡牌可消耗，开始消耗多余的受保护卡牌
            if consume_count < required:
                for card in consumable[:]:
                    if card.name in protected and card_counts[card.name] > 1:
                        # 消耗卡牌
                        idx = game.computer_hand.index(card)
                        removed = game.computer_hand.pop(idx)
                        consume_count += 1
                        print(f"消耗 {removed.name} (剩余手牌: {len(game.computer_hand)})")
                        pygame.time.delay(500)  # 添加延迟，模拟动画效果
                        consumable.remove(card)  # 从可消耗列表中移除
                        if consume_count >= required:
                            break

        # 返回实际消耗的卡牌数量
        print(f"=== 总计消耗 {consume_count} 张牌 ===\n")
        actual_queue=protected
        actual_queue.append(consume_count)
        return actual_queue
# ----------------------------
# PVE 游戏主类
# ----------------------------
class PVEGame:
    def __init__(self):
        #让玩家选择难度
        self.easy=False
        self.middle=False
        self.hard=False
        self.hardest=False

        self.show_initial_overlay = True  # 控制是否显示初始覆盖层
        self.initial_overlay_start_time = pygame.time.get_ticks()  # 记录开局时间
        self.allow_mouse_events = False  # 控制是否允许捕获鼠标事件

        self.alpha = 0  # 透明度
        self.fade_direction = 1  # 1 为渐变显示，-1 为渐变消失
        self.start_image_displayed = False
        self.current_state = "start_menu"  # 新增状态：start_menu, gaming, ending
        self.start_menu_image = None  # 开局图片
        self.ending_image = None  # 结局图片
        self.ending_start_time = 0  # 结局开始时间

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.NOFRAME  # 无边框
        )
        pygame.display.set_caption("胜利属于丽文！")
        self.clock = pygame.time.Clock()
        self.running = True

        # 在__init__末尾添加图片加载：
        try:
            # 加载开场图片并缩放到屏幕尺寸
            self.start_menu_image = pygame.image.load(resource_path("fire_and_water/opening.png")).convert_alpha()
            self.start_menu_image = pygame.transform.smoothscale(self.start_menu_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"加载开场图片失败: {e}")

        self.preloaded_images = preloaded_images
        self.computer_image = computer_image

        self.player = Role("Player")
        self.computer = Role("Computer")

        self.player_hand = []
        self.computer_hand = []
        self.max_hand_size = MAX_HAND_SIZE

        # 计算中等难度按钮的顶部坐标
        middle_button_top = SCREEN_HEIGHT // 2 - 128 // 2

        # 定义三个按钮的位置
        self.difficulty_buttons = [
            {
                "rect": pygame.Rect(
                    SCREEN_WIDTH - 275 - 50,  # 右侧留 50px
                    middle_button_top - 128 - 150,  # 简单难度按钮顶部坐标
                    275, 128
                ),
                "image": "111.png",
                "difficulty": "easy",
                "visible": False  # 新增可见性标志


            },
            {
                "rect": pygame.Rect(
                    SCREEN_WIDTH - 275 - 50,
                    middle_button_top,  # 中等难度按钮顶部坐标
                    275, 128
                ),
                "image": "222.png",
                "difficulty": "middle",
                "visible": False  # 新增可见性标志
            },
            {
                "rect": pygame.Rect(
                    SCREEN_WIDTH - 275 - 50,
                    middle_button_top + 128 + 150,  # 困难难度按钮顶部坐标
                    275, 128
                ),
                "image": "333.png",
                "difficulty": "hard",
                "visible": False  # 新增可见性标志
            },
            {
                "rect": pygame.Rect(  # 中心位置
                    SCREEN_WIDTH // 2 - 138+520,  # 275*1.2/2=138
                    SCREEN_HEIGHT // 2 - 64+290,  # 128*1.2/2=64
                    50, 23.25
                ),
                "image": "444.png",
                "difficulty": "hardest",
                "visible": False  # 新增可见性标志
            }
        ]
        self.easy_hovered = False
        self.middle_hovered = False
        self.hard_hovered = False
        self.hardest_hovered = False

        # 加载按钮图片
        self.button_images = {}
        try:
            for btn in self.difficulty_buttons:
                img_path = resource_path(f"./fire_and_water/{btn['image']}")
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    self.button_images[btn['difficulty']] = pygame.transform.smoothscale(img, (275, 128))
                    print(f"成功加载按钮图片: {btn['image']}")
                except Exception as e:
                    print(f"加载按钮图片 {btn['image']} 失败: {e}")
                    # 使用灰色占位图
                    self.button_images[btn['difficulty']] = pygame.Surface((275, 128), pygame.SRCALPHA)
                    self.button_images[btn['difficulty']].fill((100, 100, 100, 128))
        except Exception as e:
            print(f"初始化按钮图片失败: {e}")



        self.initial_deal_phase = True
        self.initial_deal_count = 0
        self.last_initial_deal_time = pygame.time.get_ticks()

        self.animating_card = None
        self.pending_extra_moves_for_player = 0
        self.pending_extra_moves_for_computer = 0

        self.button_alpha = 128  # 半透明值（0-255）

        self.player_moves = 1
        self.computer_moves = 1

        self.turn_count=1
        self.turn = "player"  # 初始轮到玩家
        self.new_turn = False
        self.have_played=False#检验玩家是否出牌

        self.ending_phase = 0  # 0-结算图片 1-制作名单
        self.ending_images = [None, None]  # [结算图片, 制作名单]
        self.ending_click_count = 0


        self.played=[]#储存已出过的牌

        self.current_turn = "player"#回合判定

        self.result_image_path = None#结局的对应图片
        self.negative=False#消极判断#_______________________________________---

        self.deal_queue = []#出牌队列


        self.consumption_mode = False
        self.consumption_count = 0

        self.front_computer_queue=set()

        self.swap_mode = False
        self.swap_selection = []

        self.computer_play_queue=computer_choose_card(
            self.computer_hand.copy(), self.computer, self.player, self
        )

        self.skip_button_rect = pygame.Rect(50, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.consume_button_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_WIDTH - 50, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.swap_button_rect = SWAP_BUTTON_RECT

        self.font = pygame.font.SysFont("arial", 50)
        self.message = ""
        self.message2= ""

        self.played_card = None
        self.played_card_time = 0

        # 新增大号字体（在初始化部分添加）
        self.effect_font = pygame.font.Font(resource_path("./fire_and_water/SimHei.ttf"), 40)  # 40号字体
        # 分离伤害和治愈提示变量
        self.damage_indicator = None
        self.damage_color = (255, 0, 0)
        self.heal_indicator = None
        self.heal_color = (0, 255, 0)
        self.effect_start_time = 0
        # 统一将效果提示及额外文字显示在提示量下方
        self.effect_extra_text = ""
        #非ultra难度时的电脑方多次数不足出手时的补偿提示
        self.add4message = False
        self.add8message = False



        self.heal_indicator_color = None
        self.heal_indicator_time = 0

        self.popup_image = None
        self.popup_color=(0,255,0)

        self.front_computer_queue_name=set()


        self.computer_delay = COMPUTER_DELAY
        self.computer_action_time = 0

        self.is_dealing_animation = False  # 发牌动画标志
        self.not_enough_image = None  # 资源不足提示图
        self.computer_go = None  # 速度免疫提示
        self.player_go = None  # 同上
        self.negative_image = None  # 惩罚提示图
        self.hover_start_time = 0  # 记录悬停开始时间

        # 预加载提示图片
        try:
            self.not_enough_image = pygame.image.load(resource_path("./fire_and_water/not_enough.png")).convert_alpha()
            self.negative_image = pygame.image.load(resource_path("./fire_and_water/punishment.png")).convert_alpha()
            self.computer_go = pygame.image.load(resource_path("fire_and_water/speed_up_computer.png")).convert_alpha()
            self.player_go = pygame.image.load(resource_path("fire_and_water/speed_up_player.png")).convert_alpha()
            # 等比缩放到弹窗尺寸（1185×495）
            self.not_enough_image = pygame.transform.smoothscale(self.not_enough_image, (1185, 495))
            self.negative_image = pygame.transform.smoothscale(self.negative_image, (1185, 495))
            self.computer_go = pygame.transform.smoothscale(self.computer_go, (1185, 495))
            self.player_go = pygame.transform.smoothscale(self.player_go, (1185, 495))
            print("============Computer Go Image loaded:", bool(self.computer_go))  # 应为True
            print("===============Player Go Image loaded:", bool(self.player_go))
        except Exception as e:
            print(f"加载提示图片失败: {e}")

#fail_end
        try:
            # 加载中文字体文件
            self.chinese_font = pygame.font.Font(resource_path("./fire_and_water/SimHei.ttf"), 20)  # 20 是字体大小
        except Exception as e:
            print(f"加载中文字体失败: {e}")
            # 如果加载失败，使用默认字体（可能无法显示中文）
            self.chinese_font = pygame.font.SysFont("arial", 50)

        # 对局提示按钮
        self.help_button_rect = pygame.Rect(20, SCREEN_HEIGHT - 100, 150, 80)  # 左下角位置
        self.is_help_hovered = False # 鼠标是否悬停在按钮上
        self.last_hovered_index = None #在类中新增一个变量，用于记录上一次悬停的卡牌索引
        self.help_image = None  # 提示图片
        self.help_image_rect = None  # 提示图片的显示区域

        # 加载提示图片
        try:
            self.help_image = pygame.image.load(resource_path("./fire_and_water/point_out.png")).convert_alpha()
            # 缩放到覆盖全屏（可选，或按需调整）
            self.help_image = pygame.transform.scale(self.help_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.help_image_rect = self.help_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        except Exception as e:
            print(f"加载提示图片失败: {e}")

        try:
            self.ending_images[1] = pygame.image.load(resource_path("./fire_and_water/endimg.png")).convert_alpha()
            self.ending_images[1] = pygame.transform.smoothscale(self.ending_images[1], (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"加载制作名单图片失败: {e}")

        self.temp_hand_count = 0  # 临时记录玩家手牌数
        self.popup_message = None
        self.popup_start_time = 0
        self.popup_duration = 1000  # 弹窗显示时间，单位为毫秒

        self.message3=""

        self.messageflag=False

        self.is_dealing_animation = False #发牌动画结束标志

        self.flagok1=0#检查当前玩家的牌堆是否为空
        self.effect_texts = []  # 存储当前所有正在显示的提示语
        self.font = self.chinese_font  # 使用中文字体
        self.effect_display_duration = 2000  # 提示语显示持续时间（毫秒）

        self.waiting_for_computer_animation=False   #检测动画与回合的关系
        self.waiting_for_player_animation=False

        self.computer_play_queue = []  # 存储所有要出的牌
        self.current_play_index = 0  # 当前出牌索引
        self.animating_card = None  # 当前动画卡牌信息

        self.damage=0
        self.heal=0
        self.skip_hovered = False
        self.consume_hovered = False
        self.swap_hovered = False

        self.button_hover_states = {
            "easy": False,
            "middle": False,
            "hard": False,
            "hardest": False,
            "exit": False
        }
        # 退出按钮
        self.exit_button_rect = pygame.Rect(
            SCREEN_WIDTH - 150-10 ,  # 右侧留20px边距
            SCREEN_HEIGHT - 83,  # 底部留20px边距
            150, 83
        )
        self.exit_hovered = False
        try:
            exit_img = pygame.image.load(resource_path("./fire_and_water/exit.png")).convert_alpha()
            self.button_images["exit"] = pygame.transform.smoothscale(exit_img, (140, 63))
        except Exception as e:
            print(f"加载退出按钮图片失败: {e}")
            self.button_images["exit"] = pygame.Surface((140, 63), pygame.SRCALPHA)
            self.button_images["exit"].fill((100, 100, 100, 128))

# self.exit_button_rect.centery - scaled_h//2
        # 为每个按钮添加独立的悬停状态变量
        self.easy_hovered = False
        self.middle_hovered = False
        self.hard_hovered = False
        self.hardest_hovered = False
        self.exit_hovered = False

        # 记录上次播放音效的时间（用于防抖）
        self.last_hover_sound_time = 0

        # 初始化音频系统
        self.game_start_time = pygame.time.get_ticks()  # 新增游戏开始时间记录
        pygame.mixer.init()
        self.background_volume = 0.3  # 背景音乐音量
        self.effect_volume = 0.15  # 音效音量统一设为 50%
        self.sfx_channels = {}  # 存储音效通道




        # 加载背景音乐
        self.open_music_path = resource_path("./fire_and_water/open2.mp3")
        self.fighting_music_path = resource_path("./fire_and_water/fighting2.mp3")
        # 在音频初始化部分添加
        try:
            self.sfx_button_hover = pygame.mixer.Sound(resource_path("./fire_and_water/bottom.mp3"))
            self.sfx_button_hover.set_volume(self.effect_volume)
            self.hover_channel = pygame.mixer.Channel(5)  # 使用单独的音频通道
        except Exception as e:
            print(f"加载按钮悬停音效失败: {e}")
            self.sfx_button_hover = None

        # 加载音效（胜利/失败）
        try:
            self.victory_sound = pygame.mixer.Sound(resource_path("./fire_and_water/victory.mp3"))
            self.failure_sound = pygame.mixer.Sound(resource_path("./fire_and_water/failure3.mp3"))
            self.victory_sound.set_volume(self.effect_volume)
            self.failure_sound.set_volume(self.effect_volume)
        except Exception as e:
            print(f"加载音效失败: {e}")

        # 初始化音效
        pygame.mixer.init()
        self.last_hover_sound_time = 0  # 记录上次播放悬停音效的时间
        self.background_volume = 0.3
        self.effect_volume = 0.5

        # 加载音效文件
        try:
            self.sfx_deal = pygame.mixer.Sound(resource_path("./fire_and_water/put_out.wav"))
            self.sfx_play_card = pygame.mixer.Sound(resource_path("./fire_and_water/put_out.wav"))
            self.sfx_click = pygame.mixer.Sound(resource_path("./fire_and_water/button.wav"))
            self.sfx_beginvoice=pygame.mixer.Sound(resource_path("./fire_and_water/beginvoice.wav"))

            # 设置音量
            self.sfx_deal.set_volume(self.effect_volume)
            self.sfx_play_card.set_volume(self.effect_volume)
            self.sfx_click.set_volume(self.effect_volume)
            self.sfx_beginvoice.set_volume(self.effect_volume)

            # 分配音效通道
            self.deal_channel = pygame.mixer.Channel(1)
            self.play_channel = pygame.mixer.Channel(2)
            self.click_channel = pygame.mixer.Channel(3)
            self.beginvoice=pygame.mixer.Channel(6)
        except Exception as e:
            print(f"音效加载失败: {e}")
        self.last_hovered_index = None  # 新增：确保属性存在
            # 加载悬停音效
        try:
            self.sfx_hover = pygame.mixer.Sound(resource_path("./fire_and_water/choose.mp3"))
            self.sfx_hover.set_volume(self.effect_volume)  # 与其他音效音量一致
            self.hover_channel = pygame.mixer.Channel(4)  # 独立通道防止冲突
        except Exception as e:
            print(f"悬停音效加载失败: {e}")

        # 记录上一次悬停的卡牌索引
        self.last_hovered_index = None
        self.skip=False
        self.hovered_card_index = -1  # 当前悬停卡牌的索引
        self.hovered_card_rect = None  # 悬停卡牌的缩放后矩形区域

        # 初始音乐状态
        self.is_playing_open_music = False
        self.is_playing_fighting_music = False

        # 游戏结束标志与结算信息
        self.game_over = False
        self.result_text = ""
        self.result_color = (255, 255, 255)

    def play_button_hover_sound(self):#辅助音效播放函数
        if not self.hover_channel.get_busy():
            self.hover_channel.play(self.sfx_button_hover)

    def reset_game_state(self):
        """完全重置游戏状态"""
        self.__init__()
        pygame.mixer.music.stop()
        self.current_state = "start_menu"
        print("游戏状态已重置")


    def computer_consume_cards(self):
        return computer_consume_cards(self,self.computer_play_queue,len(self.computer_play_queue))

    def play_button_click_sound(self):
        """播放按钮点击音效"""
        current_time = pygame.time.get_ticks()
        # 添加500ms的冷却时间防止快速连续点击
        if self.sfx_button_hover and not self.hover_channel.get_busy():
            self.hover_channel.play(self.sfx_button_hover)
            self.last_hover_sound_time = current_time

    def play_sfx(self, channel, sound):
        """防止音效重叠"""
        if not channel.get_busy():
            channel.play(sound)

    def play_hover_sfx(self):
        """播放悬停音效（非重复触发）"""
        if not self.hover_channel.get_busy():
            self.hover_channel.play(self.sfx_hover)

    def set_effect_volume(self, volume):
        """动态调整所有音效音量（0.0 ~ 1.0）"""
        self.effect_volume = volume
        for sfx in [self.victory_sound, self.failure_sound,
                    self.sfx_deal, self.sfx_play_card, self.sfx_click]:
            sfx.set_volume(volume)

    def show_popup(self, message, color):

        self.popup_message = message
        self.popup_start_time = pygame.time.get_ticks()
        self.popup_color = color
        #self.popup_image = None  # 每次显示弹窗时重置====================================================================

        # 匹配消息与图片
        if message == "NOT ENOUGH!":
            self.popup_image = self.not_enough_image
        elif message == "Negative Punishment!":
            self.popup_image = self.negative_image
        elif message == "1":
            self.popup_image = self.computer_go
            print("fuck!!!!!!!!!!!!!!!!111")
        elif message == "2":
            self.popup_image = self.player_go
            print("what the fuck!!!!!!!!!!!!!!!!!!!!!!11")


    def handle_swap_mode(self):
        if len(self.player_hand) < 2:
            self.show_popup("NOT ENOUGH!", (255, 255, 0))  # 黄色
            self.message = "嘿伙计，只有一张牌也敢点交换吗？"
            self.swap_mode = False
            return
        self.swap_mode = True
        self.swap_selection = []
        self.message = "选择两张牌进行位置交换吧"
        print("Entered swap mode")

    def show_card_effect_image(self, image_path, position=(1250,250)):
        """显示卡牌效果图片"""
        if self.turn=="player":
            try:
                image = pygame.image.load(image_path)
                image = pygame.transform.scale(image, (500, 250))
                self.screen.blit(image, position)
                pygame.display.update()
                start_time = pygame.time.get_ticks()
                while pygame.time.get_ticks() - start_time < 700:#500
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
            except Exception as e:
                print(f"图片加载失败：{e}")

    def show_card_effect_text(self, text, color=(255, 255, 255)):
        """显示卡牌特效文字，使用中文字体"""
        # 更新特效文本
        self.effect_extra_text = text
        self.effect_indicator_color = color
        self.effect_indicator_time = pygame.time.get_ticks()

        # 使用中文字体渲染
        effect_font = self.chinese_font
        text_surface = effect_font.render(text, True, color)

        # 清理之前的文本，并重新渲染
        self.screen.fill((0, 0, 0, 0))  # 清空屏幕区域
#message2
        # 确保文本显示在指定位置
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)

    def image_load(self, image_path, position):
        try:
            image = pygame.image.load(image_path).convert_alpha()
            self.screen.blit(image, position)
            pygame.display.flip()  # 立即更新显示
        except Exception as e:
            print(f"Failed to load effect image: {e}")

    def start_next_deal_animation(self):
        if self.deal_queue and self.animating_card is None:
            side = self.deal_queue.pop(0)
            self.start_animating_card(side)

    def handle_consume_mode(self):
        if not self.consumption_mode:
            # 进入消耗模式时，记录当前手牌数
            self.temp_hand_count = len(self.player_hand)
            self.consumption_mode = True
            self.consumption_count = 0
            self.message = "进入消耗状态，请选择你要消耗的牌，注意，点击到什么牌就会删除什么牌。"
            print("Entered consume mode")
        else:
            # 提交消耗时，检查消耗的手牌数是否等于临时记录的手牌数
            if self.consumption_count == self.temp_hand_count:
                self.player_moves = 1  # 强制将出手数变为1
                #self.start_animating_card("player")  # 使用正常发牌动画
                self.show_popup("Negative Punishment!", (255, 0, 0))  # 红色
                self.negative=True
                self.message = "你貌似很调皮嘛，很有自己的想法，但是请你好好对局哦"

                self.end_player_turn()

            elif self.consumption_count==0:
                self.message=f"不打算消耗牌你还点请求按钮，阁下莫不是在逗洒家玩？"
            else:
                self.player_moves += self.consumption_count
                self.message = f"你已经支付了{self.consumption_count}张牌了, 按照契约，你有{self.consumption_count}次额外出手数，现在你有 {self.player_moves}次出手次数。"
            self.consumption_mode = False
            self.consumption_count = 0
            print(f"Submitted consume mode: extra moves = {self.consumption_count}")

    def handle_events(self):
        for event in pygame.event.get():
            #print(f"捕获到事件: {event}")  # 打印所有事件
            if event.type == pygame.QUIT:
                self.running = False
                print("检测到退出事件")
            elif event.type == pygame.KEYDOWN:
                print(f"检测到按键事件，键值: {event.key}, 当前状态: {self.current_state}")
                if event.key == pygame.K_q and self.current_state == "ending":
                    print("当前理应退出")
                    self.running = False
            elif event.type == pygame.MOUSEMOTION:
                current_time = pygame.time.get_ticks()
                if self.current_state != "gaming":
                    # print("代码抵达此处===")
                    continue  # 前9秒忽略按钮悬浮

                mouse_pos = pygame.mouse.get_pos()
                self.exit_hovered = self.exit_button_rect.collidepoint(mouse_pos)
                # 在MOUSEMOTION事件处理中补充音效
                if self.exit_hovered and not self.hover_channel.get_busy():
                    self.hover_channel.play(self.sfx_button_hover)
                if self.current_state == 'strat_menu':
                    # 处理难度按钮悬停
                    for btn in self.difficulty_buttons:
                        # 获取当前悬停状态
                        current_hover = btn["rect"].collidepoint(mouse_pos)
                        # 获取之前的悬停状态
                        prev_hover = getattr(self, f"{btn['difficulty']}_hovered", False)

                        # 如果状态变化
                        if current_hover != prev_hover:
                            # 更新状态
                            setattr(self, f"{btn['difficulty']}_hovered", current_hover)

                            # 如果是新悬停且需要播放音效
                            if current_hover:
                                if btn['difficulty'] == "hardest":
                                    if not self.hover_channel.get_busy():
                                        self.hover_channel.play(self.sfx_beginvoice)
                                else:
                                    if not self.hover_channel.get_busy():
                                        self.hover_channel.play(self.sfx_button_hover)

            # 添加时间判断：游戏开始9秒后才允许点击按钮

                # 检测鼠标是否悬停在帮助按钮上

                self.is_help_hovered = self.help_button_rect.collidepoint(mouse_pos)
                # 保存之前的悬停状态用于比较
                prev_states = {
                    "skip": self.skip_hovered,
                    "consume": self.consume_hovered,
                    "swap": self.swap_hovered
                }

                # 检测当前悬停状态
                self.skip_hovered = self.skip_button_rect.collidepoint(mouse_pos)
                self.consume_hovered = self.consume_button_rect.collidepoint(mouse_pos)
                self.swap_hovered = self.swap_button_rect.collidepoint(mouse_pos)


                # 如果悬停状态改变，重置时间
                for btn_type in ["skip", "consume", "swap"]:
                    if current_time - self.game_start_time < 10000 and self.current_state == "gaming":
                        #print("代码抵达此处===")
                        break  # 前9秒忽略按钮悬浮
                    current_state = getattr(self, f"{btn_type}_hovered")
                    if current_state != prev_states[btn_type]:
                        if current_state:  # 只有从非悬停变为悬停时才播放音效
                            if self.sfx_button_hover and not self.hover_channel.get_busy():
                                self.hover_channel.play(self.sfx_button_hover)

                        setattr(self, f"{btn_type}_hover_start", pygame.time.get_ticks())



            elif event.type == pygame.MOUSEBUTTONDOWN:
                current_time = pygame.time.get_ticks()
                mouse_pos = pygame.mouse.get_pos()
                self.play_sfx(self.click_channel, self.sfx_click)
                # 检查是否点击了按钮
                if self.skip_button_rect.collidepoint(mouse_pos):
                    self.play_button_click_sound()
                elif self.consume_button_rect.collidepoint(mouse_pos):
                    self.play_button_click_sound()
                elif self.swap_button_rect.collidepoint(mouse_pos):
                    self.play_button_click_sound()


                    # 在结局状态点击切换图片
                    self.ending_phase = 1 - self.ending_phase
                    self.ending_click_count += 1
                    # 奇数次点击显示制作名单，偶数次显示结算图片
                    if self.ending_click_count % 2 == 1:
                        self.show_ending_image = True
                    else:
                        self.show_ending_image = False

                # 结局画面点击处理
                if self.current_state == "ending":
                    # 在结局状态点击切换图片
                    self.ending_phase = 1 - self.ending_phase
                    self.ending_click_count += 1
                    # 奇数次点击显示制作名单，偶数次显示结算图片
                    if self.ending_click_count % 2 == 1:
                        self.show_ending_image = True
                    else:
                        self.show_ending_image = False
                    if self.ending_click_count>=10:
                        self.running=False
                    #self.running = False  # 点击任意位置退出

                # 开始菜单点击处理
                elif self.current_state == "start_menu":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for btn in self.difficulty_buttons:
                            if btn["rect"].collidepoint(event.pos):
                                # 设置难度
                                self.easy = (btn['difficulty'] == 'easy')
                                self.middle = (btn['difficulty'] == 'middle')
                                self.hard = (btn['difficulty'] == 'hard')
                                self.hardest=(btn['difficulty']=='hardest')
                                if self.easy:
                                    self.player.hp = 35
                                    self.computer.hp = 35
                                    self.player.speed=20
                                    print("游戏进入电脑无脑出牌模式，牢底你还是怕了吗")
                                elif self.middle:
                                    print("游戏进入电脑决策有限出牌模式，小老弟你用这个试水还行吗")
                                    self.player.hp = 60
                                    self.computer.hp = 60
                                elif self.hard:
                                    self.player.hp = 100
                                    self.computer.speed=20
                                    self.computer.hp = 120
                                    self.computer.FD=True
                                    self.computer.WD=True

                                    print("牢底你随便选的话你的实力允许吗")
                                elif self.hardest:
                                    self.player.hp=22
                                    self.computer.hp=225
                                    self.computer.speed=30
                                    self.computer.FD=True
                                    self.computer.WD=True
                                    self.player.DEAD=True
                                    self.computer.FK=True
                                    self.computer.WK=True
                                    print("享受杀戮吧")

                                # 切换到游戏状态
                                self.current_state = "gaming"
                                pygame.mixer.music.stop()
                                pygame.mixer.music.load(self.fighting_music_path)
                                pygame.mixer.music.set_volume(self.background_volume)
                                pygame.mixer.music.play(-1)
                                self.is_playing_open_music = False
                                self.is_playing_fighting_music = True

                elif self.current_state == "gaming":  # 游戏进行状态

                    if self.game_over:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            self.running = False
                        continue
                        # 禁止在开局7秒内或发牌动画期间捕获鼠标事件
                    if not self.allow_mouse_events or self.animating_card is not None:
                        continue  # 忽略所有鼠标事件
                    # 禁止在发牌动画阶段出牌
                    if self.animating_card is not None:
                        continue  # 忽略所有事件，直到动画结束
                    if self.exit_button_rect.collidepoint(mouse_pos):
                        self.play_button_click_sound()
                        # 重置游戏状态
                        self.__init__()  # 重新初始化游戏
                        pygame.mixer.music.stop()
                        self.current_state = "start_menu"
                        return

                    if self.swap_mode:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pos = event.pos
                            idx = self.get_hand_index(pos, side="player")
                            if idx is not None and idx not in self.swap_selection:
                                self.swap_selection.append(idx)
                                self.message = f"这才选了{len(self.swap_selection)} 张卡，另外一张会是什么呢？"
                                print(f"Selected card index {idx} for swapping")
                                if len(self.swap_selection) == 2:
                                    i1, i2 = self.swap_selection
                                    self.player_hand[i1], self.player_hand[i2] = self.player_hand[i2], self.player_hand[
                                        i1]
                                    self.swap_mode = False
                                    self.swap_selection = []
                                    self.message = "叮咚！成功交换！"
                        continue

                    if self.consumption_mode:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pos = event.pos
                            if self.consume_button_rect.collidepoint(pos):
                                self.handle_consume_mode()
                            else:
                                idx = self.get_hand_index(pos, side="player")
                                if idx is not None:
                                    removed = self.player_hand.pop(idx)
                                    self.consumption_count += 1
                                    self.message = f"进入消耗状态，当前消耗了 {self.consumption_count} 张卡，需要再次点击消耗键提交请求并退出消耗状态。"
                                    print(f"Consumed card: {removed.name}")
                        continue

                    if self.turn == "player" and event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        if self.swap_button_rect.collidepoint(pos):
                            self.handle_swap_mode()
                            continue
                        if self.consume_button_rect.collidepoint(pos):
                            self.handle_consume_mode()
                            continue
                        if self.skip_button_rect.collidepoint(pos):
                            self.skip = True
                            print("Player chooses to skip turn")
                            self.end_player_turn()
                            continue
                        indices = []
                        total_width = len(self.player_hand) * CARD_SPACING
                        start_x = (
                                          SCREEN_WIDTH - total_width) // 2 if self.player_hand else SCREEN_WIDTH // 2 - HAND_CARD_WIDTH // 2
                        for i, card in enumerate(self.player_hand):
                            slot = (start_x + i * CARD_SPACING, SCREEN_HEIGHT - HAND_CARD_HEIGHT - 20)
                            rect = pygame.Rect(slot, (HAND_CARD_WIDTH, HAND_CARD_HEIGHT))
                            if rect.collidepoint(pos):
                                indices.append((i, slot))
                        # 玩家出牌逻辑
                        if indices:
                            idx, chosen_slot = max(indices, key=lambda x: x[1][0])
                            if idx < len(self.player_hand):  # 检查手牌是否为空
                                card = self.player_hand[idx]
                                if card:
                                    print(f"Player plays {card.name}")
                                    self.played_card = card
                                    self.played_card_time = pygame.time.get_ticks()
                                    process_card_effect(card, self.player, self.computer,
                                                        game=self)  # 卡牌移除逻辑在 process_card_effect 中处理

                                # 更新 message2 基于卡牌和玩家状态
                                if card.name == "fireK":
                                    if self.player.FD:  # 检查玩家是否有火盾
                                        if self.player.FK:  # 检查玩家是否有火刃
                                            if self.player.fire_attach:  # 火附着
                                                if self.computer.water_attach:  # 电脑有水附着
                                                    self.message2 = "这是……东方燧人留下的祈愿！"
                                                else:
                                                    self.message2 = "汇聚了火的全部力量……这是击碎星辰的一斩！"
                                            else:
                                                self.message2 = "以火盾的庇护挥动带着火刃的刀把么，哈基米你这家伙……"
                                        else:
                                            self.message2 = "你是怎么发现在火盾的庇护下使用火的力量能够事半功倍的？"
                                    elif self.player.FK:
                                        if self.computer.water_attach:
                                            if self.player.fire_attach:
                                                self.message2 = "体内流淌着的火延续在了刀刃上，好可怕……"
                                            else:
                                                self.message2 = "你刚好以火淬剑，对面身上还有水，他不炸了吗？"
                                        else:
                                            self.message2 = "我似乎听闻过：以火为剑，可断众生"
                                    elif self.player.fire_attach:
                                        if self.computer.water_attach:
                                            self.message2 = "你身上有火，他身上有水，但是呢，你出的是火杀"
                                        else:
                                            self.message2 = "身上着火了为什么用火刀人还能更痛啊喂！"
                                    elif self.computer.water_attach:
                                        self.message2 = "hiahia！对面身上有水，出火杀刚好弄他一炮！"
                                    else:
                                        self.message2 = "能够运用火的力量么……真是有趣"

                                elif card.name == "waterK":
                                    if self.player.WD:  # 水盾
                                        if self.player.WK:  # 水刃
                                            if self.player.water_attach:  # 水附着
                                                if self.computer.fire_attach:  # 电脑有火附着
                                                    self.message2 = "这是……善利万物而不争的力量！"
                                                else:
                                                    self.message2 = "汇聚了水的全部力量……这是贯穿星河的一击！"
                                            else:
                                                self.message2 = "于水盾之下的水刃闪耀着美如月色的波纹，哈基丽文太会了……"
                                        else:
                                            self.message2 = "被你试出来了！于水盾下的水杀，回甘着醇香~"
                                    elif self.player.WK:
                                        if self.computer.fire_attach:
                                            if self.player.water_attach:
                                                self.message2 = "在你刀刃上停留的水痕，是水的呼唤，还是你的眼泪呢？"
                                            else:
                                                self.message2 = "对方尝试以火之身抵抗水之剑……可笑~"
                                        else:
                                            self.message2 = "我似乎听闻过：以水为剑，可濯众尘"
                                    elif self.player.water_attach:
                                        if self.computer.fire_attach:
                                            self.message2 = "怀着水源的梦，满身火的人正是好方法~"
                                        else:
                                            self.message2 = "他真的要用火来面对流水的剑吗"
                                    elif self.computer.fire_attach:
                                        self.message2 = "这是，似柔情的水浇灭的火哦"
                                    else:
                                        self.message2 = "善于引导水为你所用吗，你真是令人惊喜"

                                # 其它卡牌的处理
                                elif card.name == "fireD":
                                    self.message2 = "升起了火盾呢，至少这回合不怕对面的火了"
                                elif card.name == "waterD":
                                    self.message2 = "歆羡水的庇佑吗？那是万物依恋的母亲的感触"
                                elif card.name == "fire":
                                    self.message2 = "化火为生，可以得长久"
                                elif card.name == "water":
                                    self.message2 = "以水固本，可以得永生"
                                elif card.name == "FK":
                                    self.message2 = "烈焰会聆听你剑刃的低语"
                                elif card.name == "WK":
                                    self.message2 = "塑水为剑形，一态斩百态！~"
                                elif card.name == "timer":
                                    self.message2 = "当熵增停下脚步，生命是否就能够与时间对视呢？"
                                elif card.name == "fast":
                                    self.message2 = "不动如山，动如……"
                                elif card.name == "wind":
                                    self.message2 = "哇！有什么风在我面前刮过了！……"
                                elif card.name == "get_time":
                                    self.message2 = "纵使白驹过隙，你还会是你么……"
                                elif card.name == "GETTIME":
                                    self.message2 = "嘘——别说话，此刻永恒……"
                                elif card.name == "regive":
                                    self.message2 = "你能不能自己大方一点……"
                                elif card.name == "REGIVE":
                                    self.message2 = "对面知道他自己这么大方吗……"
                                elif card.name == "burn":
                                    self.message2 = "燃烧了自己，这双手就是烈焰的刃么"
                                elif card.name == "flood":
                                    self.message2 = "沉没在一片虚幻的海里，你是唯一的光亮……"
                                elif card.name == "ORDER":
                                    self.message2 = "当熵增停止的时候，时间还会有意义吗……"

                                if card.name == "back_go":
                                    if self.turn == "player":
                                        self.pending_extra_moves_for_player = 1
                                        self.message2 = f"厚积而薄发，不在朝暮间……？还是君子报仇，十年……"
                                        print("back_go: pending extra moves for Player set to 1")
                                        if get_hand_index_from_card(self.player_hand, card) is not None:
                                            del self.player_hand[get_hand_index_from_card(self.player_hand, card)]
                                        self.end_player_turn()
                                    else:
                                        self.pending_extra_moves_for_computer = 1
                                        self.message2 = f"居然也能够以退为进吗？"
                                        if get_hand_index_from_card(self.computer_hand, card) is not None:
                                            del self.computer_hand[get_hand_index_from_card(self.computer, card)]
                                        self.end_computer_turn()



                                elif card.name == "order":
                                    if self.turn == "player":
                                        self.player_moves -= 1

                                        self.message2 = f"秩序的罅隙间，也会有生命的存在吗？…"
                                        if self.player_moves <= 0:
                                            self.end_player_turn()
                                    elif self.turn == "computer":
                                        self.computer_moves -= 1

                                        if self.computer_moves <= 0:
                                            self.end_computer_turn()
                                else:
                                    # del self.player_hand[idx]
                                    self.player_moves -= 1
                                    self.message = (f""
                                                    )
                                    if self.player_moves <= 0:
                                        self.end_player_turn()
                            self.effect_texts.append({
                                "text": self.message,
                                "color": (255, 255, 0),  # 黄色字体
                                "start_time": pygame.time.get_ticks()  # 当前时间
                            })
                            self.effect_texts.append({
                                "text": self.message2,
                                "color": (255, 255, 255),  # 白色字体
                                "start_time": pygame.time.get_ticks()  # 当前时间
                            })
            elif self.current_state == "ending":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.ending_image:
                        # 检查是否点击了“查看结局”按钮
                        btn_rect = pygame.Rect(
                            (SCREEN_WIDTH - 200) // 2,
                            (SCREEN_HEIGHT - 80) // 2,
                            200, 80
                        )
                        if btn_rect.collidepoint(event.pos):
                            self.show_ending_image = True
                    else:
                        # 点击任意位置退出
                        self.running = False

    def get_hand_index(self, pos, side="player"):
        if side == "player":
            hand = self.player_hand
            y = SCREEN_HEIGHT - HAND_CARD_HEIGHT - 20
        else:
            hand = self.computer_hand
            y = 20
        if not hand:
            return None
        total_width = len(hand) * CARD_SPACING
        start_x = (SCREEN_WIDTH - total_width) // 2 if hand else SCREEN_WIDTH // 2 - HAND_CARD_WIDTH // 2
        for i in range(len(hand)):
            rect = pygame.Rect(start_x + i * CARD_SPACING, y, HAND_CARD_WIDTH, HAND_CARD_HEIGHT)
            if rect.collidepoint(pos):
                return i
        return None

    def adjust_hand(self, hand, side):
        while len(hand) > self.max_hand_size-5:
            removed = hand.pop(0)
            print(f"{side} hand exceeds {self.max_hand_size}, removing {removed.name}")

    def start_animating_card(self, side):
        self.play_sfx(self.deal_channel, self.sfx_deal)
        new_card = deal_card(side)

        # 设置动画参数
        duration = 1250
        if side == "computer":
            target_x = (SCREEN_WIDTH - HAND_CARD_WIDTH) // 2
            target_y = 20
        else:
            target_x = (SCREEN_WIDTH - HAND_CARD_WIDTH) // 2
            target_y = SCREEN_HEIGHT - HAND_CARD_HEIGHT - 20

        start_pos = (SCREEN_WIDTH, target_y)

        self.animating_card = {
            "card": new_card,
            "side": side,
            "start_pos": start_pos,
            "end_pos": (target_x, target_y),
            "start_time": pygame.time.get_ticks(),
            "duration": duration
        }

    def update_animating_card(self):
        current_time = pygame.time.get_ticks()
        anim = self.animating_card
        if anim is None:
            return
        elapsed = current_time - anim["start_time"]+300
        progress = min(elapsed / anim["duration"], 1)
        sx, sy = anim["start_pos"]
        ex, ey = anim["end_pos"]
        current_x = sx + (ex - sx) * progress
        anim["current_pos"] = (current_x, sy)
        if progress >= 1:
            # 添加卡牌到对应手牌
            if anim["side"] == "computer":
                self.computer_hand.append(anim["card"])
                self.adjust_hand(self.computer_hand, "Computer")
            else:
                self.player_hand.append(anim["card"])
                self.adjust_hand(self.player_hand, "Player")

            # 动画结束后处理队列中的下一张牌
            self.animating_card = None
            self.start_next_deal_animation()  # 新增

    def show_damage_text(self, damage, extra_text):
        self.damage_indicator = f"-{damage}"
        if extra_text == "水！":
            self.damage_color = (173, 216, 230)
        elif extra_text in {"被盾了！", "被逃了！"}:
            self.damage_color = (255, 255, 255)
        elif extra_text == "火!":
            self.damage_color = (255, 0, 0)
        self.effect_start_time = pygame.time.get_ticks()

    def show_heal(self, n):
        print("============================此处函数抵达到========================")
        self.heal_indicator = f"+{n}"
        self.effect_start_time = pygame.time.get_ticks()
        self.effect_extra_text = ""
        self.show_heal_extra("得以治愈！")


    def show_damage_and_heal(self,damage,heal,extra_text):
        self.damage_indicator = f"-{damage}"
        self.heal_indicator = f"+{heal}"
        self.effect_extra_text = ""
        self.show_heal_extra("得以治愈！")
        if extra_text == "水！":
            self.damage_color = (173, 216, 230)
        elif extra_text in {"被盾了！", "被逃了！"}:
            self.damage_color = (255, 255, 255)
        elif extra_text == "火!":
            self.damage_color = (255, 0, 0)
        self.effect_start_time = pygame.time.get_ticks()




    def show_heal_extra(self, text):
        # 使用中文字体渲染文本


        self.heal_indicator_color = (0, 255, 177)
        self.heal_indicator_time = pygame.time.get_ticks()

        # 计算文本位置
        #text_rect = ext_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # 绘制文本到屏幕
        #self.screen.blit(ext_surface, text_rect)

        # 记录时间
        self.heal_indicator_time = pygame.time.get_ticks()

    def check_game_over(self):
        if self.player.hp <= 0 or self.computer.hp <= 0:
            self.game_over = True
            self.current_state = "ending"
            self.ending_phase = 0  # 初始显示结算图片
            self.ending_click_count = 0
            pygame.mixer.music.stop()

            try:
                if self.hardest:
                    if self.player.hp <= 0:
                        self.ending_image = pygame.image.load(
                            resource_path("./fire_and_water/hidefail.png")).convert_alpha()
                        if self.failure_sound:
                            self.failure_sound.play()
                    else:
                        self.ending_image = pygame.image.load(
                            resource_path("./fire_and_water/hidevictory.png")).convert_alpha()
                        if self.victory_sound:
                            self.victory_sound.play()
                    self.ending_image = pygame.transform.smoothscale(self.ending_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                else:
                    if self.player.hp <= 0:
                        self.ending_image = pygame.image.load(
                            resource_path("./fire_and_water/fail_end.png")).convert_alpha()
                        if self.failure_sound:
                            self.failure_sound.play()
                    else:
                        self.ending_image = pygame.image.load(
                            resource_path("./fire_and_water/victory_end.png")).convert_alpha()
                        if self.victory_sound:
                            self.victory_sound.play()
                    self.ending_image = pygame.transform.smoothscale(self.ending_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception as e:
                print(f"加载结局图片失败: {e}")
                self.ending_image = None



    def end_player_turn(self):
        self.current_turn = "computer"  # 直接切换回合状态
        self.turn = "computer"
        self.new_turn = True
        self.consumption_mode = False
        self.consumption_count = 0
        self.swap_mode = False
        self.swap_selection = []
        print("Player turn ended")
        self.message = ""#原：又到对面这个老头思考了

    def end_computer_turn(self):
        self.current_turn = "player"
        self.turn = "player"
        self.new_turn = True
        print("Computer turn ended")
        self.message = "如花落般的牌呵……"

    # 处理单张出牌逻辑
    def play_card2(self, card):
        if card:
            print(f"Computer plays {card.name}")
            self.played_card = card
            self.played_card_time = pygame.time.get_ticks()
            process_card_effect(card, self.computer, self.player, game=self)

            # 添加延迟
            pygame.time.delay(600)

            # 消耗卡牌
            if card in self.computer_hand:
                self.computer_hand.remove(card)
                self.adjust_hand(self.computer_hand, "Computer")

            # 出牌后减少出手次数
            self.computer_moves -= 1

            # 检查是否需要结束回合
            if self.computer_moves <= 0:
                self.end_computer_turn()

    def update(self):

        # 透明度判定
        if self.alpha <= 0 and self.fade_direction == -1:
            self.fade_direction = 1  # 等待渐变进入
        if self.alpha >= 255 and self.fade_direction == 1 and not self.start_image_displayed:
            self.alpha = 255  # 完全透明后停止渐变

        self.alpha += self.fade_direction * 5
        self.alpha = max(0, min(255, self.alpha))  # 限制透明度范围

        # 对局判定
        if self.current_state == "ending":
            pass
        elif self.current_state == "gaming":
            current_time = pygame.time.get_ticks()
            self.player.update_status()  # 更新玩家的濒死状态
            self.computer.update_status()  # 更新电脑的濒死状态

            # 开局覆盖层显示7秒
            if self.show_initial_overlay:
                if current_time - self.initial_overlay_start_time >= 7000:
                    self.show_initial_overlay = False  # 7秒后关闭覆盖层
                    self.allow_mouse_events = True  # 允许捕获鼠标事件
                else:
                    self.allow_mouse_events = False  # 禁止捕获鼠标事件

            # 发牌动画期间禁止鼠标事件
            if self.animating_card is not None:
                self.allow_mouse_events = False
            else:
                self.allow_mouse_events = True

            # 添加检测
            if self.waiting_for_computer_animation and not self.animating_card:
                self.turn = "computer"
                self.new_turn = True
                self.waiting_for_computer_animation = False

            self.is_dealing_animation = self.animating_card is not None
            current_time = pygame.time.get_ticks()
            self.check_game_over()
            if self.game_over:
                return
            #computer_play_sequence
            # 更新发牌动画
            if self.animating_card is not None:
                self.update_animating_card()
                return
                 # 动画未结束，不执行其他逻辑

            # 初始发牌阶段：使用动画发牌
            if self.initial_deal_phase:
                if current_time - self.last_initial_deal_time >= INITIAL_DEAL_DELAY:
                    if self.initial_deal_count % 2 == 0:
                        self.start_animating_card("player")  # 玩家发牌动画
                    else:
                        self.start_animating_card("computer")  # 电脑发牌动画
                    self.initial_deal_count += 1
                    self.last_initial_deal_time = current_time
                    if self.initial_deal_count >= 6:  # 总共发6张牌（3张玩家，3张电脑）
                        self.initial_deal_phase = False
                        self.turn = "player"
                        self.new_turn = True
                        if self.hardest:
                            self.message3="我将给予你【水火的祝福】，每回合额外获取一张牌，加油！"
                        else:
                            self.message3 = "我是牌中的精灵，欢迎再次来到对局，你是先手，加油！"
                if len(self.player_hand)<=5 and self.turn_count<=1:
                    if self.easy:
                        self.message = "当前选择的是老者大放水难度，二者血量为35且你拥有初始的20速度哦"
                    elif self.middle:
                        self.message = "当前选择的是老者稍微放水难度，二者血量为60且双方速度初始相同哦"
                    elif self.hard:
                        self.message = f"老者要认真对局了，他拥有领先你20的初始速度和血量，同时双盾初始存在，千万小心！"
                    elif self.hardest:
                        self.message = f"欢迎来到隐藏对局，你进入了老者的决一死战领域，他拥有225点血量、30的初始速度、初始双盾、常驻双刃，且他出牌不再需要消耗牌来获取多出手次数"
                        self.message3=f"在这个领域里，对方每出手一次就会隐藏增加一点血量，不过你也因此获取了【水火的祝福】，每回合额外获取一张牌，并且很多牌都会有额外增益"

                return

            if self.turn=="player":
                # 电脑自动换牌逻辑（在出牌前执行）
                swap_name = {'get_time', 'GETTIME', 'fast', 'wind', 'timer'}
                hand_copy = self.computer_hand.copy()
                for idx, card in enumerate(hand_copy):
                    if card.name in swap_name:
                        if idx == 0 or idx == len(hand_copy) - 1:
                            for mid_idx in range(1, len(hand_copy) - 1):
                                if hand_copy[mid_idx].name not in swap_name:
                                    self.computer_hand[idx], self.computer_hand[mid_idx] = \
                                        self.computer_hand[mid_idx], self.computer_hand[idx]
                                    break
                if len(self.player_hand)==0 and self.have_played==True:
                    self.end_player_turn()
            # 新回合开始时：为当前回合方发1张新牌，并设置出手次数
            if self.new_turn and self.animating_card is None:
                if self.turn == "player":
                    # 删除原有的直接发牌代码
                    # [原代码] if self.hardest: self.player_hand.append(deal_card())

                    # 改为使用队列处理
                    cards_to_deal = 2 if self.hardest else 1
                    for _ in range(cards_to_deal):
                        self.deal_queue.append("player")

                    self.start_next_deal_animation()  # 开始处理队列

                    self.player.reset_on_my_turn()
                    self.player_moves = 1 + self.pending_extra_moves_for_player
                    self.pending_extra_moves_for_player = 0
                    self.player_moves = 1 + self.pending_extra_moves_for_player
                    self.pending_extra_moves_for_player = 0
                    if self.messageflag==False:
                        oklw = [reverse_card_name_mapping[c] for c in self.front_computer_queue_name]
                        stringlw = ""
                        print(oklw)
                        for i in range(0, len(oklw)):
                            stringlw += oklw[i] + "、"
                        stringlw = stringlw[:-1]  # 有可能因为这个导致顺序颠倒了？
                        # 根据玩家的濒死状态设置提示信息
                        if len(self.player_hand) >= 10:
                            self.message = f"当前有{self.player_moves}次出手机会。你的牌已经到达储存临界，若再不出牌则会删除第一张牌。"
                        elif self.player.DEAD:
                            if stringlw is not None:
                                if self.hard:
                                    self.message=f"你当前有{self.player_moves}次出手机会。上把对方出牌为{stringlw}（瞳孔发光）我是这个游戏的制作者，老弟，没实力还硬来打高难度吗"
                                elif self.hardest:
                                    self.message=f"你当前有{self.player_moves}次出手机会。上把对方出牌为{stringlw}（瞳孔发光）你不该来的，孩子，不过，不去试试怎么知道一定打不过呢"
                                else:
                                    self.message = f"你当前有{self.player_moves}次出手机会。上把对方出牌为{stringlw}（瞳孔发光）我是这个游戏的制作者，老弟，你连简单人机都打不过了吗"
                            else:
                                if self.hard:
                                    self.message=f"你当前有{self.player_moves}次出手机会。上把对方没有出牌（瞳孔发光）我是这个游戏的制作者，老弟，没实力还硬来打高难度吗"
                                elif self.hardest:
                                    self.message=f"你当前有{self.player_moves}次出手机会。上把对方没有出牌（瞳孔发光）你不该来的，孩子，不过，不去试试怎么知道一定打不过呢"
                                else:
                                    self.message = f"你当前有{self.player_moves}次出手机会。上把对方没有出牌（瞳孔发光）我是这个游戏的制作者，老弟，你连简单人机都打不过了吗"
                        elif self.player_moves==1 and self.turn_count==1:
                            #<=5
                            if self.easy:
                                self.message="当前选择的是老者大放水难度，二者血量为35且你拥有初始的20速度哦"
                            elif self.middle:
                                self.message="当前选择的是老者稍微放水难度，二者血量为60且双方速度初始相同哦"
                            elif self.hard:
                                self.message=f"老者要认真对局了，他拥有领先你20的初始速度和血量，同时双盾初始存在，千万小心！"
                            elif self.hardest:
                                self.message=f"欢迎来到隐藏对局，你进入了老者的决一死战领域，他拥有225点血量、30的初始速度、初始双盾、常驻双刃，且他出牌不再需要消耗牌来获取多出手次数"

                        elif  not self.front_computer_queue_name :
                            self.message=f"你有{self.player_moves}次出手机会，上把对方没出牌，好机会！"
                        elif self.add4message:
                            self.message=f"由于当前你选择的是老者放水难度，当对方打出“以退为进”和“乘如白驹”时从加两次出手数变为加4点血量。当前出手数{self.player_moves}"
                            self.add4message = False
                            self.add8message = False
                        elif self.add8message:
                            self.message = f"由于当前你选择的是老者放水难度，当对方打出“此刻永恒”时从加四次出手数变为加8点血量.当前出手数{self.player_moves}"
                            self.add4message = False
                            self.add8message = False
                        else:
                            if self.hardest:
                                self.message = f"你有{self.player_moves}次出手机会，上一把对方出的牌是{stringlw}，（瞳孔发光）孩子，这并不好笑。"
                            self.message = f"你有{self.player_moves}次出手机会，上一把对方出的牌是{stringlw}"
                else:
                    self.start_animating_card("computer")
                    self.adjust_hand(self.computer_hand, "Computer")
                    self.computer.reset_on_my_turn()
                    print(f"电脑的额外出手数为{self.pending_extra_moves_for_computer}==================")
                    self.computer_moves = 1 + self.pending_extra_moves_for_computer
                    self.pending_extra_moves_for_computer = 0
                    self.computer_action_time = current_time + COMPUTER_DELAY

                    # 根据电脑的濒死状态设置提示信息
                    if self.computer.DEAD:
                        self.message = f"这老头已经奄奄一息了，你有{self.player_moves}次出手数，再加把劲！"
                    elif self.skip == True:
                        self.message = f"这是什么以退为进的运筹帷幄吗？……"
                        self.skip = False
                    elif self.negative == True:
                        self.message = f"你貌似很调皮嘛，有着自己的想法，但是请你好好对局哦"
                        self.negative = False
                    else:
                        if self.player.DEAD:
                            if self.hard:
                                self.message=f"（瞳孔发光）孩子，新手村都没出就来打boss吗，有点意思"
                            elif self.hardest:
                                self.message=f"（瞳孔发光）既然来都来了，不尝试尝试怎么知道赢不了"
                            else:
                                self.message="（瞳孔发光）孩子，人机都能把你打濒死，你还在挣扎什么，我是你我就直接退了"
                        else:
                            self.message = "当你打出牌的时候，牌也打出了你……"

                self.new_turn = False  # 确保在发牌后将 new_turn 设置为 False

            # 电脑回合自动出牌
            if self.turn == "computer" and self.animating_card is None and current_time >= self.computer_action_time:
                # 电脑自动换牌逻辑（在出牌前执行）
                swap_name = {'get_time', 'GETTIME', 'fast', 'wind', 'timer'}  # 使用集合提高查询效率

                # 创建副本避免修改遍历中的列表
                hand_copy = self.computer_hand.copy()

                for idx, card in enumerate(hand_copy):
                    if card.name in swap_name:
                        # 只处理首尾位置的关键牌
                        if idx == 0 or idx == len(hand_copy) - 1:
                            # 寻找中间非关键牌交换
                            for mid_idx in range(1, len(hand_copy) - 1):
                                if hand_copy[mid_idx].name not in swap_name:
                                    # 交换位置
                                    self.computer_hand[idx], self.computer_hand[mid_idx] = \
                                        self.computer_hand[mid_idx], self.computer_hand[idx]
                                    break  # 交换后立即退出循环
                print(f"==========电脑当前出手数为{self.computer_moves}")
                self.have_played=False
                flagu = 0
                legal_extra = 0
                print(f"电脑手牌: {[c.name for c in self.computer_hand]}")
                #简单难度
                if self.easy:
                    self.computer_moves=1
                    self.computer_play_queue=easy(self.computer_hand)
                    if self.computer_play_queue:
                        print(f"简单难度下的出牌决策为{[c for c in self.computer_play_queue]}")
                        card_name=self.computer_play_queue[0]
                        if card_name=="back_go" or card_name=="get_time":
                            self.computer.hp+=4
                            self.add4message=True
                        elif card_name=="GETTIME":
                            self.computer.hp+=8
                            self.add8message=True

                #中等难度
                elif self.middle:
                    self.computer_moves=1
                    self.computer_play_queue=middle(self.computer_hand,self.computer,self.player,self)
                    if self.computer_play_queue:
                        print(f"中等难度下的出牌决策为{[c for c in self.computer_play_queue]}")
                        card_name = self.computer_play_queue[0]
                        if card_name == "back_go" or card_name == "get_time":
                            self.computer.hp += 4
                            self.add4message = True
                        elif card_name == "GETTIME":
                            self.computer.hp += 8
                            self.add8message = True


                #困难难度
                elif self.hard :
                    # 生成新的出牌序列（每次回合重置）
                    if  not self.computer_play_queue :
                        print("开始行动决策")
                        self.computer_play_queue = computer_choose_card(
                            self.computer_hand.copy(), self.computer, self.player, self)

                    if self.computer_moves>1 and self.computer_play_queue:
                        print("=====被动继承上回合的出手数，开始额外出手决策===")
                        self.computer_play_queue=computer_extra_active_card(self.computer_moves,self.computer,self.player,self,self.computer_play_queue)
                        print(f"新出牌队列: {[c for c in self.computer_play_queue]}")
                    if self.computer_play_queue:
                        if len(self.computer_play_queue)==1 and (self.computer_play_queue[0]=="get_time" or self.computer_play_queue[0]=="GETTIME") and self.computer_hand is not None:
                            legal_extra+= 2 if self.computer_play_queue[0]=="get_time" else 4
                            self.computer_moves=legal_extra
                            for card3 in self.computer_hand:
                                if legal_extra==2 and card3.name=="get_time":
                                    self.computer_hand.remove(card3)
                                elif legal_extra==4 and card3.name=="GETTIME":
                                    self.computer_hand.remove(card3)
                            flagu=1
                            print(f"电脑使用秩序牌额外获取了{legal_extra}次出手数")

                    self.computer_play_queue=computer_extra_active_card(legal_extra,self.computer,self.player,self,self.computer_play_queue)
                    if self.computer_play_queue:
                        print(f"我已经非常无语时候的决策牌组{[c for c in self.computer_play_queue]}")
                        if len(self.computer_play_queue)>1 and self.computer_moves<len(self.computer_play_queue) and flagu==0:
                            self.computer_play_queue=computer_consume_cards(self,self.computer_play_queue,len(self.computer_play_queue))
                            if self.computer_play_queue is None:
                                print("==========无法完成多出手决策===============")
                            else:
                                extra_move=self.computer_play_queue.pop(-1)
                                self.computer_moves+=extra_move
                                print(f"电脑通过消耗手牌获取了{extra_move}次额外出手数")
                                # 执行出牌
                elif self.hardest:
                    #杀戮难度模式
                    # 生成新的出牌序列（每次回合重置）
                    if not self.computer_play_queue:
                        print("开始行动决策")
                        self.computer_play_queue = computer_choose_card(
                            self.computer_hand.copy(), self.computer, self.player, self)

                    if self.computer_moves > 1 and self.computer_play_queue:
                        print("=====被动继承上回合的出手数，开始额外出手决策===")
                        self.computer_play_queue = computer_extra_active_card(self.computer_moves, self.computer,
                                                                              self.player, self,
                                                                              self.computer_play_queue)
                        print(f"新出牌队列: {[c for c in self.computer_play_queue]}")
                    if self.computer_play_queue:
                        if len(self.computer_play_queue) == 1 and (
                                self.computer_play_queue[0] == "get_time" or self.computer_play_queue[
                            0] == "GETTIME") and self.computer_hand is not None:
                            legal_extra += 2 if self.computer_play_queue[0] == "get_time" else 4
                            self.computer_moves = legal_extra
                            for card3 in self.computer_hand:
                                if legal_extra == 2 and card3.name == "get_time":
                                    self.computer_hand.remove(card3)
                                elif legal_extra == 4 and card3.name == "GETTIME":
                                    self.computer_hand.remove(card3)
                            flagu = 1
                            print(f"电脑使用秩序牌额外获取了{legal_extra}次出手数")

                    self.computer_play_queue = computer_extra_active_card(legal_extra, self.computer, self.player, self,
                                                                          self.computer_play_queue)
                    if self.computer_play_queue:
                        print(f"我已经非常无语时候的决策牌组{[c for c in self.computer_play_queue]}")
                        if len(self.computer_play_queue) > 1 and self.computer_moves < len(
                                self.computer_play_queue) and flagu == 0:
                            self.computer_play_queue = computer_consume_cards(self, self.computer_play_queue,
                                                                              len(self.computer_play_queue))
                            if self.computer_play_queue is None:
                                print("==========无法完成多出手决策===============")
                            else:
                                extra_move = self.computer_play_queue.pop(-1)
                                self.computer_moves += extra_move
                                print(f"电脑通过消耗手牌获取了{extra_move}次额外出手数")
                                # 执行出牌


                #-200
#self.end_player_turn
                if self.computer_play_queue :
                    print(f"当前决策牌组为{[c for c in self.computer_play_queue]},当前出手数为{self.computer_moves}")
                    self.front_computer_queue.clear()
                    self.front_computer_queue_name.clear()
                    for i in self.computer_hand:
                        if i.name in self.computer_play_queue and i.name not in self.front_computer_queue_name:
                            self.front_computer_queue.add(i)
                            self.front_computer_queue_name.add(i.name)

                if self.computer_play_queue  and (self.computer_moves==1 or len(self.computer_play_queue)==1):
                    card=self.computer_hand[0]
                    for cards in self.computer_hand:
                        if cards.name==self.computer_play_queue[-1]:
                            card=cards
                            print(f"电脑打出{card.name}")
                            self.play_card2(card)
                            self.played_card=card
                            self.played_card_time=pygame.time.get_ticks()
                            self.computer_action_time = current_time + EFFECT_DURATION + 500
                            self.computer_moves -= 1
                            pygame.display.flip()
                            break
                elif self.computer_play_queue is None or len(self.computer_play_queue) ==0:
                    print("跳过回合")
                    self.message=f"看起来……对面要有阴谋了"
                elif self.computer_play_queue  and  len(self.computer_play_queue)>1:
                    while len(self.computer_play_queue)>0:
                        card=self.computer_play_queue.pop(0)
                        print(f"========================现在电脑决策卡牌组的长度为{len(self.computer_play_queue)}")
                        for card2 in self.computer_hand:
                            if card2 not in self.computer_hand:
                                print(f"当前电脑的手牌中没有{card2.name}牌")
                            if card2.name==card and card2.name not in self.played:
                                print(f"电脑打出: {card2.name}")
                                self.play_card2(card2)
                                self.played_card = card2
                                self.played.append(card2.name)
                                self.played_card_time = pygame.time.get_ticks()
                                self.computer_action_time = current_time + EFFECT_DURATION + 500
                                self.computer_moves-=1
                # 电脑自动换牌逻辑（在出牌后执行）
                swap_name = {'get_time', 'GETTIME', 'fast', 'wind', 'timer'}
                hand_copy = self.computer_hand.copy()
                for idx, card in enumerate(hand_copy):
                    if card.name in swap_name:
                        if idx == 0 or idx == len(hand_copy) - 1:
                            for mid_idx in range(1, len(hand_copy) - 1):
                                if hand_copy[mid_idx].name not in swap_name:
                                    self.computer_hand[idx], self.computer_hand[mid_idx] = \
                                        self.computer_hand[mid_idx], self.computer_hand[idx]
                                    break
                # 清除队列防止残留
                self.played = []
                self.computer_play_queue = []
                self.end_computer_turn()

            if self.popup_message and pygame.time.get_ticks() - self.popup_start_time >= self.popup_duration+2250:
                self.popup_message = None

            if self.played_card and current_time - self.played_card_time > EFFECT_DURATION+1000:
                self.played_card = None
                self.damage_indicator=None
                self.heal_indicator = None

    def draw(self):

        if self.current_state == "start_menu":
            self.screen.fill((0, 0, 0))
            if self.start_menu_image:
                self.screen.blit(self.start_menu_image, (0, 0))

            if self.current_state == "start_menu":
                # 如果未在播放开场音乐，则开始播放
                if not self.is_playing_open_music:
                    pygame.mixer.music.load(self.open_music_path)
                    pygame.mixer.music.set_volume(self.background_volume)
                    pygame.mixer.music.play(-1)  # -1 表示无限循环
                    self.is_playing_open_music = True
                    self.is_playing_fighting_music = False  # 确保对战音乐停止
                self.screen.fill((0, 0, 0))
                if self.start_menu_image:
                    self.screen.blit(self.start_menu_image, (0, 0))

                # 获取鼠标位置
                mouse_pos = pygame.mouse.get_pos()
                is_hovered_3 = self.difficulty_buttons[3]["rect"].collidepoint(mouse_pos)

                # 绘制三个难度按钮
                for btn in self.difficulty_buttons:
                    is_hovered = btn["rect"].collidepoint(mouse_pos)
                    if is_hovered_3 == False:
                        if btn["difficulty"] == "hardest":
                            continue  # 不显示
                    # 根据悬停状态调整尺寸
                    if is_hovered:
                        scale = 2
                        scaled_w = int(btn["rect"].width * scale)
                        scaled_h = int(btn["rect"].height * scale)
                        scaled_img = pygame.transform.smoothscale(
                            self.button_images[btn['difficulty']],
                            (scaled_w, scaled_h)
                        )
                        # 保持按钮中心不变
                        pos = (
                            btn["rect"].centerx - scaled_w // 2,
                            btn["rect"].centery - scaled_h // 2
                        )
                        if self.sfx_button_hover and not self.hover_channel.get_busy():
                            self.hover_channel.play(self.sfx_beginvoice)
                    else:
                        scaled_img = self.button_images[btn['difficulty']]
                        pos = btn["rect"].topleft

                    self.screen.blit(scaled_img, pos)
                hidden_btn = self.difficulty_buttons[3]
                if hidden_btn["visible"]:
                    scale = 2.4  # 放大倍数大于其他按钮
                    scaled_w = int(275 * scale)
                    scaled_h = int(128 * scale)
                    scaled_img = pygame.transform.smoothscale(
                        self.button_images['hardest'],
                        (scaled_w, scaled_h)
                    )
                    # 保持中心点不变
                    pos = (
                        hidden_btn["rect"].centerx - scaled_w // 2,
                        hidden_btn["rect"].centery - scaled_h // 2
                    )
                    self.screen.blit(scaled_img, pos)

                    # 添加粒子特效
                    spark_color = (255, 215, 0)  # 金色粒子
                    for _ in range(5):  # 生成5个粒子
                        pos = (
                            hidden_btn["rect"].centerx + random.randint(-20, 20),
                            hidden_btn["rect"].centery + random.randint(-20, 20)
                        )
                        pygame.draw.circle(self.screen, spark_color, pos, 2)


        elif self.current_state == "ending":

            # 显示当前阶段的图片

            current_image = self.ending_images[self.ending_phase] if self.ending_phase == 1 else self.ending_image

            if current_image:
                self.screen.blit(current_image, (0, 0))

            # 添加操作提示文字

            prompt_font = self.chinese_font

            prompt_text1 = prompt_font.render(f"点击切换画面 | 点击超过十次则自动退出，当前点击了{self.ending_click_count}次", True, (100, 13, 153))  # 金色

            prompt_rect1 = prompt_text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15))

            prompt_text2 = prompt_font.render("制作人员名单", True, (175, 18, 237)) if self.ending_phase == 1 else prompt_font.render("战斗结算画面", True, (135, 206, 250))  # 不同状态不同颜色

            prompt_rect2 = prompt_text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))

            self.screen.blit(prompt_text1, prompt_rect1)

            self.screen.blit(prompt_text2, prompt_rect2)

        elif self.current_state == "gaming":  # 游戏进行状态
            current_time = pygame.time.get_ticks()

            # 开局覆盖层
            if self.show_initial_overlay:
                # 创建透明覆盖层
                overlay = pygame.Surface((SCREEN_WIDTH, 446), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))  # 半透明黑色
                self.screen.blit(overlay, (0, SCREEN_HEIGHT - 446))

                # 添加提示文字
                wait_font = pygame.font.SysFont("simhei", 60, bold=True)
                wait_text = wait_font.render("游戏初始化中，请稍候...", True, (168, 255, 127))
                text_rect = wait_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 446 // 2))
                self.screen.blit(wait_text, text_rect)

            if self.is_dealing_animation:
                # 透明覆盖层
                overlay = pygame.Surface((SCREEN_WIDTH, 446), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))  # 半透明黑色
                self.screen.blit(overlay, (0, SCREEN_HEIGHT - 446))

                # 发牌提示文字
                wait_font = pygame.font.SysFont("simhei", 90, bold=True)
                wait_text = wait_font.render("", True, (168, 255, 127))
                self.screen.blit(wait_text, (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT - 250))

            if self.preloaded_images.get("background") is not None:
                bg = pygame.transform.smoothscale(self.preloaded_images["background"],
                                                  (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.screen.blit(bg, (0, 0))
            else:
                self.screen.fill((0, 100, 0))
            mouse_pos = pygame.mouse.get_pos()

            # ================================================
            # 玩家手牌绘制部分（关键修改）
            # ================================================



            hovered_index = None
            total_width = len(self.player_hand) * CARD_SPACING
            start_x = (
                              SCREEN_WIDTH - total_width) // 2 if self.player_hand else SCREEN_WIDTH // 2 - HAND_CARD_WIDTH // 2

            # 初始化悬停卡牌位置记录
            self.hovered_card_rect = None

            # 第一次遍历：检测悬停索引
            for i, card in enumerate(self.player_hand):
                pos = (start_x + i * CARD_SPACING, SCREEN_HEIGHT - HAND_CARD_HEIGHT - 20)
                rect = pygame.Rect(pos, (HAND_CARD_WIDTH, HAND_CARD_HEIGHT))

                # 缩小悬停判断范围（仅卡牌中心区域）
                center_rect = pygame.Rect(
                    rect.centerx - HAND_CARD_WIDTH // 5,
                    rect.centery - HAND_CARD_HEIGHT // 5,
                    HAND_CARD_WIDTH // 2,
                    HAND_CARD_HEIGHT // 2
                )

                if center_rect.collidepoint(mouse_pos):
                    hovered_index = i
                    if   self.current_state == "gaming":
                        if current_time - self.game_start_time < 13567:
                            hovered_index=None
                    # 检查是否是新的悬停卡牌
                    if hovered_index != self.last_hovered_index:
                        # 播放悬停音效
                        if not self.hover_channel.get_busy():  # 确保音效通道空闲
                            self.hover_channel.play(self.sfx_hover)
                        self.last_hovered_index = hovered_index  # 更新上一次悬停的卡牌索引
                    break  # 确保只检测第一个悬停的卡牌
            else:
                # 如果没有卡牌被悬停，重置 last_hovered_index
                self.last_hovered_index = None
                self.messageflag = False

            # 第二次遍历：绘制非悬停卡牌
            for i, card in enumerate(self.player_hand):
                if i != hovered_index:
                    pos = (start_x + i * CARD_SPACING, SCREEN_HEIGHT - HAND_CARD_HEIGHT - 20)
                    card.draw(self.screen, pos)

            # 第三次处理：绘制悬停卡牌并记录位置
            if hovered_index is not None:
                self.messageflag=True
                card = self.player_hand[hovered_index]
                if card.name=="fireK":
                    damage=1
                    if self.player.FK:
                        if self.hardest:
                            damage+=6
                            if self.player.fire_attach:
                                damage+=6
                        else:
                            damage+=4
                            if self.player.fire_attach:
                                damage+=3
                    if self.player.FD:
                        if self.hardest:
                            damage+=6
                        else:
                            damage+=4
                    if self.player.DEAD:
                        damage+=5
                    if self.computer.water_attach:
                        damage+=2
                    if self.player.burn_bonus:
                        damage+=2
                    self.message3=f"你有{self.player_moves}次出手次数，当前选择为火杀，预期伤害为{damage}"
                elif card.name=="waterK":
                    damage = 1
                    heal=0
                    flag=0
                    if self.player.WK:
                        if self.hardest:
                            damage+=3
                            if self.player.water_attach:
                                flag+=2
                        else:
                            damage += 2
                            if self.player.water_attach:
                                flag+=1
                    if self.player.WD:
                        if self.hardest:
                            damage+=3
                            heal+=4
                        else:
                            damage+=2
                            heal += 3
                    if self.computer.fire_attach:
                        damage += 3
                    if self.player.DEAD:
                        damage += 2
                        flag+=1
                    heal+=damage*flag
                    self.message3 = f"你有{self.player_moves}次出手次数，当前选择为水杀，预期伤害为{damage}，预期治疗量为{heal}"
                elif card.name=="timer":
                    if self.hardest:
                        self.message3 = f"你有{self.player_moves}次出手次数，当前选择为时源，受到水火祝福，预期治疗量为{4 * self.player_moves}"
                    else:
                        self.message3=f"你有{self.player_moves}次出手次数，当前选择为时源，预期治疗量为{2*self.player_moves}"
                elif card.name=="fireD":
                    if self.hardest:
                        self.message3 = f"你有{self.player_moves}次出手次数，当前选择为火盾，可以在本回合免疫对方一次火杀伤害，且受到水火的祝福，提升本次火杀6点伤害"
                    else:
                        self.message3=f"你有{self.player_moves}次出手次数，当前选择为火盾，可以在本回合免疫对方一次火杀伤害，且提升本次火杀4点伤害"
                elif card.name=="waterD":
                    if self.hardest:
                        self.message3 = f"你有{self.player_moves}次出手次数，当前选择为水盾且受水火的祝福，可以在本回合免疫对方一次水杀伤害，提升本次水杀3点伤害并随着水杀打出后为你治愈4点"
                    else:
                        self.message3=f"你有{self.player_moves}次出手次数，当前选择为水盾，可以在本回合免疫对方一次水杀伤害，提升本次水杀2点伤害并随着水杀打出后为你治愈3点"
                elif card.name=="fire":
                    heal=1
                    if self.hardest:
                        heal+=2
                        if self.player.fire_attach:
                            heal += 1
                            self.message3 = f"你有{self.player_moves}次出手次数，当前选择为火源，受到水火祝福，预期治疗量为{heal}点，且你的火附着会被火源所熄灭"
                        else:
                            self.message3 = f"你有{self.player_moves}次出手次数，当前选择为火源，受到水火祝福，预期治疗量为{heal}点"
                    else:

                        if self.player.fire_attach:
                            heal+=1
                            self.message3=f"你有{self.player_moves}次出手次数，当前选择为火源，预期治疗量为{heal}点，且你的火附着会被火源所熄灭"
                        else:
                            self.message3=f"你有{self.player_moves}次出手次数，当前选择为火源，预期治疗量为{heal}点"
                elif card.name=="water":
                    heal=1
                    if self.hardest:
                        heal+=2
                        if self.player.water_attach:
                            heal += 2
                        self.message3 = f"你有{self.player_moves}次出手次数，当前选择为水源，受到水火祝福，预期治疗量为{heal}点，你的水附着不会被水源所汲干"
                    else:
                        if self.player.water_attach:
                            heal+=2
                        self.message3=f"你有{self.player_moves}次出手次数，当前选择为水源，预期治疗量为{heal}点，你的水附着不会被水源所汲干"
                elif card.name=="order":
                    if self.hardest:
                        self.message3=f"你有{self.player_moves}次出手次数，当前选择为序源，会删除你的最后一张卡,受到水火祝福，为你治愈4点。你应合理运用秩序的力量……"
                    else:
                        self.message3 = f"你有{self.player_moves}次出手次数，当前选择为序源，会删除你的最后一张卡并为你治愈2点。你应合理运用秩序的力量……"
                elif card.name=="FK":
                    if self.hardest:
                        if self.player.fire_attach:
                            self.message3 = f"你有{self.player_moves}次出手次数，当前选择为火刃，受到水火的祝福，火刃之下你的火杀伤害+6；而火刃之下你身燃火，因此火杀伤害额外+4"
                        else:
                            self.message3 = f"你有{self.player_moves}次出手次数，当前选择为火刃，受到水火的祝福，火刃之下你的火杀伤害+6"
                    else:
                        if self.player.fire_attach:
                            self.message3 = f"你有{self.player_moves}次出手次数，当前选择为火刃，火刃之下你的火杀伤害+4；而火刃之下你身燃火，因此火杀伤害额外+3"
                        else:
                            self.message3=f"你有{self.player_moves}次出手次数，当前选择为火刃，火刃之下你的火杀伤害+4"
                elif card.name=="WK":
                    if self.hardest:
                        if self.player.water_attach:
                            self.message3 = f"你有{self.player_moves}次出手次数，当前选择为水刃且受到水火的祝福，水刃之下水杀伤害+3；而水刃之下你身着水，若打出水杀则获得两倍于同等伤害的治疗量"
                        else:
                            self.message3 = f"你有{self.player_moves}次出手次数，当前选择为水刃且受到水火的祝福，水刃之下水杀伤害+3"
                    else:
                        if self.player.water_attach:
                            self.message3=f"你有{self.player_moves}次出手次数，当前选择为水刃，水刃之下水杀伤害+2；而水刃之下你身着水，因此若打出水杀则获得同等于伤害的治疗量"
                        else:
                            self.message3 = f"你有{self.player_moves}次出手次数，当前选择为水刃，水刃之下水杀伤害+2"
                elif card.name=="fast":
                    self.message3=f"你有{self.player_moves}次出手次数，当前选择为动如脱兔，永久提升自身速度10点"
                elif card.name=="wind":
                    self.message3=f"你有{self.player_moves}次出手次数，当前选择为迅疾如风，永久提升自身速度20点"
                elif card.name=="get_time":
                    self.message3=f"你有{self.player_moves}次出手次数，聆听时间的回响，纵使光阴如梭……打出此牌你将获取三次出手机会。"
                elif card.name=="GETTIME":
                    self.message3=f"你有{self.player_moves}次出手次数，寂静如众神的残骸，窥见永恒如我心漫长……打出此牌你将获取四次出手机会"
                elif card.name=="ORDER":
                    self.message3=f"你有{self.player_moves}次出手次数，于孤闭之处绽放熵增，打出此牌双方将各获取两张牌"
                elif card.name=="regive":
                    self.message3=f"你有{self.player_moves}次出手次数，当前选择为索取，你可以获取对方第一张手牌"
                elif card.name=="REGIVE":
                    self.message3=f"你有{self.player_moves}次出手次数，当前选择为更多的索取，你可以在获取对方第一张手牌的同时再随机获取一张牌"
                elif card.name=="burn":
                    self.message3=f"你有{self.player_moves}次出手次数，当前选择为自我燃烧，会使你身燃火并提升本回合火杀2点伤害"
                elif card.name=="flood":
                    if self.hardest:
                        self.message3 = f"你有{self.player_moves}次出手次数，当前选择为自我淹没，受水火祝福，会使你身着水并治愈三点"
                    else:
                        self.message3=f"你有{self.player_moves}次出手次数，当前选择为自我淹没，会使你身着水并治愈一点"
                elif card.name=="back_go":
                    self.message3=f"你有{self.player_moves}次出手次数，当前选择为以退为进，将立即结束本次出牌阶段，下回合你将有两次初始出手数"





                # 计算悬停位置（放大并向上偏移）
                original_pos = (start_x + hovered_index * CARD_SPACING, SCREEN_HEIGHT - HAND_CARD_HEIGHT - 20)
                hover_pos = (original_pos[0], original_pos[1] - 80)  # 向上偏移50像素
                # 绘制放大后的卡牌并获取实际位置
                rect = card.draw(self.screen, hover_pos, hovered=True)
                self.hovered_card_rect = rect  # 关键！记录最终渲染位置
            else:
                self.messageflag = False  # ✅ 必须在这里立即清除状态
                self.last_hovered_index = None  # 需要同时清除上次悬停记录


            # ======================================================
            total_width_comp = len(self.computer_hand) * CARD_SPACING
            start_x_comp = (
                                       SCREEN_WIDTH - total_width_comp) // 2 if self.computer_hand else SCREEN_WIDTH // 2 - HAND_CARD_WIDTH // 2
            for i in range(len(self.computer_hand)):
                pos = (start_x_comp + i * CARD_SPACING, 20)
                comp_img = get_computer_card_image()
                self.screen.blit(comp_img, pos)

            # 按钮图像
            consume_image = pygame.image.load(
                resource_path("fire_and_water/consume.png")).convert_alpha()  # 加载consume按钮的图像
            skip_image = pygame.image.load(resource_path("fire_and_water/go.png")).convert_alpha()  # 加载skip按钮的图像
            swap_image = pygame.image.load(resource_path("fire_and_water/swap.png")).convert_alpha()  # 加载swap按钮的图像
            # 调整图像大小，确保它们适应按钮的尺寸
            consume_image = pygame.transform.scale(consume_image, self.consume_button_rect.size)  # 调整为consume按钮大小
            skip_image = pygame.transform.scale(skip_image, self.skip_button_rect.size)  # 调整为go按钮大小
            swap_image = pygame.transform.scale(swap_image, self.swap_button_rect.size)  # 调整为swap按钮大小
            # 绘制跳过按钮
            current_time = pygame.time.get_ticks()
            btn_to_draw = [
                (self.skip_hovered, self.skip_button_rect, skip_image, "skip"),
                (self.consume_hovered, self.consume_button_rect, consume_image, "consume"),
                (self.swap_hovered, self.swap_button_rect, swap_image, "swap")
            ]

            for is_hovered, rect, img, btn_type in btn_to_draw:
                if is_hovered:
                    # 计算缩放比例
                    scale = 1.25
                    scaled_width = int(rect.width * scale)
                    scaled_height = int(rect.height * scale)

                    # 计算晃动偏移量
                    if not hasattr(self, f'{btn_type}_hover_start'):
                        setattr(self, f'{btn_type}_hover_start', current_time)
                    hover_duration = current_time - getattr(self, f'{btn_type}_hover_start')
                    x_offset = int(5 * math.sin(hover_duration / 100 * math.pi * 1.25))  # 左右晃动

                    # 创建缩放后的图像
                    scaled_img = pygame.transform.smoothscale(img, (scaled_width, scaled_height))

                    # 计算位置（保持中心点）
                    pos_x = rect.centerx - scaled_width // 2 + x_offset
                    pos_y = rect.centery - scaled_height // 2
                    self.screen.blit(scaled_img, (pos_x, pos_y))
                else:
                    if hasattr(self, f'{btn_type}_hover_start'):
                        delattr(self, f'{btn_type}_hover_start')
                    self.screen.blit(img, rect.topleft)
            exit_img = self.button_images["exit"]
            if self.exit_hovered:
                # 悬停放大效果
                scale = 1.1
                scaled_w = int(140 * scale)
                scaled_h = int(63 * scale)
                scaled_img = pygame.transform.smoothscale(exit_img, (scaled_w, scaled_h))
                # 添加晃动效果
                hover_duration = pygame.time.get_ticks() % 1000
                x_offset = int(5 * math.sin(hover_duration / 100 * math.pi))
                pos = (
                    self.exit_button_rect.centerx - scaled_w // 2 + x_offset,
                    self.exit_button_rect.centery - scaled_h // 2
                )
            else:
                scaled_img = exit_img
                pos = self.exit_button_rect.topleft

            self.screen.blit(scaled_img, pos)

            comp_status = [
                f"血量: {self.computer.hp}",
                f"速度: {self.computer.speed}",
                f"刃上之火态: {'火刃正上' if self.computer.FK or self.hardest else '无'}",
                f"刃上之水态: {'水刃正上' if self.computer.WK or self.hardest else '无'}",
                f"火盾之庇护: {'火盾已至' if self.computer.FD else '无'}",
                f"水盾之庇护: {'水盾已至' if self.computer.WD else '无'}",
                f"身燃火: {'是' if self.computer.fire_attach else '无'}",
                f"身着水: {'是' if self.computer.water_attach else '无'}",
                f"濒死: {'是' if self.computer.DEAD else '否'}"
            ]
            for i, line in enumerate(comp_status):
                surf = self.chinese_font.render(line, True, (255, 255, 255))  # 使用中文字体
                self.screen.blit(surf, (20, 20 + i * 20))

            # 玩家状态显示
            player_status = [
                f"血量: {self.player.hp}",
                f"速度: {self.player.speed}",
                f"刃上之火态: {'火刃正上' if self.player.FK else '无'}",
                f"刃上之水态: {'水刃正上' if self.player.WK else '无'}",
                f"火盾之庇护: {'火盾已至' if self.player.FD else '无'}",
                f"水盾之庇护: {'水盾已至' if self.player.WD else '无'}",
                f"身燃火: {'是' if self.player.fire_attach else '无'}",
                f"身着水: {'是' if self.player.water_attach else '无'}",
                f"濒死: {'是' if self.player.DEAD else '否'}"
            ]
            for i, line in enumerate(player_status):
                surf = self.chinese_font.render(line, True, (255, 255, 255))  # 使用中文字体
                self.screen.blit(surf, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 200 + i * 20))

            # 渲染所有的提示语
            current_time = pygame.time.get_ticks()
#self.message
            # 绘制所有正在显示的提示语
            for effect_text in self.effect_texts[:]:
                elapsed_time = current_time - effect_text["start_time"]

                # 如果提示语超过显示时长，则删除
                if elapsed_time > self.effect_display_duration+1500:
                    self.effect_texts.remove(effect_text)
                else:
                    # 渲染并显示提示语
                    text_surface = self.font.render(effect_text["text"], True, effect_text["color"])
                    pos_x = SCREEN_WIDTH//2-160  # 默认位置


                    pos_y = SCREEN_HEIGHT // 2 + self.effect_texts.index(effect_text) * 10+20
                    self.screen.blit(text_surface, (pos_x, pos_y))

            # 提示消息
            message_surf3=self.chinese_font.render(self.message3, True, (149, 245, 149))  # 使用中文字体
            message_surf = self.chinese_font.render(self.message, True, (255, 255, 0))  # 使用中文字体
            self.screen.blit(message_surf, (300, SCREEN_HEIGHT // 2-30))
            self.screen.blit(message_surf3, (300, SCREEN_HEIGHT // 2))
#牌呵
            # self.played_card
            # 游戏结束文字也使用中文字体
            if self.game_over:
                result_font = self.chinese_font  # 使用中文字体
                result_surf = result_font.render(self.result_text, True, self.result_color)

            if self.played_card is not None:
                #print("手牌有效===================================")
                k=0
                # print(f"当前是{self.current_turn}")

                if self.current_turn == "player":
                    k=1
                    # print(f"电脑当前的决策牌组为{[c.name for c in self.front_computer_queue]}")
                    num_cards = len(self.front_computer_queue)  #
                    if num_cards > 1 and self.current_turn == "player" and self.front_computer_queue is not None:
                        # 多张牌水平排列
                        # print("多出手牌渲染成功")
                        total_width = num_cards * PLAYED_CARD_WIDTH
                        start_x = (SCREEN_WIDTH - total_width) // 2

                        for i, card in enumerate(self.front_computer_queue):
                            pos = (start_x + i * PLAYED_CARD_WIDTH, (SCREEN_HEIGHT - PLAYED_CARD_HEIGHT) // 2)
                            scaled_img = pygame.transform.smoothscale(card.image,
                                                                      (PLAYED_CARD_WIDTH, PLAYED_CARD_HEIGHT))
                            self.screen.blit(scaled_img, pos)
                    # print("单张玩家牌渲染成功")
                    else:
                        #print("yes")
                        scaled_img = pygame.transform.smoothscale(self.played_card.image,
                                                                  (PLAYED_CARD_WIDTH, PLAYED_CARD_HEIGHT))
                        # print("代码走到这里了吗")
                        center_pos = (
                        (SCREEN_WIDTH - PLAYED_CARD_WIDTH) // 2, (SCREEN_HEIGHT - PLAYED_CARD_HEIGHT) // 2)
                        # print("走到了兄弟，走到了")
                        self.screen.blit(scaled_img, center_pos)
                else:
                    #print("no")
                    scaled_img = pygame.transform.smoothscale(self.played_card.image,
                                                              (PLAYED_CARD_WIDTH, PLAYED_CARD_HEIGHT))
                    # print("代码走到这里了吗")
                    center_pos = (
                        (SCREEN_WIDTH - PLAYED_CARD_WIDTH) // 2, (SCREEN_HEIGHT - PLAYED_CARD_HEIGHT) // 2)
                    # print("走到了兄弟，走到了")
                    self.screen.blit(scaled_img, center_pos)
                # print("刷新了兄弟")

                # 初始化 pos_effect
                pos_effect = (50, (SCREEN_HEIGHT - math.ceil(SCREEN_HEIGHT / 4)) // 2)

                if self.damage_indicator is not None or self.heal_indicator is not None:
                    if self.damage_indicator and self.heal_indicator:
                        if self.damage_indicator and pygame.time.get_ticks() - self.effect_start_time < 4000:
                            damage_surf = self.effect_font.render(self.damage_indicator, True, self.damage_color)
                            damage_rect = damage_surf.get_rect(midleft=(50, SCREEN_HEIGHT // 2 - 50))  # 上移30像素

                            heal_surf = self.effect_font.render(self.heal_indicator, True, self.heal_color)
                            heal_rect = heal_surf.get_rect(midleft=(50, SCREEN_HEIGHT // 2 + 10))  # 下移30像素（总间隔60像素）

                            self.screen.blit(damage_surf, damage_rect)
                            self.screen.blit(heal_surf, heal_rect)

                    elif self.damage_indicator is not None:
                        #print("启动伤害提示")
                        # 渲染伤害提示（上方）
                        if self.damage_indicator and pygame.time.get_ticks() - self.effect_start_time < 2000:
                            damage_surf = self.effect_font.render(self.damage_indicator, True, self.damage_color)
                            damage_rect = damage_surf.get_rect(midleft=(50, SCREEN_HEIGHT // 2 - 50))  # 上移30像素
                            self.screen.blit(damage_surf, damage_rect)
                    elif self.heal_indicator is not None:
                        #print("启动治愈提示")
                        # 渲染治愈提示（下方）
                        if self.heal_indicator and pygame.time.get_ticks() - self.effect_start_time < 2000:
                            heal_surf = self.effect_font.render(self.heal_indicator, True, self.heal_color)
                            heal_rect = heal_surf.get_rect(midleft=(50, SCREEN_HEIGHT // 2 + 10))  # 下移30像素（总间隔60像素）
                            self.screen.blit(heal_surf, heal_rect)


            def render_bold_text(font, text, color):
                """手动加粗文本"""
                text_surface = font.render(text, True, color)
                bold_surface = pygame.Surface((text_surface.get_width() + 2, text_surface.get_height() + 2),
                                              pygame.SRCALPHA)
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        bold_surface.blit(text_surface, (dx + 1, dy + 1))
                bold_surface.blit(text_surface, (1, 1))
                return bold_surface

            # 使用手动加粗
            text_surface = render_bold_text(self.chinese_font, "得以治愈！", (0, 255, 0))

            if self.animating_card is not None:
                pos = self.animating_card.get("current_pos", self.animating_card["start_pos"])
                if self.animating_card["side"] == "computer":
                    anim_surf = get_computer_card_image()
                else:
                    anim_surf = self.animating_card["card"].image
                self.screen.blit(anim_surf, pos)
            if self.popup_message and pygame.time.get_ticks() - self.popup_start_time < self.popup_duration + 2250:
                popup_width = 1185
                popup_height = 495
                popup_x = (SCREEN_WIDTH - popup_width) // 2
                popup_y = (SCREEN_HEIGHT - popup_height) // 2

                # 绘制半透明背景
                s = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
                s.fill((50, 50, 50, 0))  # 半透明灰黑色
                self.screen.blit(s, (popup_x, popup_y))

                # 绘制文字
                font = pygame.font.SysFont("arial", 64, bold=True)
                text_surf = font.render(self.popup_message, True, self.popup_color)
                text_rect = text_surf.get_rect(center=(popup_x + popup_width // 2, popup_y + popup_height // 2))
                self.screen.blit(text_surf, text_rect.topleft)
                # 修改所有文字渲染调用，例如：
                if self.effect_extra_text:
                    # 设置 pos_effect 的位置
                    pos_effect = (50, (SCREEN_HEIGHT - math.ceil(SCREEN_HEIGHT / 4)) // 2)  # 设置一个合适的初始位置

                    # 使用中文字体渲染
                    extra_surf = self.chinese_font.render(
                        self.effect_extra_text,
                        True,
                        self.effect_indicator_color  # 使用设置的颜色
                    )

                    # 在适当的位置绘制文本
                    pos_extra = (pos_effect[0], pos_effect[1] + 30)
                    self.screen.blit(extra_surf, pos_extra)

            if self.game_over:
                # 计算透明度：0 -> 1 -> 1 -> 0，修改成逐步变化
                cycle_time = 2000  # 透明度变化周期为2000ms
                elapsed_time = pygame.time.get_ticks() % (cycle_time * 2)  # 总周期为2倍的变化周期
                if elapsed_time < cycle_time:
                    alpha = int((elapsed_time / cycle_time) * 255)  # 从0到255
                else:
                    alpha = int(((2 * cycle_time - elapsed_time) / cycle_time) * 255)  # 从255回到0

                # 生成一个全透明覆盖图，冻结操作
                freeze_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                freeze_surface.fill((0, 0, 0, 0))  # 完全透明
                self.screen.blit(freeze_surface, (0, 0))

                popup_width = 1185
                popup_height = 495
                popup_x = (SCREEN_WIDTH - popup_width) // 2
                popup_y = (SCREEN_HEIGHT - popup_height) // 2
                popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

                # 绘制半透明背景
                s = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
                s.fill((50, 50, 50, 0))  # 半透明灰黑色 (Alpha 值为 200)
                self.screen.blit(s, (popup_x, popup_y))

                # 绘制结算图片（动态透明度）
                if self.result_image_path:
                    result_image = pygame.image.load(self.result_image_path).convert_alpha()
                    result_image = pygame.transform.scale(result_image, (popup_width, popup_height))
                    result_image.set_alpha(alpha)  # 动态设置透明度
                    result_image_rect = result_image.get_rect(center=popup_rect.center)
                    self.screen.blit(result_image, result_image_rect.topleft)

            if self.is_dealing_animation:
                # 创建半透明遮罩层（尺寸2502×446，实际根据屏幕调整）
                overlay = pygame.Surface((SCREEN_WIDTH, 446), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 0))  # 75%透明度的黑色
                self.screen.blit(overlay, (0, SCREEN_HEIGHT - 446))

                # 添加等待文字
                wait_font = pygame.font.SysFont("simhei", 72, bold=True)
                wait_text = wait_font.render("······少侠莫着急······", True, (168, 255, 127))
                text_rect = wait_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 446 // 2))
                self.screen.blit(wait_text, text_rect)

                # 修改弹窗绘制逻辑
            if self.popup_message and pygame.time.get_ticks() - self.popup_start_time < self.popup_duration + 2250:
                popup_width = 1185
                popup_height = 495
                popup_x = (SCREEN_WIDTH - popup_width) // 2
                popup_y = (SCREEN_HEIGHT - popup_height) // 2

                # 绘制半透明背景
                s = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
                s.fill((50, 50, 50, 200))
                self.screen.blit(s, (popup_x, popup_y))

                # 优先绘制图片提示
                if self.popup_image is not None:  # 修改判断条件
                    self.screen.blit(self.popup_image, (popup_x, popup_y))
                else:
                    # 后备文字提示
                    font = pygame.font.SysFont("simhei", 64, bold=True)
                    text_surf = font.render(self.popup_message, True, self.popup_color)
                    text_rect = text_surf.get_rect(center=(popup_x + popup_width // 2, popup_y + popup_height // 2))
                    self.screen.blit(text_surf, text_rect)
            button_color = (150, 27, 74) if self.is_help_hovered else (150, 27, 74)
            pygame.draw.rect(self.screen, button_color, self.help_button_rect)
            # 绘制按钮文字（居中）
            text_surf = self.chinese_font.render("前世的经验", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.help_button_rect.center)
            self.screen.blit(text_surf, text_rect)

            # 如果悬停在按钮上，显示提示图片
            if self.is_help_hovered and self.help_image:
                # 在屏幕中央显示提示图片（覆盖全屏）
                self.screen.blit(self.help_image, self.help_image_rect)
            pygame.display.flip()
        # ——————————————————————————————————————————————————————————————————————————————————————————————————————————

        elif self.current_state == "ending":
            print("进入游戏结算")
            # 显示当前阶段的图片

            current_image = self.ending_images[self.ending_phase] if self.ending_phase == 1 else self.ending_image

            if current_image:
                self.screen.blit(current_image, (0, 0))

            # 添加操作提示文字

            prompt_font = self.chinese_font

            prompt_text1 = prompt_font.render("点击切换画面 | 按Q键退出", True, (255, 215, 0))  # 金色

            prompt_rect1 = prompt_text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))

            prompt_text2 = prompt_font.render("制作人员名单", True, (255, 105, 180)) if self.ending_phase == 1 else prompt_font.render("战斗结算画面", True, (135, 206, 250))  # 不同状态不同颜色
            prompt_rect2 = prompt_text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))

            self.screen.blit(prompt_text1, prompt_rect1)
            self.screen.blit(prompt_text2, prompt_rect2)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(720)
        pygame.quit()



if __name__ == "__main__":
    icon_path = resource_path("./fire_and_water/1.ico")
    icon_surface = pygame.image.load(icon_path)
    pygame.display.set_icon(icon_surface)

    pygame.init()
    pygame.mixer.init()
    # 加载自定义图标

    icon_path = resource_path("./fire_and_water/1.ico")
    icon_surface = pygame.image.load(icon_path)
    pygame.display.set_icon(icon_surface)

    temp_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    for key, path in image_path_mapping.items():
        try:
            preloaded_images[key] = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Failed to preload {path}: {e}")
            preloaded_images[key] = None
    try:
        computer_image = pygame.image.load(COMPUTER_IMAGE_PATH).convert_alpha()
    except Exception as e:
        print(f"Failed to preload computer image: {e}")
        computer_image = None
    try:
        preloaded_images["background"] = pygame.image.load(image_path_mapping["background"]).convert_alpha()
    except Exception as e:
        print(f"Failed to preload background image: {e}")
        preloaded_images["background"] = None
    pygame.display.quit()
    game = PVEGame()
    icon_path = resource_path("./fire_and_water/1.ico")
    icon_surface = pygame.image.load(icon_path)
    pygame.display.set_icon(icon_surface)
    game.pending_extra_moves_for_player = 0
    game.pending_extra_moves_for_computer = 0
    icon_path = resource_path("./fire_and_water/1.ico")
    icon_surface = pygame.image.load(icon_path)
    pygame.display.set_icon(icon_surface)
    game.run()
    icon_path = resource_path("./fire_and_water/1.ico")
    icon_surface = pygame.image.load(icon_path)
    pygame.display.set_icon(icon_surface)
