from abc import ABC, abstractmethod
import uuid
from datetime import datetime

from application.Produtos import LoteAgro
from application.Entidades import EntidadeLogistica
from application.Riscos import ValidadorRisco

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
        # self.assinatura_digital = entidade_responsavel.assinar_bloco_blockchain()
        self.validador = ValidadorRisco()

    @abstractmethod
    def validar_regras(self) -> bool:
        """As classes filhas definem quais riscos validar neste evento."""
        pass
    
    @abstractmethod
    def executar_acao(self) -> None:
        """As classes filhas implementam a ação específica do evento."""
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

class EventoColheita(EventoLogistico):
    def validar_regras(self) -> bool:
        """Valida os riscos ambientais, sociais e logísticos para a colheita."""
        self.validador.validar(self, "ambiental", deve_falhar=False)
        self.validador.validar(self, "social", deve_falhar=False)
        self.validador.validar(self, "logistico", deve_falhar=False)
        return True
    def executar_acao(self) -> None:
        """A ação de colheita é apenas simbólica neste contexto."""
        print(f"Evento de Colheita registrado para o lote {self.lote_envolvido.id_lote}.")
    
class EventoArmazenamento(EventoLogistico):
    def validar_regras(self) -> bool:
        """Valida os riscos logísticos para o armazenamento do lote."""
        self.validador.validar(self, "logistico", deve_falhar=False)
        return True

    def executar_acao(self, id_recipiente: str) -> None:
        """Armazena o lote em um recipiente específico da entidade logística."""
        pass
    
    

class EventoTransferencia(EventoLogistico):
    def validar_regras(self) -> bool:
        """Valida os riscos logísticos para a transferência de custódia."""
        self.validador.validar(self, "logistico", deve_falhar=False)
        return True

    def executar_acao(self, destino: EntidadeLogistica) -> None:
        """Transfere a posse do lote para outra entidade logística."""
        # Aqui você pode implementar a lógica de transferência de custódia
        try:
            self.lote_envolvido.proprietario_atual = destino.nome_razao_social
        except Exception as e:
            print(f"❌ [ERRO] Erro ao transferir o lote {self.lote_envolvido.id_lote}: {e}")
        print(f"Evento de Transferência registrado para o lote {self.lote_envolvido.id_lote}.")

class EventoFracionamento(EventoLogistico):
    pass

class EventoProcessamento(EventoLogistico):
    pass

class EventoFinalizacao(EventoLogistico):
    def validar_regras(self) -> bool:
        """Valida os riscos logísticos para a finalização do lote."""
        self.validador.validar(self, "logistico", deve_falhar=False)
        self.validador.validar(self, "ambiental", deve_falhar=False)
        self.validador.validar(self, "social", deve_falhar=False)
        return True
    def executar_acao(self) -> None:
        """Marca o lote como finalizado e pronto para consumo ou exportação."""
        print(f"Evento de Finalização registrado para o lote {self.lote_envolvido.id_lote}.")
        ## Logica de finalização do lote, como atualizar status, notificar entidades, etc.


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
    
    evento_colheita = EventoColheita(fazenda_legal, soja_legal)
    
    # Executa a validação em cadeia de todas as estratégias injetadas via rsc
    if evento_colheita.validar_regras():
        print(f"✅ SUCESSO: Evento {evento_colheita.id_evento} validado contra todos os riscos de mercado.")
        evento_colheita.exibir_resumo()