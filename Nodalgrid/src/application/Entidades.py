from abc import ABC, abstractmethod
import uuid
from typing import List, Any
from enum import Enum   

# A IMPORTAÇÃO DE OURO: Trazendo os tijolos físicos para o mundo dos negócios
from Recipientes import Silo, Armazem, CaminhaoContinuo, CaminhaoDiscreto

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

    def assinar_bloco_blockchain(self) -> str:
        """Método concreto herdado por todos para carimbar autoria nos eventos."""
        return f"ASSINATURA_{self.documento_cnpj_cpf}_{uuid.uuid4().hex[:8]}"

    @abstractmethod
    def obter_papel_rede(self) -> str:
        pass


# =====================================================================
# 2. PAPÉIS COMPORTAMENTAIS (O que a Entidade faz com o Produto)
# =====================================================================
class EntidadeCriadora(EntidadeLogistica, ABC):
    @abstractmethod
    def gerar_lote_genesis(self, *args, **kwargs):
        """Apenas quem herda desta classe pode dar à luz a um produto no sistema."""
        pass

class EntidadeIntermediária(EntidadeLogistica, ABC):
    @abstractmethod
    def receber_carga(self, lote) -> None:
        """Recebe a posse de um lote, mas não pode alterar sua natureza biológica."""
        pass
    
class EntidadeTransformadora(EntidadeLogistica, ABC):
    @abstractmethod
    def processar_lote(self, lote) -> Any:
        """Transforma o lote em outro produto, alterando suas características."""
        pass
    
class EntidadeFinalizadora(EntidadeLogistica, ABC):
    @abstractmethod
    def finalizar_lote(self, lote) -> None:
        """Marca o lote como pronto para consumo ou exportação, encerrando seu ciclo."""
        pass

# =====================================================================
# 3. CLASSES CONCRETAS (Mundo Real + Composição de Infraestrutura)
# =====================================================================
class Fazenda(EntidadeCriadora):
    """Entidade Gênesis. Possui o CAR e invoca a criação de Lotes."""
    def __init__(self, nome: str, cnpj: str, gps: str, car_registro: str):
        super().__init__(nome, cnpj, gps)
        self.car_registro = car_registro
        self.silos_proprios: List[Silo] = [] # COMPOSIÇÃO
        self.armazens_proprios: List[Armazem] = [] # COMPOSIÇÃO

    def obter_papel_rede(self) -> str:
        return "CRIADOR_GENESIS"

    def construir_silo(self, id_silo: str, capacidade_toneladas: float) -> Silo:
        novo_silo = Silo(id_silo, capacidade_toneladas * 1000)
        self.silos_proprios.append(novo_silo)
        return novo_silo

    def gerar_lote_genesis(self, classe_produto, peso_kg: float):
        """Instancia a classe de produto injetando o CAR da fazenda."""
        novo_lote = classe_produto(
            proprietario_atual=self.nome_razao_social, 
            car_origem=self.car_registro, 
            peso_inicial=peso_kg
        )
        return novo_lote

class Cooperativa(EntidadeIntermediária):
    """Operador Logístico Intermediário. Agrupa silos gigantes para balanço de massa."""
    def __init__(self, nome: str, cnpj: str, gps: str):
        super().__init__(nome, cnpj, gps)
        self.bateria_de_silos: List[Silo] = [] 
        self.armazens_proprios: List[Armazem] = [] 

    def obter_papel_rede(self) -> str:
        return "CUSTODIANTE_INTERMEDIARIO"

    def construir_silo(self, id_silo: str, capacidade_toneladas: float) -> Silo:
        novo_silo = Silo(id_silo, capacidade_toneladas * 1000)
        self.bateria_de_silos.append(novo_silo)
        return novo_silo

    def receber_carga(self, lote, index_silo: int = 0) -> None:
        if not self.bateria_de_silos:
            raise RuntimeError(f"A Cooperativa {self.nome_razao_social} não possui silos construídos.")
        
        lote.proprietario_atual = self.nome_razao_social
        self.bateria_de_silos[index_silo].armazenar(lote)

