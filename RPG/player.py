import random as rd

class player:
    min_level = 1  #nivel minimo, começa nele
    max_level = 50 #nivel maximo
    min_precision = 0    #precisão minima
    max_precision = 100  #precisão máxima
    __points_per_level = 3 #pontos ganhos pelo jogador

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
            "hp": stats_points.get("hp", 0), #zerissima de hp
            "mana": stats_points.get("mana", 0), #zerissima de mana
            "atk": {
                "phy": stats_points.get("phy_atk", 0), #zerissima de ataque fisico
                "mag": stats_points.get["mag_atk", 0]}, #zerissima de ataque magico
            "def": {
                "phy": stats_points.get["phy_def", 0], #zerissima de defesa fisica
                "mag": stats_points.get["mag_def", 0]} #zerissima de defesa magica
        }

        self.points_value = {
            "hp": 2, #ponto ganho por upar hp
            "mana": 3, #ponto ganho por upar mana
            "atk": {
                "phy_atk": float, #ponto ganho por upar ataque fisico
                "mag_atk": float}, #ponto ganho por upar ataque magico
            "def": {
                "phy_def": float, #ponto ganho por upar defesa fisica
                "mag_def": float} #ponto ganho por upar defesa magica
        } #valor dos pontos por raça

        self.__points_earn = 0  # pontos disponíveis para gastar

    # -------------------- sistema de pontos (leitura) ---------------------

    @property
    def points_earn(self):
        return self.__points_earn

    def spend_point(self, stat, amount=1): #administrador de pontos gastos em atributos
        if amount < 1 or amount > self.__points_earn: #verifica se quantidade é valida e disponivel
            return False #cancela operação se não tiver ponto para distribuir em atributos

        key_attribute = self.stats_points #cria referencia ao dicionario de pontos dos atributos
        keys = stat.split("_") #separa nome dos atributos em chaves para acessar dicionarios internos

        if keys[-1] in ("atk", "def"): #verifica se o último elemento corresponde a um tipo de atributo
            keys.reverse() # inverte a ordem das chaves para corresponder à estrutura dos dicionários

        for key in keys[:-1]:  #percorre as chaves intermediárias para localizar o atributo desejado
            if isinstance(key_attribute, dict) and key in key_attribute: #verifica se a estrutura é um dicionário e contém a chave
                key_attribute = key_attribute[key] #avança para o próximo nível do dicionário
            else:
                raise ValueError(f"Atributo inválido: {stat}") # informa que o atributo solicitado não existe

        last_key = keys[-1] #identifica a chave final do atributo que receberá os pontos
 
        if last_key not in key_attribute or not isinstance(key_attribute[last_key], int): # verifica se a chave existe e possui um valor inteiro
            raise ValueError(f"Atributo inválido: {stat}") #impede a distribuição em um atributo inválido
    
        key_attribute[last_key] += amount #adiciona os pontos ao atributo selecionado
        self.__points_earn -= amount #desconta os pontos utilizados do saldo disponível
        return True # confirma que distribuição foi feita

    # -------------------- sistema de nivel ---------------------
    
    def gain_experience(self, amount): #registra ganho de xp | vê se jogador pode upar de lvl
        exp = self.information["experience"] #atalho para dict de experiencia
        exp["gained_xp"] = amount # registra quanto de xp ganhou
        exp["xp"] += amount # torna quanto xp ganhou para xp atual

        return self.level_up() #chama level_up para ver se upou de nivel
    
    def level_up (self): #ve se o jogador pode subir de nivel e da pontos por subir de nivel
        exp = self.information["experience"] #encurtador para dicionario de experiencia
        points_gained = 0 #inicia contador de pontos obtidos com a evolução

        while (exp["xp"] >= exp["xp_req"]) and self.information["level"] < self.max_level: #verifica se tem xp suficiente para upar
            exp["xp"] -= exp["req_xp"] #desconta o xp do jogador pelo tanto que precisa upar
            exp["xp_req"] = int(exp["xp_req"] * 1.5) #aumenta quantidade necessaria para upar

            self.information["level"] += 1 #aumenta o nivel
            points_gained += self.__points_per_level #ganha pontos

        self.__points_earn += points_gained #adiciona os pontos em saldo disponivel para distribuição
        return self.information["level"], points_gained #retorna nivel atual e pontos ganhos pelo jogador

    def level_cap (self): #teto de nivel máximo e minimo
        self.information["level"] = min(max(self.information["level"], self.min_level), self.max_level) #restritor de nivel

        return self.information["level"] #retorna o nivel atual do player

    # -------------------- sistema de atributos ---------------------

    def __compute_attributes(self, base, points, value):  # percorre a estrutura: base + (pontos * value)
        result = {}

        for stat, base_value in base.items():
            if isinstance(base_value, dict):  # atk/def desce um nível
                result[stat] = self.__compute_attributes(
                    base_value, points.get(stat, {}), value.get(stat, {})
                )
            else:
                result[stat] = base_value + points.get(stat, 0) * value.get(stat, 0)

        return result

    def calculate_attribute (self): #calcula o atributo
        self.__final_stats = self.__compute_attributes(
        self.base_stats, self.stats_points, self.points_value
    )
        return self.__final_stats

    # -------------------- sistema de combate ---------------------

    def precision_cap (self, value): #limita precisão de 0~100
         return min(max(value, self.min_precision), self.max_precision)

    def calculate_damage (self, target, power=40, damage_type ="phy", crit_chance = 0.1): #valor do dano
       pass
        
    def first_attack(self, vel_you, vel_him): #quem ataca primeiro
        vel_you = vel_you.base_stats["vel"]
        vel_him = vel_him.base_stats["vel"]

        if vel_you > vel_him: #se velocidade maior, retorna verdadeiro que voce ataque
            return vel_you
        elif vel_you < vel_him: #se menor, quem ataca é o outro
            return vel_him
        else:
            return rd.choice([vel_you, vel_him]) #aleatoriedade de quem ataca primeiro quando velocidade são ==