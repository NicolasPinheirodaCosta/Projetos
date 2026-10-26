import time as tm

class Ano_Letivo:
    def __init__(self, nome, periodo):
        self.nome = nome
        self.periodo = periodo

    def tempo(self):
        return tm.time()

class Notas(Ano_Letivo):
    def __init__(self, nome, periodo, nota1, nota2, nota3, nota4):
        super().__init__(nome, periodo)
        self.nota1 = nota1
        self.nota2 = nota2
        self.nota3 = nota3
        self.nota4 = nota4

    def limite_nota(self):
        self.nota = self.nota1, self.nota2, self.nota3, self.nota4
        for nota in self.nota:
            if nota < 0 or nota > 10:
                return "nota inválida"

    def media(self):
        media = (self.nota1 + self.nota2 + self.nota3 + self.nota4) / 4
        return media

    def situacao(self):
        media = self.media()
        if media >= 7:
            return "aprovado"
        elif media >=5:
            return "recuperação"
        else:
            return "reprovado"

    def visualizar(self):

        print(f"nome: {self.nome}")
        print(f"periodo: {self.periodo} nota: {self.nota1 if self.periodo == 1 else self.nota2 if self.periodo == 2 else self.nota3 if self.periodo == 3 else self.nota4}") 