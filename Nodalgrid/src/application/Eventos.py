from abc import ABC, abstractmethod
import uuid
from datetime import datetime

from Produtos import LoteAgro
from Entidades import EntidadeLogistica
from Riscos import ValidadorRisco

# =====================================================================
# 1. O CONTEXTO BASE (Abstração do Evento)
# =====================================================================
class EventoLogistico(ABC):
    def __init__(self, entidade_responsavel: EntidadeLogistica, lote_envolvido: LoteAgro):
        self.id_evento = uuid.uuid4()
        self.timestamp = datetime.now().isoformat()
        self.entidade_responsavel = entidade_responsavel
        self.lote_envolvido = lote_envolvido
        self.selo_procedencia = lote_envolvido.selo_procedencia
        self.assinatura_digital = entidade_responsavel.assinar_bloco_blockchain()
        
        # Instância única do validador centralizado
        self.validador = ValidadorRisco()

    @abstractmethod
    def validar_regras(self) -> bool:
        """As classes filhas definem quais riscos validar neste evento."""
        pass

    def resumir_evento(self) -> dict:
        return {
            "id_evento": str(self.id_evento),
            "tipo_evento": self.__class__.__name__,
            "timestamp": self.timestamp,
            "id_lote": str(self.lote_envolvido.id_lote),
            "cnpj_responsavel": self.entidade_responsavel.documento_cnpj_cpf,
            "assinatura": self.assinatura_digital,
            "selo_eudr_valido": self.selo_procedencia
        }

    def exibir_resumo(self) -> None:
        resumo = self.resumir_evento()
        print(f"Resumo do Evento {resumo['id_evento']}:")
        for chave, valor in resumo.items():
            print(f"  {chave}: {valor}")

# =====================================================================
# 2. CLASSES CONCRETAS (Implementação do novo modelo)
# =====================================================================

class EventoColheitaGenesis(EventoLogistico):
    def validar_regras(self) -> bool:
        # Passando o booleano 'True' (deve_falhar) para simular fracasso
        self.validador.validar(self, "ambiental", deve_falhar=True, mensagem="Desmatamento detectado")
        self.validador.validar(self, "ambiental", deve_falhar=True, mensagem="Embargo IBAMA")
        self.validador.validar(self, "social", deve_falhar=True, mensagem="Trabalho Escravo")
        return True

class EventoTransferenciaCustodia(EventoLogistico):
    def validar_regras(self) -> bool:
        self.validador.validar(self, "logistico", deve_falhar=True, mensagem="Fraude de Origem")
        self.validador.validar(self, "logistico", deve_falhar=True, mensagem="Silo Contaminado")
        return True

class EventoFracionamento(EventoLogistico):
    def __init__(self, entidade, original, extraido, qtd):
        super().__init__(entidade, original)
        self.lote_extraido = extraido
        self.quantidade_movimentada = qtd

    def validar_regras(self) -> bool:
        self.validador.validar(self, "logistico", deve_falhar=True, mensagem="Fraude na Balança")
        self.validador.validar(self, "logistico", deve_falhar=True, mensagem="Silo Contaminado")
        return True

# O exemplo de uso no if __name__ == "__main__" agora deve chamar 
# evento.validar_regras() em vez de evento.validar_integridade()
# =====================================================================
# PLAYGROUND DE INTEGRAÇÃO (Garantindo o funcionamento do Namespace)
# =====================================================================
if __name__ == "__main__":
    from Entidades import Fazenda
    from Produtos import LoteSoja
    
    print("--- TESTING NODALGRID EVENT ENVIRONMENT (NAMESPACE MODE) ---")
    
    # Criando uma fazenda regular e simulando o fluxo normal
    fazenda_legal = Fazenda(
        nome="Fazenda Progresso", 
        cnpj="33.333.333/0001-22", 
        gps="Lat:-15.5 Lon:-47.9", 
        car_registro="CAR-GO-11111"
    )
    soja_legal = LoteSoja(fazenda_legal.nome_razao_social, fazenda_legal.car_registro, peso_inicial=50000)
    
    evento_colheita = EventoColheitaGenesis(fazenda_legal, soja_legal)
    
    # Executa a validação em cadeia de todas as estratégias injetadas via rsc
    if evento_colheita.validar_regras():
        print(f"✅ SUCESSO: Evento {evento_colheita.id_evento} validado contra todos os riscos de mercado.")
        evento_colheita.exibir_resumo()