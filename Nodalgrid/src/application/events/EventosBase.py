from abc import ABC, abstractmethod
import uuid
from datetime import datetime
# Importamos o contrato do produto para fazer a dica de tipo (Type Hint)
from ..Produtos import LoteAgro

class EventoLogistico(ABC):
    """
    Classe Abstrata Base (Contrato) para os nós de histórico da Blockchain.
    Qualquer ação real (Colheita, Silo, Navio) precisa assinar este contrato.
    """
    def __init__(self, lote: LoteAgro, custodiante_atual: str):
        self.id_evento = uuid.uuid4()             # ID único do fato histórico
        self.lote = lote                          # Associação de POO: O evento carrega o objeto do lote
        self.timestamp = datetime.now().isoformat()
        self.custodiante_atual = custodiante_atual # O operador logístico responsável no momento
        
        # O evento herda o estado de conformidade atual do lote no momento do registo
        self.selo_procedencia = lote.selo_procedencia

    @abstractmethod
    def validar_regras(self) -> bool:
        """
        O coração do Polimorfismo no projeto.
        A Blockchain chamará este método às cegas. Cada evento específico (Colheita, Porto)
        deverá implementar aqui o seu pente-fino de auditoria ambiental e fiscal.
        Retorna True se estiver em conformidade, ou False/Lança Exceção se violar as regras.
        """
        pass