from abc import ABC, abstractmethod
import uuid
from typing import List, Any
from enum import Enum   

from application.Recipientes import Silo, Armazem, CaminhaoContinuo, CaminhaoDiscreto

# =====================================================================
# 1. FAMÍLIA DOS CNPJs (Atores Ativos e Legais)
# =====================================================================
class EntidadeLogistica(ABC):
    """Contrato base para qualquer operador que responde legalmente na Blockchain."""
    def __init__(self, nome_razao_social: str, documento_cnpj_cpf: str, coordenadas_gps: str):
        self.id_entidade = uuid.uuid4()
        self.nome_razao_social = nome_razao_social
        self.documento_cnpj_cpf = documento_cnpj_cpf
        self.coordenadas_gps = coordenadas_gps
        
        # Atributos privados para evitar RecursionError com as propriedades
        self._silos_proprios: List[Silo] = []
        self._armazens_proprios: List[Armazem] = []
        self._caminhoes_graneleiros: List[CaminhaoContinuo] = []
        self._caminhoes_discretos: List[CaminhaoDiscreto] = []
        self._listeners = [] 

    def registrar_listener(self, listener):
        self._listeners.append(listener)

    def notificar_listeners(self, acao: str, **kwargs):
        for listener in self._listeners:
            listener.on_evento_logistico(self, acao, **kwargs)

    def assinar_bloco_blockchain(self) -> str:
        return f"ASSINATURA_{self.documento_cnpj_cpf}_{uuid.uuid4().hex[:8]}"
    
    def armazenar_em_silo(self, id_silo: str, lote) -> None:
        silo = next((s for s in self.silos if s.id_recipiente == id_silo), None)
        if not silo:
            raise ValueError(f"Silo com ID '{id_silo}' não encontrado na entidade '{self.nome_razao_social}'.")
            
        # Pega a lista de quem já está no silo ANTES da mistura ocorrer
        lotes_anteriores = [str(id_l) for id_l in silo.historico_lotes]
        
        silo.armazenar(lote)
        print(f"📦 [MUNDO FÍSICO] Lote {lote.id_lote} armazenado no Silo '{id_silo}' da entidade '{self.nome_razao_social}'.")
        
        # Emite o evento de MISTURA passando os ancestrais!
        self.notificar_listeners("ARMAZENAMENTO_MISTURA", lote=lote, id_silo=id_silo, ids_lotes_origem=lotes_anteriores)

    @abstractmethod
    def obter_papel_rede(self) -> str:
        pass
    
    @property
    def silos(self) -> List[Silo]:
        return self._silos_proprios
        
    @property
    def armazens(self) -> List[Armazem]:
        return self._armazens_proprios
    
    @property
    def caminhoes_graneleiros(self) -> List[CaminhaoContinuo]:
        return self._caminhoes_graneleiros
        
    @property
    def caminhoes_discretos(self) -> List[CaminhaoDiscreto]:
        return self._caminhoes_discretos
    
    def criar_silo(self, id_silo: str, capacidade_toneladas: float) -> Silo:
        novo_silo = Silo(id_silo, capacidade_toneladas * 1000)
        self._silos_proprios.append(novo_silo)
        return novo_silo
    
    def criar_armazem(self, id_armazem: str, capacidade_unitario: int) -> Armazem:
        novo_armazem = Armazem(id_armazem, capacidade_unitario)
        self._armazens_proprios.append(novo_armazem)
        return novo_armazem

    def criar_caminhao_continuo(self, id_caminhao: str, capacidad_toneladas: float) -> CaminhaoContinuo:
        novo_caminhao = CaminhaoContinuo(id_caminhao, capacidad_toneladas * 1000)
        self._caminhoes_graneleiros.append(novo_caminhao)
        return novo_caminhao

    def criar_caminhao_discreto(self, id_caminhao: str, capacidade_unitarios: int) -> CaminhaoDiscreto:
        novo_caminhao = CaminhaoDiscreto(id_caminhao, capacidade_unitarios)
        self._caminhoes_discretos.append(novo_caminhao)
        return novo_caminhao


# =====================================================================
# 2. PAPÉIS COMPORTAMENTAIS
# =====================================================================
class EntidadeCriadora(EntidadeLogistica, ABC):
    @abstractmethod
    def gerar_lote(self, *args, **kwargs):
        pass

class EntidadeIntermediária(EntidadeLogistica, ABC):
    @abstractmethod
    def transferir_carga(self, lote, destino) -> None:
        pass
    @abstractmethod
    def receber_carga(self, lote, index_silo: int = 0) -> None:
        pass

class EntidadeTransformadora(EntidadeLogistica, ABC):
    @abstractmethod
    def processar_lote(self, lote) -> Any:
        pass
    @abstractmethod
    def transferir_carga(self, lote, destino) -> None:
        pass
    @abstractmethod
    def receber_carga(self, lote, index_silo: int = 0) -> None:
        pass
    
class EntidadeFinalizadora(EntidadeLogistica, ABC):
    @abstractmethod
    def finalizar_lote(self, lote) -> None:
        pass

