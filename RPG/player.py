import random as rd
import time as tm

class Player:
    min_level, max_level = 1, 50 #nivel minimo/maximo
    min_precision, max_precision = 0, 100 #precisão minima/máxima

    min_dodge, max_dodge = 0, 100 #esquiva minima/máxima
    min_hit_chance, max_hit_chance = 5, 95 #chance de acerto minimo/máxima



    evasion_scale = 100 #escala de evasão

    __progression_point, __max_points = 3, 3 * max_level #ponto de progressão | limite de pontos máximo

    stats_path = {"hit_points": ("resources", "health", "maximum"),
    "mana": ("resources", "mana", "maximum"),
    "phy_atk": ("attack", "physical"),
    "mag_atk": ("attack", "magical"),
    "phy_def": ("defense", "physical"),
    "mag_def": ("defense", "magical")} #caminho para os atributos
    
    def __init__ (self, informations, base_stats, stats_points):
        self.informations = {
            "identity": {
                "name": informations["name"],
                "gender": informations["gender"],
                "race": informations["race"],
                "category": informations["category"],
                "class": informations["class"]}, #identidade do personagem
                
            "experience": {
                "level": informations.get("level", 1),
                "xp": informations.get("xp", 0),
                "xp_req": informations.get("xp_req", self.xp_required(informations.get("level", 1))),
                "xp_earn": informations.get("xp_earn", 0)},

            "resources": {
                "money": informations.get("money", 0),
                "reset_token": informations.get("reset_token", 0)}
            } #informações de experiencia e nivel

        self.base_stats = {
            "resources": {
                "health": {
                    "current": base_stats["c_hp"],
                    "maximum": base_stats["m_hp"]}, #informações de hp
                "mana": {
                    "current": base_stats["c_mana"],
                    "maximum": base_stats["m_mana"],
                    "regeneration": base_stats["r_mana"]} #informações de mana
                }, #recursos    
            "attack": {
                "physical": base_stats["phy_atk"],
                "magical": base_stats["mag_atk"]}, #tipos de ataque
            "defense": {
                "physical": base_stats["phy_def"],
                "magical": base_stats["mag_def"]}, #tipos de defesa
            "combat": {
                "precision": base_stats["prc"],
                "evasion": base_stats["eva"],
                "agility": base_stats["agl"],
                "reaction": base_stats["rct"]} #informações de combate
            } #informações base de status

        self.stats_points = {stat: stats_points.get(stat, 0) for stat in self.stats_path}

        self.__points_earn = 0  # pontos disponíveis para gastar

# -------------------- sistema de nivel ---------------------


    def xp_required (self, level): #xp necessário para sair do nivel informado
        return round(100 * level * 1.5)

    def can_level_up (self): #True se o jogador ainda não chegou no nivel máximo
        return self.min_level <= self.informations["experience"]["level"] < self.max_level

    def level_up (self): #upar level
        xp = self.informations["experience"]
        xp["level"] += 1
        xp["xp_req"] = self.xp_required(xp["level"])
        self.earn_points()
        return True

    def gain_xp (self, amount): #conta quanto de xp foi ganho
        if amount <= 0 or not self.can_level_up():
            return False

        xp = self.informations["experience"]
        xp["xp"] += amount ; xp["xp_earn"] += amount

        while xp["xp"] >= xp["xp_req"] and self.can_level_up():
            xp["xp"] -= xp["xp_req"]
            self.level_up()

        if not self.can_level_up(): #nivel máximo: descarta o xp restante
            xp["xp"] = 0
        return True

