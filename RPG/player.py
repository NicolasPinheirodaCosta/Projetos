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
                "xp_req": informations.get("xp_req", 100),
                "xp_earn": informations.get("xp_earn", 0)}
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

    # -------------------- sistema de pontos (leitura) ---------------------

    @property
    def points_earn(self):
        return self.__points_earn
 
    def spend_point(self, stat, amount=1):  # gasta pontos em um atributo
        path = self.stat_path.get(stat)
        if path is None:
            raise ValueError(f"Atributo inválido: {stat}")
 
        if amount < 1 or amount > self.__points_earn:  # quantidade válida e disponível?
            return False

        target = self.stats_points
        for key in path[:-1]:  # desce nos dicionários intermediários
            target = target[key]
 
        target[path[-1]] += amount  # adiciona os pontos ao atributo
        self.__points_earn -= amount  # desconta do saldo
        return True

    # -------------------- sistema de nivel ---------------------
    
    def gain_experience(self, amount):  # registra ganho de xp e vê se sobe de lvl
        exp = self.information["experience"]
        exp["gained_xp"] = amount
        exp["xp"] += amount
 
        return self.level_up()
 
    def level_up(self):  # sobe de nível e concede pontos
        exp = self.information["experience"]
        points_gained = 0
 
        while exp["xp"] >= exp["xp_req"] and self.information["level"] < self.max_level:
            exp["xp"] -= exp["xp_req"]  # (antes estava "req_xp", chave inexistente)
            exp["xp_req"] = int(exp["xp_req"] * 1.5)
 
            self.information["level"] += 1
            points_gained += self.__points_per_level
 
        self.__points_earn += points_gained
        return self.information["level"], points_gained
 
    def level_cap(self):  # limita o nível entre mínimo e máximo
        self.information["level"] = min(
            max(self.information["level"], self.min_level), self.max_level
        )

        return self.information["level"]

    # -------------------- sistema de atributos ---------------------

    def __compute_attributes(self, base, points, value):  # base + (pontos * valor)
        result = {}
 
        for stat, base_value in base.items():
            if isinstance(base_value, dict):  # attack/defense/combat descem um nível
                result[stat] = self.__compute_attributes(
                    base_value, points.get(stat, {}), value.get(stat, {})
                )
            else:
                result[stat] = base_value + points.get(stat, 0) * value.get(stat, 0)
    
        return result
 
    def calculate_attribute(self):  # calcula os atributos finais
        final = self.__compute_attributes(
            self.base_stats, self.stats_points, self.points_value
        )
        # precisão fica sempre entre min_precision e max_precision
        final["combat"]["precision"] = self.precision_cap(final["combat"]["precision"])
 
        self.__final_stats = final
        return final

    # -------------------- sistema de esquiva ---------------------

    def hit_cap (self, value):
        return min(max(value, self.min_hit_chance), self.max_hit_chance)
    
    def dodge_cap (self,value):
        return min(max(value, self.min_dodge), self.max_dodge)

    def precision_cap (self, value): #limita precisão de 0~100
        return min(max(value, self.min_precision), self.max_precision)

    def avoid (self, attacker):
        mine = self.calculate_attribute()["combat"]
        prc = attacker.calculate_attribute()["combat"]["precision"]

        evasion = mine["dodge"] * mine["reaction"] / self.evasion_scale
        hit_chance = self.hit_cap(self.base_hit_chance + (prc - evasion))
        avoid_chance = 100 - hit_chance

        if rd.uniform(0, 100) < avoid_chance:
            return 0  # desviou
        return 1  # não desviou

    # -------------------- sistema de combate ---------------------

    def calculate_damage(self, target, power=40, damage_type="phy", crit_chance=0.1):
        my_attack = self.calculate_attribute()["attack"]
        his_defense = target.calculate_attribute()["defense"]

        attack = {"phy": my_attack["physical"], "mag": my_attack["magical"]}
        defense = {"phy": his_defense["physical"], "mag": his_defense["magical"]}

        if damage_type not in attack:  # valida antes do sorteio do desvio
            raise ValueError(f"Tipo de dano inválido: {damage_type}")

        if target.avoid(self) == 0:  # alvo desviou: nem calcula o dano
            return 0

        level = self.information["level"]
        base = ((2 * level / 5 + 2) * power * attack[damage_type]
                / max(defense[damage_type], 1)) / 50 + 2  # max(...,1) evita divisão por zero

        modifier = rd.uniform(self.min_random, self.max_random)
        if rd.random() < crit_chance:  # crítico
            modifier *= self.crit_multiplier

        return max(1, int(base * modifier))

    def take_damage (self, damage):
        if damage < 0:
            raise ValueError("O dano não pode ser negativo.")

        self.current_hp = max(0, self.current_hp - damage)

        if self.current_hp == 0:
            return False  # Jogador derrotado

        return True 
        
    def first_attack(self, other):  # retorna quem ataca primeiro (self ou other)
        # velocity agora fica em combat (antes: base_stats["vel"])
            vel_you = self.calculate_attribute()["combat"]["velocity"]
            vel_him = other.calculate_attribute()["combat"]["velocity"]
 
            if vel_you > vel_him:
                return self
            elif vel_you < vel_him:
                return other
            else:
                return rd.choice([self, other])