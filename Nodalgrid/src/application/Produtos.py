from abc import ABC, abstractmethod
import uuid
from typing import Any, List, Dict

# =====================================================================
# 1. CLASSES DE BASE (Unidades Físicas Reais)
# =====================================================================
class Boi:
    """Objeto que representa o animal no mundo físico."""
    def __init__(self, id_brinco: str, peso_kg: float, raca: str):
        self.id_brinco = id_brinco
        self.peso_kg = peso_kg
        self.raca = raca

    def __repr__(self):
        return f"Boi({self.id_brinco}, {self.peso_kg}kg)"

class ToraMadeira:
    """Objeto que representa uma tora de madeira rastreada com plaqueta."""
    def __init__(self, id_plaqueta: str, especie: str, volume_m3: float):
        self.id_plaqueta = id_plaqueta
        self.especie = especie
        self.volume_m3 = volume_m3

    def __repr__(self):
        return f"Tora({self.id_plaqueta}, {self.especie}, {self.volume_m3}m³)"


# =====================================================================
# 2. CONTRATO UNIVERSAL E CLASSES DE TAXONOMIA BIOLÓGICA
# =====================================================================
class LoteAgro(ABC):
    def __init__(self, proprietario_atual: str):
        self.id_lote = uuid.uuid4()
        self.proprietario_atual = proprietario_atual
        self.selo_procedencia = True

    @abstractmethod
    def mostrar_detalhes(self) -> str: pass

    @abstractmethod
    def obter_macro_categoria(self) -> str: pass

    def _formatar_detalhes(self, detalhes: dict) -> str:
        linhas = [f"{self.__class__.__name__}", "-" * 40]
        for chave, valor in detalhes.items():
            if isinstance(valor, list):
                linhas.append(f"{chave}:")
                for item in valor:
                    linhas.append(f"  - {item}")
            else:
                linhas.append(f"{chave}: {valor}")
        return "\n".join(linhas)

    def __str__(self) -> str:
        return self.mostrar_detalhes()

    def invalidar_selo(self) -> None:
        self.selo_procedencia = False

class ProdutoAgricola(LoteAgro, ABC):
    """Herda LoteAgro e adiciona obrigações de lavoura (Ex: CAR)."""
    def __init__(self, proprietario_atual: str, car_origem: str):
        super().__init__(proprietario_atual)
        self.car_origem = car_origem

    def obter_macro_categoria(self) -> str:
        return "PRODUTOS_AGRICOLAS"
    
    def mostrar_detalhes(self) -> str:
        detalhes = {
            "id_lote": str(self.id_lote),
            "categoria": self.obter_macro_categoria(),
            "proprietario": self.proprietario_atual,
            "car_fazenda": self.car_origem,
            "selo_procedencia": self.selo_procedencia
        }
        return self._formatar_detalhes(detalhes)

class ProdutoPecuario(LoteAgro, ABC):
    def __init__(self, proprietario_atual: str, gta_origem: str):
        super().__init__(proprietario_atual)
        self.gta_origem = gta_origem

    def obter_macro_categoria(self) -> str:
        return "PRODUTOS_PECUARIOS"
    
    def mostrar_detalhes(self) -> str:
        detalhes = {
            "id_lote": str(self.id_lote),
            "categoria": self.obter_macro_categoria(),
            "proprietario": self.proprietario_atual,
            "gta_origem": self.gta_origem,
            "selo_procedencia": self.selo_procedencia
        }
        return self._formatar_detalhes(detalhes)

class ProdutoFlorestal(LoteAgro, ABC):
    def __init__(self, proprietario_atual: str, dof_origem: str):
        super().__init__(proprietario_atual)
        self.dof_origem = dof_origem

    def obter_macro_categoria(self) -> str:
        return "PRODUTOS_FLORESTAIS"
    
    def mostrar_detalhes(self) -> str:
        detalhes = {
            "id_lote": str(self.id_lote),
            "categoria": self.obter_macro_categoria(),
            "proprietario": self.proprietario_atual,
            "dof_origem": self.dof_origem,
            "selo_procedencia": self.selo_procedencia
        }
        return self._formatar_detalhes(detalhes)


