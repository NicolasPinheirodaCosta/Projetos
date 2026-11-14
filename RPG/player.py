import random as rd

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

    # -------------------- combate ---------------------
    def combat (self, enemy): #sistema de combate
        you_agility = self.base_stats["resources"]["combat"]["agility"] #agilidade do jogador
        enemy_agility = enemy.base_stats["resources"]["combat"]["agility"] #agilidade do inimigo

        evasion = self.base_stats["resources"]["combat"]["evasion"] #evasão
        reaction = self.base_stats["resources"]["combat"]["reaction"] #reação
        precision = self.base_stats["resources"]["combat"]["precision"] #precisão

        crit_multiplier, crit_chance = 1.5, 0.1 #multiplicador de critico e chance de critico
        my_attack = self.base_stats["attack"] #ataque
        his_defense = enemy.base_stats["defense"] #defesa

        current_life = self.base_stats["resources"]["health"]["current"]
        maximum_life = self.base_stats["resources"]["health"]["maximum"]

        turncount = 0

        def first_attack (): #quem ataca primeiro  
            if you_agility > enemy_agility:
                return True #True se player tiver agility mais alta que inimigo, ataca primeiro
            elif you_agility < enemy_agility:
                return False #se inimigo tiver agilidade maior, falso, ele ataca primeiro
            else:
                return rd.choice([True, False]) #50/50 entre escolha caso seja igual

        def avoid(): #mecanica de desviar
            dodge_chance = min(self.evasion_scale,(evasion * reaction) / self.evasion_scale) #formula de desvio

            return rd.random() * 100 > (100 - dodge_chance) #chance de desvio

        def accuracy(): #mecanica de precisão
            hit_chance = max(self.min_hit_chance, min(self.max_hit_chance, precision)) #formula de acerto

            return rd.random() * 100 < hit_chance #chance de acerto

        def damage(damage_type="phy", power=100): #calculadora de dano
            final_damage = 0

            if damage_type == "phy":
                final_damage = (my_attack["physical"] * power / 100) - his_defense["physical"]

            elif damage_type == "mag":
                final_damage = (my_attack["magical"] * power / 100) - his_defense["magical"]

            final_damage = max(0, final_damage) #evita dano negativo (defesa maior que ataque)

            if rd.random() < crit_chance: #10% de chance de critico
                final_damage *= crit_multiplier #1.5x = 50% a mais de dano

            return final_damage #dano final causado

        def health_bar(target): #barra de vida
            percent_life = (current_life/maximum_life) * 100

            if current_life <= 0:
                return "defeated"

            return f"HP: {current_life}/{maximum_life} | ({percent_life:.1f}%)"

        def damage_take(damage):
            nonlocal current_life

            current_life = max(0, current_life - damage)

            return current_life

        def actions (): #ações tomadas
            player_act = None
            enemy_act = None

            if player_act and enemy_act:
                pass

        def turnos (): #contabilidade de turnos
            nonlocal turncount

            turncount += 1

            return turncount