from abc import ABC, abstractmethod
import uuid
from typing import List, Dict, Any,Tuple
from enum import Enum   

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
# 1. COMPORTAMENTO PARA RECIPIENTES DE VOLUME/KG (Silo, Caminhão Graneleiro)
# =====================================================================
class ArmazenamentoContinuo:
    """Gerencia o armazenamento de pesos contínuos (floats) e impede transbordamento."""
    
    def armazenar(self, lote_granel) -> None:
        # Se o peso do lote extraído + o que já tem dentro estourar o limite, ele grita.
        if self.ocupacao_atual + lote_granel.peso_atual > self.capacidade_maxima:
            raise ValueError(f"Recipiente {self.id_recipiente} estourou a capacidade máxima de KG!")
        
        # Se couber, ele apenas soma o peso e guarda o ID do lote no histórico
        self.ocupacao_atual += lote_granel.peso_atual
        self.historico_lotes.append(lote_granel.id_lote)

class CarregamentoContinuo:
    """Injeta a lógica de movimentação de fluidos/massas baseada em peso (float)."""
    def carregar(self, lote_origem, peso_a_movimentar: float) -> Any:
        """
        Extrai uma parte do peso do lote e absorve para dentro do recipiente.
        'lote_origem' deve ter o método 'fracionar'.
        """
        if peso_a_movimentar <= 0:
            raise ValueError("A quantidade a ser carregada deve ser maior que zero.")
            
        # O método 'fracionar' do lote deduz o peso dele e nos cospe um novo lote com o extrato
        lote_extraido = lote_origem.fracionar(peso_a_movimentar, self.id_recipiente)
        
        # O recipiente tenta engolir esse peso extraído (chama a validação do Mixin físico)
        self.armazenar(lote_extraido)
        return lote_extraido

    def descarregar(self, lote_contido, peso_a_remover: float, entidade_destino) -> None:
        """Retira o peso de dentro do recipiente físico e entrega para uma entidade."""
        if peso_a_remover > lote_contido.peso_atual:
            raise ValueError("Tentativa de descarregar volume maior do que o contido no veículo.")
            
        # Executa a matemática de saída do aço
        self.ocupacao_atual -= peso_a_remover
        lote_contido.peso_atual -= peso_a_remover
        
        # Entrega o rastro jurídico para o destino
        entidade_destino.receber_carga(lote_contido)


# =====================================================================
# 2. COMPORTAMENTO PARA RECIPIENTES DISCRETOS (Curral, Caminhão Boiadeiro)
# =====================================================================
class ArmazenamentoDiscreto:
    """Gerencia o armazenamento de unidades indivisíveis (ints) e impede superlotação do pátio/curral."""
    def armazenar(self, lote_discreto) -> None:
        # Se a quantidade de cabeças/toras do lote + o que já tem estourar o limite, grita.
        if self.ocupacao_atual + lote_discreto.quantidade_unidades > self.capacidade_maxima:
            raise ValueError(f"Recipiente {self.id_recipiente} estourou a capacidade máxima de UNIDADES!")
        
        # Se couber, soma as unidades e guarda o ID do lote
        self.ocupacao_atual += lote_discreto.quantidade_unidades
        
        # Como é discreto, usamos lotes_armazenados para manter a segregação (não vira sopa)
        if not hasattr(self, 'lotes_armazenados'):
            self.lotes_armazenados = []
        self.lotes_armazenados.append(lote_discreto.id_lote)