# =====================================================================
# 3. CLASSES PARA DEFINIÇÃO DE COMPORTAMENTO (HERANÇA MÚLTIPLA)
# =====================================================================

class ComportamentoGranel:
    """Injeta a física de fluidos/massas: Medido por peso contínuo."""
    def inicializar_granel(self, peso_inicial: float):
        self.peso_atual = float(peso_inicial)

    def fracionar(self, peso_extraido: float, novo_proprietario: str):
        if peso_extraido > self.peso_atual:
            raise ValueError("Erro: Tentativa de extrair mais peso do que o lote possui.")
        self.peso_atual -= peso_extraido
        return peso_extraido, novo_proprietario
    
class ComportamentoDiscreto:
    """Gerencia um dicionário de objetos físicos indivisíveis."""
    def inicializar_discreto(self, dicionario_unidades: Dict[str, Any]):
        self.unidades = dicionario_unidades  # Ex: {"BRINCO-01": objeto_boi}
        self.quantidade_unidades = len(self.unidades)

    def desmembrar_lote(self, chaves_selecionadas: List[str], novo_proprietario: str):
        unidades_extraidas = {}
        for chave in chaves_selecionadas:
            if chave not in self.unidades:
                raise ValueError(f"Erro Crítico: Unidade ID {chave} não existe neste lote.")
            # O 'pop' remove o objeto do lote original e o transfere para a extração
            unidades_extraidas[chave] = self.unidades.pop(chave)
        
        self.quantidade_unidades = len(self.unidades)
        return unidades_extraidas, novo_proprietario


# =====================================================================
# 4. CLASSES CONCRETAS (Herança Múltipla)
# =====================================================================

class LoteSoja(ProdutoAgricola, ComportamentoGranel):
    """Exemplo de Herança Múltipla: É um Produto Agrícola E é Granel."""
    def __init__(self, proprietario_atual: str, car_origem: str, peso_inicial: float):
        # Inicializa a camada biológica
        ProdutoAgricola.__init__(self, proprietario_atual, car_origem)
        # Inicializa a camada física
        ComportamentoGranel.inicializar_granel(self, peso_inicial)

    def fracionar(self, peso_extraido: float, novo_proprietario: str) -> 'LoteSoja':
        # Subtrai o peso do lote original usando o método do Mixin
        peso, prop = super().fracionar(peso_extraido, novo_proprietario)
        # Instancia e devolve o novo vagão/caminhão gerado
        novo_lote = LoteSoja(prop, self.car_origem, peso)
        novo_lote.selo_procedencia = self.selo_procedencia
        return novo_lote

    def mostrar_detalhes(self) -> dict:
        return {
            "id_lote": str(self.id_lote),
            "categoria": self.obter_macro_categoria(),
            "proprietario": self.proprietario_atual,
            "car_fazenda": self.car_origem,
            "peso_atual_kg": self.peso_atual,
            "selo_procedencia": self.selo_procedencia
        }

class LoteGado(ProdutoPecuario, ComportamentoDiscreto):
    def __init__(self, proprietario_atual: str, gta_origem: str, dict_bois: Dict[str, Boi]):
        ProdutoPecuario.__init__(self, proprietario_atual, gta_origem)
        ComportamentoDiscreto.inicializar_discreto(self, dict_bois)

    def desmembrar_lote(self, brincos_selecionados: List[str], novo_proprietario: str) -> 'LoteGado':
        bois_extraidos, prop = super().desmembrar_lote(brincos_selecionados, novo_proprietario)
        novo_lote = LoteGado(prop, self.gta_origem, bois_extraidos)
        novo_lote.selo_procedencia = self.selo_procedencia
        return novo_lote

    def mostrar_detalhes(self) -> dict:
        return {
            "id_lote": str(self.id_lote),
            "categoria": self.obter_macro_categoria(),
            "proprietario": self.proprietario_atual,
            "gta_origem": self.gta_origem,
            "qtd_cabecas": self.quantidade_unidades,
            "objetos_contidos": list(self.unidades.values())
        }

