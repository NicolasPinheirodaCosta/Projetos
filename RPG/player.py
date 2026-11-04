import random as rd

class player:
    min_level = 1  #nivel minimo, começa nele
    max_level = 50 #nivel maximo

    min_precision = 0    #precisão minima
    max_precision = 100  #precisão máxima

    min_dodge = 0 #esquiva minima
    max_dodge = 100 #esquiva maxima

    min_hit_chance = 5
    max_hit_chance = 95

    evasion_scale = 100

    __points_per_level = 3 #pontos ganhos pelo jogador

    stat_path = {
        "hit_points": ("hp",),
        "mana": ("mana",),
        "phy_atk": ("attack", "physical"),
        "mag_atk": ("attack", "magical"),
        "phy_def": ("defense", "physical"),
        "mag_def": ("defense", "magical"),
    }

    def __init__(self, information, stats, stats_points):
        self. information = {
            "name": information["name"], #nome do jogador
            "category": information["category"], #categoria do jogador: tank/melee/ranged/magic
            "classe": information["classe"], #classe do jogador: warrior/mage/shooter/assassin/mage/necro/guardian
            "race": information["race"], #raça
            "level": information["level"], #nivel do player
            "experience": {
                "xp": information.get("xp", 0), #xp total
                "xp_req": information.get("xp_req", 100), #total de xp inicial requerido para upar pro proximo lvl
                "gained_xp": information.get("gained_xp", 0)} #xp ganho
            }        

        self.base_stats = {
            "hit_points": stats["hp"], #pontos de vida
            "mana": stats["mana"], #quantia de mana
            "attack": {
                "physical": stats["phy_atk"], #ataque fisico base
                "magical": stats["mag_atk"]}, #ataque magico base
            "defense": {
                "physical": stats["phy_def"], #defesa fisica base
                "magical": stats["mag_def"]}, #defesa magica base
            "combat": {
                "precision": stats["prc"], #precisão
                "dodge": stats["dodge"], #esquiva
                "velocity": stats["vel"], #velocidade
                "reaction": stats["react"] #tempo de reação
            } #informações para combate
        } #status para combate
        
        self.stats_points = {
            "hit_points": stats_points.get("hp", 0), #zerissima de hp
            "mana": stats_points.get("mana", 0), #zerissima de mana
            "attack": {
                "physical": stats_points.get("phy_atk", 0), #zerissima de ataque fisico
                "magical": stats_points.get("mag_atk", 0)}, #zerissima de ataque magico
            "defense": {
                "physical": stats_points.get("phy_def", 0), #zerissima de defesa fisica
                "magical": stats_points.get("mag_def", 0)} #zerissima de defesa magica
        }

        self.points_value = {
            "hit_points": 2, #ponto ganho por upar hp
            "mana": 3, #ponto ganho por upar mana
            "attack": {
                "physical_attack": float, #ponto ganho por upar ataque fisico
                "magical_attack": float}, #ponto ganho por upar ataque magico
            "defense": {
                "physical_defense": float, #ponto ganho por upar defesa fisica
                "magical_defense": float} #ponto ganho por upar defesa magica
        } #valor dos pontos por raça

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