class CarregamentoDiscreto:
    """Injeta a lógica de movimentação de unidades indivisíveis (List de objetos)."""

    def carregar(self, lote_origem, ids_unidades: list) -> Any:
        """
        Arranca os objetos específicos do lote de origem e joga no veículo.
        'lote_origem' deve ter o método 'desmembrar_lote'.
        """
        if not ids_unidades:
            raise ValueError("Selecione pelo menos uma unidade (Boi/Tora) para carregar.")
            
        # Desmandra os bois específicos do lote original na fazenda
        lote_extraido = lote_origem.desmembrar_lote(ids_unidades, self.id_recipiente)
        
        # O veículo engole a contagem dessas unidades
        self.armazenar(lote_extraido)
        return lote_extraido

    def descarregar(self, lote_contido, ids_unidades: list, entidade_destino) -> None:
        """Desmolda os animais ou toras do veículo e passa a custódia para o CNPJ de destino."""
        # Remove do lote que estava viajando no caminhão
        lote_descarregado = lote_contido.desmembrar_lote(ids_unidades, entidade_destino.nome_razao_social)
        
        # Subtrai a ocupação física do veículo de aço
        self.ocupacao_atual -= len(ids_unidades)
        
        # Aloca o lote resultante dentro do armazém da entidade receptora
        entidade_destino.receber_carga(lote_descarregado)
    


class Silo(RecipienteEstacionario, CarregamentoContinuo, ArmazenamentoContinuo):
    """Infraestrutura para Granéis (Soja, Milho). Trabalha com peso contínuo (float)."""
    def __init__(self, id_recipiente: str, capacidade_maxima_kg: float):
        super().__init__(id_recipiente, capacidade_maxima_kg)
        self.historico_lotes = [] # Rastreia o que já entrou aqui (Balanço de Massa)

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
        # Passa a capacidade como inteiro para a classe mãe
        super().__init__(id_recipiente, capacidade_maxima_unidades)
        self.lotes_armazenados = [] # Mantém a segregação física, não faz "sopa" de unidades

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
        self.lotes_transportados = [] # Mantém o histórico de lotes transportados

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
        self.lotes_transportados = [] # Mantém o histórico de lotes transportados

    def exibir_status(self) -> dict:
        return {
            "caminhao_id": self.id_recipiente,
            "capacidade_unidades": int(self.capacidade_maxima),
            "ocupacao_unidades": int(self.ocupacao_atual),
            "qtd_lotes_transportados": len(self.lotes_transportados)
        }

# =====================================================================
# 2. FAMÍLIA DOS CNPJs (Atores Ativos e Legais)
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
# 3. PAPÉIS COMPORTAMENTAIS (O que a Entidade faz com o Produto)
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
# 4. CLASSES CONCRETAS (Mundo Real + Composição de Infraestrutura)
# =====================================================================
class Fazenda(EntidadeCriadora):
    """Entidade Gênesis. Possui o CAR e invoca a criação de Lotes."""
    def __init__(self, nome: str, cnpj: str, gps: str, car_registro: str):
        super().__init__(nome, cnpj, gps)
        self.car_registro = car_registro
        self.silos_proprios: List[Silo] = [] # COMPOSIÇÃO: A Fazenda TEM Silos
        self.armazens_proprios: List[Armazem] = [] # COMPOSIÇÃO: A Fazenda TEM Armazéns

    def obter_papel_rede(self) -> str:
        return "CRIADOR_GENESIS"

    def construir_silo(self, id_silo: str, capacidade_toneladas: float) -> Silo:
        novo_silo = Silo(id_silo, capacidade_toneladas * 1000)
        self.silos_proprios.append(novo_silo)
        return novo_silo

    def gerar_lote_genesis(self, classe_produto, peso_kg: float):
        """Instancia a classe de produto (ex: LoteSoja) injetando o CAR da fazenda."""
        # Nota: No sistema final, usaremos a FactoryProdutos aqui dentro.
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
        self.bateria_de_silos: List[Silo] = [] # COMPOSIÇÃO: A Cooperativa TEM Silos
        self.armazens_proprios: List[Armazem] = [] # COMPOSIÇÃO: A Cooperativa TEM Armazéns

    def obter_papel_rede(self) -> str:
        return "CUSTODIANTE_INTERMEDIARIO"

    def construir_silo(self, id_silo: str, capacidade_toneladas: float) -> Silo:
        novo_silo = Silo(id_silo, capacidade_toneladas * 1000)
        self.bateria_de_silos.append(novo_silo)
        return novo_silo

    def receber_carga(self, lote, index_silo: int = 0) -> None:
        """Guarda o lote na infraestrutura física e muda a propriedade jurídica."""
        if not self.bateria_de_silos:
            raise RuntimeError(f"A Cooperativa {self.nome_razao_social} não possui silos construídos.")
        
        # 1. Altera a propriedade (Jurídico)
        lote.proprietario_atual = self.nome_razao_social
        # 2. Armazena no recipiente físico (Física)
        self.bateria_de_silos[index_silo].armazenar(lote)

