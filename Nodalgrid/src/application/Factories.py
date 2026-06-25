from application.Entidades import EntidadeLogistica
from application.Produtos import LoteAgro
from application.Eventos import (EventoArmazenamento,
                                 EventoColheita,
                                 EventoTransferencia,
                                 EventoFracionamento,
                                 EventoProcessamento,
                                 EventoFinalizacao)


class FabricaEventos:
    """
    Factory para encapsular a instanciação de 
    Seguindo o padrão de projeto Factory Method.
    """
    
    @staticmethod
    def criar_lote(entidade: EntidadeLogistica, lote: LoteAgro):
        """Cria um evento de gênese (início do ciclo)."""
        return EventoColheita(entidade, lote)

    @staticmethod
    def criar_transferencia(origem: EntidadeLogistica, destino: EntidadeLogistica, lote: LoteAgro):
        """Cria um evento de transferência entre entidades."""
        return EventoTransferencia(origem, lote, destino)

    @staticmethod
    def criar_armazenamento(entidade: EntidadeLogistica, lote: LoteAgro, id_recipiente: str):
        """Cria um evento de armazenamento de lotes."""
        return EventoArmazenamento(entidade, lote, id_recipiente)

    @staticmethod
    def criar_fracionamento(entidade: EntidadeLogistica, original: LoteAgro, extraido: LoteAgro, qtd: float):
        """Cria um evento de fracionamento de lotes."""
        return EventoFracionamento(entidade, original, extraido, qtd)
    
    @staticmethod
    def criar_processamento(entidade: EntidadeLogistica, lote: LoteAgro):
        """Cria um evento de processamento de lotes."""
        return EventoProcessamento(entidade, lote)
    
    @staticmethod
    def criar_finalizacao(entidade: EntidadeLogistica, lote: LoteAgro):
        """Cria um evento de finalização de lotes."""
        return EventoFinalizacao(entidade, lote)