# -------------------- manejamento de pontos ---------------------

    def __total_points(self): #pontos totais acumulados pelo jogador
        return sum(self.stats_points.values()) + self.__points_earn

    def points_cap (self): #limite máximo para pontos
        total = self.__total_points()
        return max(0, self.__max_points - total)

    def earn_points(self): #pontos ganhos pela progressão do player
        available = self.points_cap()
        if available <= 0:
            return 0

        gained = min(self.__progression_point, available)
        self.__points_earn += gained
        return gained

    def spend_points(self, stat, amount = 1): #gasta pontos em atributos
        if stat not in self.stats_path or amount <= 0:
            return False

        if amount > self.__points_earn:
            return False

        self.stats_points[stat] += amount
        self.__points_earn -= amount
        return True
    
    def exchange_points (self): #converte valor de pontos gastos
        rates = {"hit_points": 2,
        "mana": 3,
       "phy_atk": 1,
        "mag_atk": 1,
        "phy_def": 1,
        "mag_def": 1}

        return {stat: points * rates[stat] for stat, points in self.stats_points.items()}

    def reset_points(self, tokens, stats=None): #resetar pontos
        level = self.informations["experience"]["level"] #caminho de nivel
        resources =  self.informations["resources"] #caminho de recursos

        if level < self.max_level: #verificador de nivel para resetar pontos
            return False
        
        if not stats or any(s not in self.stats_path for s in stats):
            return False

        groups = {self.stats_path[s][:-1] for s in stats}
        cost = len(groups)  # 1 token por grupo
        if resources["reset_token"] < cost:
            return False

        targets = [s for s, path in self.stats_path.items() if path[:-1] in groups]
        refunded = sum(self.stats_points[s] for s in targets)
        if refunded == 0:
            return False

        resources["reset_token"] -= cost
        for s in targets:
            self.stats_points[s] = 0
        self.__points_earn += refunded  # devolução dos pontos
        return True #devolução de pontos feita

# -------------------- vida --------------------

    def life_cap(self): # gerenciamento de vida
        health = self.base_stats["resources"]["health"]

        health["current"] = max(0, min(health["current"], health["maximum"]))
        return health["current"]

    def health_bar(self): #funcionamento de barra de vida
        health = self.base_stats["resources"]["health"]
        self.life_cap()

        current = health["current"]
        maximum = health["maximum"]
        percent = current / maximum
        
        return f"HP: {current}/{maximum} | {percent:.0%}"

    def heal(self): # recuperação de vida por descanso
        health = self.base_stats["resources"]["health"]

        if not self.is_alive() or health["current"] >= health["maximum"]:
            return False

        current_time = tm.time()

        if not hasattr(self, "_last_heal"):
            self._last_heal = current_time
            return False

        if current_time - self._last_heal >= 2:
            health["current"] += health["maximum"] * 0.01
            self.life_cap()
            self._last_heal = current_time

        return True
            
    def take_damage(self, damage=0):  #validador de recebimento de dano
        if damage < 0 or not self.is_alive():
            return False
        
        health = self.base_stats["resources"]["health"]

        health["current"] -= damage
        self.life_cap()

    def is_alive(self): #verifica se player esta vivo ou morto

            if self.life_cap() <= 0:
                return False
            else:
                return True
    
# -------------------- mana ---------------------

    def mana_cap(self): #teto de gasto e uso para mana
        mana = self.base_stats["resources"]["mana"]

        mana["current"] = max(0, min(mana["current"], mana["maximum"]))
        return mana["current"]

    def use_mana(self, cost, type_attack="mag"): #gerenciamento de uso de mana
        mana = self.base_stats["resources"]["mana"]

        if type_attack != "mag":
            return False

        if mana["current"] < cost:
            return False

        mana["current"] -= cost
        self.mana_cap()
        return True

    def restore_mana(self, attack_type, cost=0): #gerenciamento de mana
        if attack_type == "mag":
            return self.use_mana(cost)

        elif attack_type == "phy":
            mana = self.base_stats["resources"]["mana"]
            restore = mana["maximum"] * 0.03

            mana["current"] += restore
            self.mana_cap()
            return True

        return False  
          
# -------------------- status ---------------------


    def can_act(self): #verifica se player pode fazer qualquer ação
        if self.is_alive():
            return True
        return False

    def inventory(self): #sistema de inventario
        pass

    def movement(self): #define em que estado de movimento está, se esta correndo ou caminhando
        pass