class Transportadora(EntidadeIntermediária):
    """Operador Logístico Intermediário. Transporta lotes entre silos e armazéns."""
    def __init__(self, nome: str, cnpj: str, gps: str):
        super().__init__(nome, cnpj, gps)
        self.caminhoes_graneleiros: List[CaminhaoContinuo] = [] # COMPOSIÇÃO: A Transportadora TEM Caminhões Graneleiros
        self.caminhoes_discretos: List[CaminhaoDiscreto] = [] # COMPOSIÇÃO: A Transportadora TEM Caminhões de Carga Geral
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
        
    """Classe única que resolve todo o escoamento internacional do sistema."""
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
    
    # MOCK RÁPIDO: Simulando o LoteSoja do arquivo Produtos.py para o teste rodar
    class MockLoteSoja:
        def __init__(self, proprietario_atual, car_origem, peso_inicial):
            self.id_lote = uuid.uuid4()
            self.proprietario_atual = proprietario_atual
            self.car_origem = car_origem
            self.peso_atual = peso_inicial

    print("--- TESTE DE ARQUITETURA: FAZENDA E COOPERATIVA ---")
    
    # 1. Instanciando os CNPJs (Atores)
    fazenda_esperanca = Fazenda("Fazenda Esperança", "11.111.111/0001-99", "Lat:-28.2 Lon:-52.4", "CAR-RS-12345")
    coop_passo_fundo = Cooperativa("Coop Passo Fundo", "22.222.222/0001-88", "Lat:-28.1 Lon:-52.3")
    
    # 2. Construindo a Infraestrutura de Aço (Composição)
    silo_fazenda = fazenda_esperanca.construir_silo("SILO-FAZ-01", capacidade_toneladas=50)
    silo_coop = coop_passo_fundo.construir_silo("SILO-COOP-99", capacidade_toneladas=5000)
    
    print(f"\n[AÇÃO] A Fazenda {fazenda_esperanca.nome_razao_social} colheu soja...")
    
    # 3. A Entidade Criadora gera o bloco Gênesis
    lote_colheita = fazenda_esperanca.gerar_lote_genesis(MockLoteSoja, peso_kg=40000.0)
    
    # 4. A Fazenda guarda no próprio silo provisoriamente
    silo_fazenda.armazenar(lote_colheita)
    print("Status Silo Fazenda:", silo_fazenda.exibir_status())
    
    print(f"\n[AÇÃO] Caminhão transfere a soja para a Cooperativa...")
    
    # 5. A Cooperativa recebe a carga (Muda propriedade legal e joga na lata de metal dela)
    coop_passo_fundo.receber_carga(lote_colheita, index_silo=0)
    
    print("Novo Proprietário do Lote:", lote_colheita.proprietario_atual)
    print("Status Silo Cooperativa:", silo_coop.exibir_status())
    
    # 6. Testando as assinaturas criptográficas
    print("\nAssinatura da Fazenda:", fazenda_esperanca.assinar_bloco_blockchain())
    print("Assinatura da Cooperativa:", coop_passo_fundo.assinar_bloco_blockchain())
    print("\n✅ O teste provou que os CNPJs operam o aço sem se misturarem com ele.")