# =====================================================================
# 3. CLASSES CONCRETAS
# =====================================================================
class Fazenda(EntidadeCriadora):
    """Entidade Gênesis. Possui o CAR e invoca a criação de Lotes."""
    def __init__(self, nome: str, cnpj: str, gps: str, car_registro: str):
        super().__init__(nome, cnpj, gps)
        self.car_registro = car_registro

    def obter_papel_rede(self) -> str:
        return "CRIADOR_GENESIS"

    def colher(self, classe_produto, peso_kg: float):
        novo_lote = classe_produto(
            proprietario_atual=self.nome_razao_social, 
            car_origem=self.car_registro, 
            peso_inicial=peso_kg
        )
        print(f"🌾 [MUNDO FÍSICO] Fazenda '{self.nome_razao_social}' colheu {peso_kg}kg.")
        self.notificar_listeners("COLHEITA", lote=novo_lote)
        return novo_lote    
        
    def gerar_lote(self, classe_produto, peso_kg: float):
        self.colher(classe_produto, peso_kg)


class Cooperativa(EntidadeIntermediária):
    """Operador Logístico Intermediário. Agrupa silos gigantes para balanço de massa."""
    def __init__(self, nome: str, cnpj: str, gps: str):
        super().__init__(nome, cnpj, gps)

    def obter_papel_rede(self) -> str:
        return "CUSTODIANTE_INTERMEDIARIO"

    def receber_carga(self, lote, index_silo: int = 0) -> None:
        if not self.silos:
            raise RuntimeError(f"A Cooperativa {self.nome_razao_social} não possui silos construídos.")
            
        silo_alvo = self.silos[index_silo]
        lotes_anteriores = [str(id_l) for id_l in silo_alvo.historico_lotes]
        
        print(f"🚛 [MUNDO FÍSICO] Cooperativa '{self.nome_razao_social}' recebeu o lote {lote.id_lote}.")
        
        lote.proprietario_atual = self.nome_razao_social
        silo_alvo.armazenar(lote)
        
        self.notificar_listeners("ARMAZENAMENTO_MISTURA", lote=lote, id_silo=silo_alvo.id_recipiente, ids_lotes_origem=lotes_anteriores)
    
    def transferir_carga(self, lote, destino) -> None:
        lote.proprietario_atual = destino.nome_razao_social
        print(f"🚛 [MUNDO FÍSICO] Cooperativa '{self.nome_razao_social}' transferiu o lote {lote.id_lote} para '{destino.nome_razao_social}'.")
        self.notificar_listeners("TRANSFERENCIA", lote=lote, destino=destino)


class Transportadora(EntidadeIntermediária):
    """Operador Logístico Intermediário. Transporta lotes entre silos e armazéns."""
    def __init__(self, nome: str, cnpj: str, gps: str):
        super().__init__(nome, cnpj, gps)
        
    def obter_papel_rede(self) -> str:
        return "CUSTODIANTE_INTERMEDIARIO"

    def receber_carga(self, lote, index_silo: int = 0) -> None:
        if not self.caminhoes_graneleiros and not self.caminhoes_discretos:
            raise RuntimeError(f"A Transportadora {self.nome_razao_social} não possui caminhões disponíveis.")
        print(f"🚛 [MUNDO FÍSICO] Transportadora '{self.nome_razao_social}' recebeu o lote {lote.id_lote}.")
        self.notificar_listeners("RECEBIMENTO", lote=lote, index_silo=index_silo)
        
        lote.proprietario_atual = self.nome_razao_social
    
    def transferir_carga(self, lote, destino) -> None:
        lote.proprietario_atual = destino.nome_razao_social
        print(f"🚛 [MUNDO FÍSICO] Transportadora '{self.nome_razao_social}' transferiu o lote {lote.id_lote} para '{destino.nome_razao_social}'.")
        self.notificar_listeners("TRANSFERENCIA", lote=lote, destino=destino)


class NodoAduaneiro(EntidadeFinalizadora):
    class TipoModal(Enum):
        MARITIMO = "Porto"
        AEREO = "Aeroporto"
        TERRESTRE = "Fronteira Seca"
        
    def __init__(self, nome: str, cnpj: str, gps: str, modal: "NodoAduaneiro.TipoModal" = TipoModal.MARITIMO):
        super().__init__(nome, cnpj, gps)
        self.modal = modal 

    def obter_papel_rede(self) -> str:
        return f"FINALIZADOR_ADUANEIRO_{self.modal.name}"

    def emitir_certificado_eudr(self, lote) -> bool:
        if not lote.selo_procedencia:
            raise ValueError(f"Exportação Bloqueada no {self.modal.value}: Lote violou regras de desmatamento.")
        print(f"Carga liberada no {self.modal.value} {self.nome_razao_social}. Certificado EUDR emitido.")
        return True
        
    def finalizar_lote(self, lote) -> None:
        lote.proprietario_atual = self.nome_razao_social
        print(f"🚛 [MUNDO FÍSICO] Nodo Aduaneiro '{self.nome_razao_social}' finalizou o lote {lote.id_lote}.")
        self.notificar_listeners("FINALIZACAO", lote=lote)


class MercadoInterno(EntidadeFinalizadora):
    def __init__(self, nome: str, cnpj: str, gps: str):
        super().__init__(nome, cnpj, gps)

    def obter_papel_rede(self) -> str:
        return "MERCADO_INTERNO"
        
    def finalizar_lote(self, lote) -> None:
        lote.proprietario_atual = self.nome_razao_social
        print(f"🚛 [MUNDO FÍSICO] Mercado Interno '{self.nome_razao_social}' finalizou o lote {lote.id_lote}.")
        self.notificar_listeners("FINALIZACAO", lote=lote)