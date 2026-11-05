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

    def reset_points(self): #ainda a implementar
        pass