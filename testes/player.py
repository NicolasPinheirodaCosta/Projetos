class player:
    min_level = 1
    max_level = 50

    def __init__(self, information, stats):
        self. information = {
            "name": information["name"], #nome do jogador
            "category": information["category"], #categoria do jogador: tank/melee/ranged/magic
            "classe": information["classe"], #classe do jogador: warrior/mage/shooter/assassin/mage/necro/guardian
            "race": information["race"], #raça
            "level": information["level"], #nivel do player
            "xp": information.get("xp", 0), #experiencia do player
            "xp_req": information.get("xp_req", 100) #experiencia necessaria para subir de nivel
        } #informações base do player

        self.base_stats = {
            "hp": stats["hp"], #pontos de vida
            "mana": stats["mana"], #quantia de mana
            "atk": stats["atk"], #dano capaz de infligir
            "prc": stats["prc"], #precisão do atacante
            "def": stats["def"], #capacidade de defender
            "vel": stats["vel"] #velocidade do player
        } #status para combate
        
        self.stats_points = {
            "hp": 0, # hp começa zerado
            "mana": 0, # mana começa 0
            "atk": 0, #atk começa com 0
            "def": 0,  #def começa com 0
        } # pontos gastos pelo jogador (começa em 0)

        self.point_value = {
                    "hp": 2, #pontos inseridos em vida
                    "mana": 3, #pontos inseridos em mana
                    "atk": 1, #pontos inseridos em ataque
                    "def": 1 #pontos inseridos em defesa
                }

    # -------------------- sobre nivel ---------------------
    
    def level_up (self): #aumento de nivel
        self.information["xp_req"] = int(self.information["xp_req"] *1.5) #aumentar xp necessario pra upar level
        self.information["level"] += 1 #aumentar nivel do player

        if self.information["xp"] >= self.information["xp_req"]: #verifica se condição de xp >= xp_req
            self.information["xp"] -= self.information["xp_req"] #subtrai o xp_req do xp atual

            self.level_up() #chama a função novamente para verificar se ainda é possível upar
            self.level_cap() #verifica se o nivel do player está dentro do limite

            self.information["level"] += 1 #aumenta o nivel do player

        return self.information["level"] #retorna o nivel atual do player

    def level_cap (self): #teto de nivel máximo e minimo
        self.information["level"] = min(max(self.information["level"], self.min_level), self.max_level) #restritor de nivel

        return self.information["level"] #retorna o nivel atual do player

    # -------------------- atributos ---------------------

    def calculate_attributes (self): #calculo dos atributos do jogador 
        final_stats = {}

        for stat, base_value in self.base_stats.items():
            points = self.stats_points.get(stat, 0)  # prc e vel não têm pontos -> 0
            multiplier = self.point_value.get(stat, 0)
            final_stats[stat] = base_value + points * multiplier

        return final_stats