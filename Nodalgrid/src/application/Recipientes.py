from abc import ABC, abstractmethod
from typing import Any

# =====================================================================
# 1. FAMÍLIA DO AÇO E CONCRETO (Infraestrutura Passiva / Objetos Físicos)
# =====================================================================
class RecipienteFisico(ABC):
    """Classe base agnóstica para qualquer estrutura estática. Não impõe unidade de medida."""
    def __init__(self, id_recipiente: str, capacidade_maxima: float):
        self.id_recipiente = id_recipiente
        self.capacidade_maxima = capacidade_maxima
        self.ocupacao_atual = 0.0  # Pode ser quilos, litros ou unidades inteiras
        
    @abstractmethod
    def exibir_status(self) -> dict:
        pass

class RecipienteMovel(RecipienteFisico, ABC):
    """Classe base para qualquer estrutura móvel (Caminhão, Vagão)."""
    def __init__(self, id_recipiente: str, capacidade_maxima: float):
        super().__init__(id_recipiente, capacidade_maxima)

class RecipienteEstacionario(RecipienteFisico, ABC):
    """Classe base para qualquer estrutura fixa (Silo, Armazém)."""
    def __init__(self, id_recipiente: str, capacidade_maxima: float):
        super().__init__(id_recipiente, capacidade_maxima)
    

# =====================================================================
# 2. COMPORTAMENTO PARA RECIPIENTES DE VOLUME/KG (Silo, Caminhão Graneleiro)
# =====================================================================
class ArmazenamentoContinuo:
    """Gerencia o armazenamento de pesos contínuos (floats) e impede transbordamento."""
    def armazenar(self, lote_granel) -> None:
        if self.ocupacao_atual + lote_granel.peso_atual > self.capacidade_maxima:
            raise ValueError(f"Recipiente {self.id_recipiente} estourou a capacidade máxima de KG!")
        
        self.ocupacao_atual += lote_granel.peso_atual
        self.historico_lotes.append(lote_granel.id_lote)

class CarregamentoContinuo:
    """Injeta a lógica de movimentação de fluidos/massas baseada em peso (float)."""
    def carregar(self, lote_origem, peso_a_movimentar: float) -> Any:
        if peso_a_movimentar <= 0:
            raise ValueError("A quantidade a ser carregada deve ser maior que zero.")
            
        lote_extraido = lote_origem.fracionar(peso_a_movimentar, self.id_recipiente)
        self.armazenar(lote_extraido)
        return lote_extraido

    def descarregar(self, lote_contido, peso_a_remover: float, entidade_destino: Any) -> None:
        if peso_a_remover > lote_contido.peso_atual:
            raise ValueError("Tentativa de descarregar volume maior do que o contido no veículo.")
            
        self.ocupacao_atual -= peso_a_remover
        lote_contido.peso_atual -= peso_a_remover
        
        # Duck Typing: O recipiente não precisa importar a Entidade para saber 
        # que ela tem o método receber_carga. Ele confia que o objeto passado o tem.
        entidade_destino.receber_carga(lote_contido)


# =====================================================================
# 3. COMPORTAMENTO PARA RECIPIENTES DISCRETOS (Curral, Caminhão Boiadeiro)
# =====================================================================
class ArmazenamentoDiscreto:
    """Gerencia o armazenamento de unidades indivisíveis (ints) e impede superlotação."""
    def armazenar(self, lote_discreto) -> None:
        if self.ocupacao_atual + lote_discreto.quantidade_unidades > self.capacidade_maxima:
            raise ValueError(f"Recipiente {self.id_recipiente} estourou a capacidade máxima de UNIDADES!")
        
        self.ocupacao_atual += lote_discreto.quantidade_unidades
        
        if not hasattr(self, 'lotes_armazenados'):
            self.lotes_armazenados = []
        self.lotes_armazenados.append(lote_discreto.id_lote)

class CarregamentoDiscreto:
    """Injeta a lógica de movimentação de unidades indivisíveis (List de objetos)."""
    def carregar(self, lote_origem, ids_unidades: list) -> Any:
        if not ids_unidades:
            raise ValueError("Selecione pelo menos uma unidade (Boi/Tora) para carregar.")
            
        lote_extraido = lote_origem.desmembrar_lote(ids_unidades, self.id_recipiente)
        self.armazenar(lote_extraido)
        return lote_extraido

    def descarregar(self, lote_contido, ids_unidades: list, entidade_destino: Any) -> None:
        lote_descarregado = lote_contido.desmembrar_lote(ids_unidades, entidade_destino.nome_razao_social)
        self.ocupacao_atual -= len(ids_unidades)
        entidade_destino.receber_carga(lote_descarregado)
    
# =====================================================================
# 4. CLASSES CONCRETAS (Os Objetos Físicos Reais)
# =====================================================================
class Silo(RecipienteEstacionario, CarregamentoContinuo, ArmazenamentoContinuo):
    """Infraestrutura para Granéis (Soja, Milho). Trabalha com peso contínuo (float)."""
    def __init__(self, id_recipiente: str, capacidade_maxima_kg: float):
        super().__init__(id_recipiente, capacidade_maxima_kg)
        self.historico_lotes = [] 

    def exibir_status(self) -> dict:
        return {
            "silo_id": self.id_recipiente,
            "capacidade_kg": self.capacidade_maxima,
            "ocupacao_kg": self.ocupacao_atual,
            "lotes_misturados": len(self.historico_lotes)
        }

class Armazem(RecipienteEstacionario, CarregamentoDiscreto, ArmazenamentoDiscreto):
    """Infraestrutura para Discretos (Boi, Madeira). Trabalha com contagem unitária (int)."""
    def __init__(self, id_recipiente: str, capacidade_maxima_unidades: int):
        super().__init__(id_recipiente, capacidade_maxima_unidades)
        self.lotes_armazenados = [] 

    def exibir_status(self) -> dict:
        return {
            "armazem_id": self.id_recipiente,
            "capacidade_unidades": int(self.capacidade_maxima),
            "ocupacao_unidades": int(self.ocupacao_atual),
            "qtd_lotes_guardados": len(self.lotes_armazenados)
        }

class CaminhaoContinuo(RecipienteMovel, CarregamentoContinuo):
    """Infraestrutura móvel para transporte de Continuos (Areia, Pedra)."""
    def __init__(self, id_recipiente: str, capacidade_maxima_kg: float):
        super().__init__(id_recipiente, capacidade_maxima_kg)
        self.lotes_transportados = []

    def exibir_status(self) -> dict:
        return {
            "caminhao_id": self.id_recipiente,
            "capacidade_kg": self.capacidade_maxima,
            "ocupacao_kg": self.ocupacao_atual,
            "lotes_transportados": len(self.lotes_transportados)
        }

class CaminhaoDiscreto(RecipienteMovel, CarregamentoDiscreto):
    """Infraestrutura móvel para transporte de Discretos (Boi, Madeira)."""
    def __init__(self, id_recipiente: str, capacidade_maxima_unidades: int):
        super().__init__(id_recipiente, capacidade_maxima_unidades)
        self.lotes_transportados = []

    def exibir_status(self) -> dict:
        return {
            "caminhao_id": self.id_recipiente,
            "capacidade_unidades": int(self.capacidade_maxima),
            "ocupacao_unidades": int(self.ocupacao_atual),
            "qtd_lotes_transportados": len(self.lotes_transportados)
        }