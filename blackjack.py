class Black_Jack:
    def __init__(self, cartas):
        self.cartas = cartas
        self.valor = 0
        self.ace = 0
        self.calcular_valor()

    def calcular_valor(self):
        for carta in self.cartas:
            if carta in ['J', 'Q', 'K']:
                self.valor += 10
            elif carta == 'A':
                self.ace += 1
                self.valor += 11
            else:
                self.valor += int(carta)

        while self.valor > 21 and self.ace:
            self.valor -= 10
            self.ace -= 1

    def carta_alta(self):
        return max(self.cartas, key=lambda x: 11 if x == 'A' else 10 if x in ['J', 'Q', 'K'] else int(x))

    def resultado(self):
        if self.valor > 21:
            return "Perdeu"
        elif self.valor == 21:
            return "Blackjack!"
        else:
            return f"Valor: {self.valor}"

    def mao(self):
        max_carta = self.carta_alta()
        return f"Mão: {', '.join(self.cartas)} | Carta mais alta: {max_carta} | Valor total: {self.valor}"

    def espalhar_cartas(self):
        import random
        random.shuffle(self.cartas)
        return self.cartas

    def double_down(self):
        if len(self.cartas) == 2:
            self.cartas.append(self.espalhar_cartas()[0])
            self.calcular_valor()
            return f"Nova mão: {', '.join(self.cartas)} | Valor total: {self.valor}"
        else:
            return "Não é possível dobrar a aposta após a primeira rodada."