class LoteMadeira(ProdutoFlorestal, ComportamentoDiscreto):
    def __init__(self, proprietario_atual: str, dof_origem: str, dict_toras: Dict[str, ToraMadeira]):
        ProdutoFlorestal.__init__(self, proprietario_atual, dof_origem)
        ComportamentoDiscreto.inicializar_discreto(self, dict_toras)

    def desmembrar_lote(self, plaquetas_selecionadas: List[str], novo_proprietario: str) -> 'LoteMadeira':
        toras_extraidas, prop = super().desmembrar_lote(plaquetas_selecionadas, novo_proprietario)
        novo_lote = LoteMadeira(prop, self.dof_origem, toras_extraidas)
        novo_lote.selo_procedencia = self.selo_procedencia
        return novo_lote

    def mostrar_detalhes(self) -> dict:
        volume_total = sum(tora.volume_m3 for tora in self.unidades.values())
        return {
            "id_lote": str(self.id_lote),
            "categoria": self.obter_macro_categoria(),
            "proprietario": self.proprietario_atual,
            "dof_origem": self.dof_origem,
            "qtd_toras": self.quantidade_unidades,
            "volume_total_m3": round(volume_total, 2),
            "objetos_contidos": list(self.unidades.values())
        }


# =====================================================================
# ÁREA DE TESTES (Playground Físico)
# =====================================================================
if __name__ == "__main__":
    print("--- TESTE 1: COMPOSIÇÃO DE GADO ---")
    # Instanciando os objetos reais (Composição)
    boi1 = Boi("BR-901", 450.5, "Magnus")
    boi2 = Boi("BR-902", 480.0, "Angus")
    
    # Criando o lote injetando o dicionário de objetos
    rebanho = LoteGado("Fazenda X", "GTA-001", {boi1.id_brinco: boi1, boi2.id_brinco: boi2})
    print("Rebanho Original:", rebanho.mostrar_detalhes())
    
    # Frigorífico compra apenas o Boi Angus
    venda_frigorifico = rebanho.desmembrar_lote(["BR-902"], "Frigorífico JBS")
    print("\nRebanho após venda:", rebanho.mostrar_detalhes())
    print("Caminhão Frigorífico:", venda_frigorifico.mostrar_detalhes())


    print("\n--- TESTE 2: COMPOSIÇÃO DE MADEIRA (NOVA CLASSE) ---")
    # Instanciando as toras rastreadas
    tora1 = ToraMadeira("PLQ-AA01", "Mogno", 2.5)
    tora2 = ToraMadeira("PLQ-AA02", "Mogno", 3.1)
    tora3 = ToraMadeira("PLQ-BB01", "Ipê", 1.8)

    carga_madeireira = LoteMadeira(
        "Madeireira Norte", 
        "DOF-2026-X", 
        {tora1.id_plaqueta: tora1, tora2.id_plaqueta: tora2, tora3.id_plaqueta: tora3}
    )
    
    print("Lote Florestal Original:", carga_madeireira.mostrar_detalhes())
    
    # Serraria compra apenas a tora de Ipê
    venda_serraria = carga_madeireira.desmembrar_lote(["PLQ-BB01"], "Serraria Central")
    print("\nLote Exportação (Sobra):", carga_madeireira.mostrar_detalhes())
    print("Lote Mercado Interno:", venda_serraria.mostrar_detalhes())
    
    print("--- TESTE 3: LOGÍSTICA DE GRANEL (SOJA) ---")
    vagao_soja = LoteSoja(proprietario_atual="Cooperativa Passo Fundo", car_origem="CAR-RS-999", peso_inicial=40000.0)
    print(f"Lote Original: {vagao_soja.mostrar_detalhes()}")
    lote_novo_soja = vagao_soja.fracionar(peso_extraido=15000.0, novo_proprietario="Exportadora ABC")
    print(f"Lote Original após fracionamento: {vagao_soja.mostrar_detalhes()}")
    print(f"Lote Novo (Exportadora): {lote_novo_soja.mostrar_detalhes()}")