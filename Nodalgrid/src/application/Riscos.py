from abc import ABC
from ast import Dict
from datetime import datetime

# =====================================================================
# 1. HIERARQUIA DE EXCEÇÕES (O erro)
# =====================================================================
class RiscoBaseException(Exception):
    def __init__(self, mensagem, entidade, lote):
        super().__init__(mensagem)
        self.entidade = entidade
        self.lote = lote
        self.timestamp = datetime.now()

class RiscoAmbientalException(RiscoBaseException): pass
class RiscoSocialException(RiscoBaseException): pass
class RiscoLogisticoException(RiscoBaseException): pass

# =====================================================================
# 2. CLASSE UNIFICADA DE VALIDAÇÃO
# =====================================================================
class ValidadorRisco:
    """Centraliza a lógica de auditoria usando um dicionário de tipos."""
    
    # Mapeamento: Chave do tipo para a Classe de Exceção correspondente
    _MAPEAMENTO_RISCOS = {
        "ambiental": RiscoAmbientalException,
        "social": RiscoSocialException,
        "logistico": RiscoLogisticoException
    }

    def validar(self, evento, tipo_risco: str, deve_falhar: bool, mensagem: str = "Lote Comprometido"):
        """Método genérico que dispara a exceção correta sem if/else."""
        if deve_falhar:
            # Busca a classe de exceção no dicionário
            classe_risco = self._MAPEAMENTO_RISCOS.get(tipo_risco)
            
            if classe_risco:
                # Dispara a exceção mapeada
                raise classe_risco(mensagem, evento.entidade_responsavel, evento.lote_envolvido)
            else:
                raise ValueError(f"Tipo de risco '{tipo_risco}' desconhecido.")
        
        # print(f"Validação {tipo_risco} concluída para o lote {evento.lote_envolvido.id_lote}. Sem riscos detectados.")
        return True
    
if __name__ == "__main__":
    # Teste rápido de validação
    class MockEvento:
        def __init__(self):
            self.entidade_responsavel = "Entidade X"
            self.lote_envolvido = "Lote Y"
            self.id_evento = "Evento 1"
    validador = ValidadorRisco()
    evento_teste = MockEvento()
    
    try:
        validador.validar(evento_teste, "ambiental", True)
    except RiscoAmbientalException as e:
        print(f"Risco Ambiental: {e}, Entidade: {e.entidade}, Lote: {e.lote}, Timestamp: {e.timestamp}")
    
    try:
        validador.validar(evento_teste, "social", False)
    except RiscoSocialException as e:
        print(f"Risco Social: {e}, Entidade: {e.entidade}, Lote: {e.lote}, Timestamp: {e.timestamp}")
    
    try:
        validador.validar(evento_teste, "logistico", False)
    except RiscoLogisticoException as e:
        print(f"Risco Logístico: {e}, Entidade: {e.entidade}, Lote: {e.lote}, Timestamp: {e.timestamp}")

    try:
        validador.validar(evento_teste, "logistico", False)
    except RiscoLogisticoException as e:
        print(f"Risco Logístico: {e}, Entidade: {e.entidade}, Lote: {e.lote}, Timestamp: {e.timestamp}")