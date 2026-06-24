from Entidades import EntidadeLogistica
from Produtos import LoteAgro
import Eventos as eventos


class FabricaEventos:
    """
    Factory para encapsular a instanciação de eventos.
    Seguindo o padrão de projeto Factory Method.
    """
    
    @staticmethod
    def criar_colheita(entidade: EntidadeLogistica, lote: LoteAgro):
        """Cria um evento de gênese (início do ciclo)."""
        return eventos.EventoColheitaGenesis(entidade, lote)

    @staticmethod
    def criar_transferencia(origem: EntidadeLogistica, destino: EntidadeLogistica, lote: LoteAgro):
        """Cria um evento de transferência entre entidades."""
        return eventos.EventoTransferenciaCustodia(origem, destino, lote)

    @staticmethod
    def criar_fracionamento(entidade: EntidadeLogistica, original: LoteAgro, extraido: LoteAgro, qtd: float):
        """Cria um evento de fracionamento de lotes."""
        return eventos.EventoFracionamento(entidade, original, extraido, qtd)
    
    @staticmethod
    def criar_processamento(entidade: EntidadeLogistica, lote: LoteAgro):
        """Cria um evento de processamento de lotes."""
        return eventos.EventoProcessamento(entidade, lote)
    
    @staticmethod
    def criar_finalizacao(entidade: EntidadeLogistica, lote: LoteAgro):
        """Cria um evento de finalização de lotes."""
        return eventos.EventoFinalizacao(entidade, lote)