class Transportadora(EntidadeIntermediária):
    """Operador Logístico Intermediário. Transporta lotes entre silos e armazéns."""
    def __init__(self, nome: str, cnpj: str, gps: str):
        super().__init__(nome, cnpj, gps)
        self.caminhoes_graneleiros: List[CaminhaoContinuo] = [] 
        self.caminhoes_discretos: List[CaminhaoDiscreto] = [] 
        
    def obter_papel_rede(self) -> str:
        return "CUSTODIANTE_INTERMEDIARIO"

    def receber_carga(self, lote) -> None:
        """Transportadora apenas muda a posse do lote, não altera sua natureza."""
        lote.proprietario_atual = self.nome_razao_social

class NodoAduaneiro(EntidadeFinalizadora):
    class TipoModal(Enum):
        MARITIMO = "Porto"
        AEREO = "Aeroporto"
        TERRESTRE = "Fronteira Seca"
        
    def __init__(self, nome: str, cnpj: str, gps: str, modal: "NodoAduaneiro.TipoModal"):
        super().__init__(nome, cnpj, gps)
        self.modal = modal 

    def obter_papel_rede(self) -> str:
        return f"FINALIZADOR_ADUANEIRO_{self.modal.name}"

    def emitir_certificado_eudr(self, lote) -> bool:
        if not lote.selo_procedencia:
            raise ValueError(f"Exportação Bloqueada no {self.modal.value}: Lote violou regras de desmatamento.")
        print(f"Carga liberada no {self.modal.value} {self.nome_razao_social}. Certificado EUDR emitido.")
        return True

class MercadoInterno(EntidadeFinalizadora):
    def __init__(self, nome: str, cnpj: str, gps: str):
        super().__init__(nome, cnpj, gps)

    def obter_papel_rede(self) -> str:
        return "MERCADO_INTERNO"

# =====================================================================
# ÁREA DE TESTES (Playground de Integração)
# =====================================================================
if __name__ == "__main__":
    
    # MOCK RÁPIDO: Simulando o LoteSoja do arquivo Produtos.py para o teste rodar isolado
    class MockLoteSoja:
        def __init__(self, proprietario_atual, car_origem, peso_inicial):
            self.id_lote = uuid.uuid4()
            self.proprietario_atual = proprietario_atual
            self.car_origem = car_origem
            self.peso_atual = peso_inicial

    print("--- TESTE DE ARQUITETURA DE ARQUIVOS SEGREGADOS ---")
    
    fazenda_esperanca = Fazenda("Fazenda Esperança", "11.111.111/0001-99", "Lat:-28.2 Lon:-52.4", "CAR-RS-12345")
    coop_passo_fundo = Cooperativa("Coop Passo Fundo", "22.222.222/0001-88", "Lat:-28.1 Lon:-52.3")
    
    silo_fazenda = fazenda_esperanca.construir_silo("SILO-FAZ-01", capacidade_toneladas=50)
    silo_coop = coop_passo_fundo.construir_silo("SILO-COOP-99", capacidade_toneladas=5000)
    
    print(f"\n[AÇÃO] A Fazenda {fazenda_esperanca.nome_razao_social} colheu soja...")
    lote_colheita = fazenda_esperanca.gerar_lote_genesis(MockLoteSoja, peso_kg=40000.0)
    
    silo_fazenda.armazenar(lote_colheita)
    print("Status Silo Fazenda:", silo_fazenda.exibir_status())
    
    print(f"\n[AÇÃO] Caminhão transfere a soja para a Cooperativa...")
    coop_passo_fundo.receber_carga(lote_colheita, index_silo=0)
    
    print("Novo Proprietário do Lote:", lote_colheita.proprietario_atual)
    print("Status Silo Cooperativa:", silo_coop.exibir_status())
    print("\n✅ Separação concluída com sucesso. Os módulos operam perfeitamente integrados.")