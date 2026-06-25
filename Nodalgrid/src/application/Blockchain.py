from enum import Enum
import hashlib
import json
from datetime import datetime
from typing import Optional, List, Dict
from application.Eventos import EventoLogistico
from application.Factories import FabricaEventos 

class Bloco:
    """
    O Nó da nossa lista encadeada reversa. 
        Uma vez instanciado, seus atributos jamais devem ser alterados.
        """
    def __init__(self, evento: EventoLogistico, bloco_anterior: Optional['Bloco']):
        # 1. Payload Logístico (O Domínio)
        self.conteudo = evento
        
        # 2. Ponteiro Reversivo (A Infraestrutura)
        self.bloco_anterior = bloco_anterior
        
        # 3. Atributos Criptográficos
        self.hash_anterior = bloco_anterior.hash_atual if bloco_anterior else "0" * 64
        self.timestamp_bloco = datetime.now().isoformat()
        
        # O Hash atual é a última coisa a ser gerada, lacrando o bloco
        self.hash_atual = self._calcular_hash()

    def _calcular_hash(self) -> str:
        """
        Gera a assinatura digital (SHA-256) do bloco com base nos dados vitais.
        """
        # Criamos um dicionário estrito para não incluir ponteiros de memória no hash
        dados_para_hash = {
            "id_evento": str(self.conteudo.id_evento),
            "hash_anterior": self.hash_anterior,
            "timestamp": self.timestamp_bloco
        }
        
        # json.dumps com sort_keys garante que a ordem das chaves não mude o hash
        bloco_string = json.dumps(dados_para_hash, sort_keys=True)
        return hashlib.sha256(bloco_string.encode()).hexdigest()


class Blockchain:
    """
    O Descritor da estrutura. Gerencia exclusivamente o estado atual (a ponta) da corrente.
    """
    def __init__(self):
        # A blockchain só conhece o bloco mais recente. O resto é descoberto navegando para trás.
        self.ultimo: Optional[Bloco] = None
        self.tamanho: int = 0

    def adicionar_bloco(self, evento: EventoLogistico) -> None:
        """
        Acopla um novo evento à corrente se, e somente se, ele passar na auditoria do domínio.
        """
        if not evento.validar_regras():
            raise ValueError(f"Bloco Rejeitado: O evento possui inconformidades.")
    
        # 1. Executa a ação de fato do evento
        evento.executar_acao()

        # 2. Imortaliza o evento na corrente
        novo_bloco = Bloco(evento, self.ultimo)
        self.ultimo = novo_bloco
        self.tamanho += 1
        print(f"🔗 [BLOCKCHAIN] Bloco adicionado! Hash: {novo_bloco.hash_atual[:8]}...")

    def percorrer_historico(self) -> List[Dict]:
        """
        Varre a blockchain de trás para frente e inverte o resultado para exibição cronológica (Dashboard).
        """
        historico_reverso = []
        bloco_atual = self.ultimo
        
        # Navegação via ponteiro anterior O(n)
        while bloco_atual is not None:
            historico_reverso.append({
                "hash_bloco": bloco_atual.hash_atual,
                "hash_anterior": bloco_atual.hash_anterior,
                "evento_tipo": bloco_atual.conteudo.__class__.__name__,
                "id_evento": str(bloco_atual.conteudo.id_evento),
                "timestamp": bloco_atual.timestamp_bloco,
                "selo_procedencia": bloco_atual.conteudo.selo_procedencia
            })
            bloco_atual = bloco_atual.bloco_anterior
            
        # Inverte a lista para retornar da Gênese até o momento atual
        return historico_reverso[::-1]

    def validar_integridade_cadeia(self) -> bool:
        """
        O coração do compliance: Recalcula todos os hashes do passado para o presente
        para garantir que nenhum objeto foi adulterado na memória RAM.
        """
        bloco_atual = self.ultimo
        
        while bloco_atual is not None:
            # 1. Verifica se o hash salvo bate com o cálculo matemático atual
            if bloco_atual.hash_atual != bloco_atual._calcular_hash():
                return False
            
            # 2. Verifica se a ligação com o passado foi corrompida
            if bloco_atual.bloco_anterior is not None:
                if bloco_atual.hash_anterior != bloco_atual.bloco_anterior.hash_atual:
                    return False
                    
            bloco_atual = bloco_atual.bloco_anterior
            
        return True
    
class ComplianceListener:
    ##class TipoEventos(Enum):
    ##  COLHEITA = "COLHEITA"
    ##  TRANSFERENCIA = "TRANSFERENCIA"
    ##  FINALIZACAO = "FINALIZACAO"
        
    """Ouvinte que escuta as Entidades e dispara os Eventos Logísticos."""
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain

    def on_evento_logistico(self, entidade, acao: str, **kwargs):
            lote = kwargs.get("lote")
            
            print(f"📡 [LISTENER] Capturada ação '{acao}' da entidade '{entidade.nome_razao_social}'!")
            
            try:
                # O Listener atua como o maestro, chamando a Factory correta baseada na ação
                if acao == "COLHEITA":
                    evento = FabricaEventos.criar_lote(entidade, lote)
                    self.blockchain.adicionar_bloco(evento)
                elif acao == "ARMAZENAMENTO":
                    id_silo = kwargs.get("id_silo")
                    evento = FabricaEventos.criar_armazenamento(lote, id_silo)
                    self.blockchain.adicionar_bloco(evento)
                    
                elif acao == "TRANSFERENCIA":
                    destino = kwargs.get("destino")
                    evento = FabricaEventos.criar_transferencia(entidade, destino, lote)
                    self.blockchain.adicionar_bloco(evento)
                
                elif acao == "FRACIONAMENTO":
                    lote_extraido = kwargs.get("lote_extraido")
                    qtd = kwargs.get("quantidade")
                    evento = FabricaEventos.criar_fracionamento(entidade, lote, lote_extraido, qtd)
                    self.blockchain.adicionar_bloco(evento)
                    
                elif acao == "PROCESSAMENTO":
                    evento = FabricaEventos.criar_processamento(entidade, lote)
                    self.blockchain.adicionar_bloco(evento)
                    
                elif acao == "FINALIZACAO":
                    evento = FabricaEventos.criar_finalizacao(entidade, lote)
                    self.blockchain.adicionar_bloco(evento)
                    
            except ValueError as e:
                # Se o validador dentro de adicionar_bloco barrar, o erro é capturado aqui
                print(f"❌ [ERRO COMPLIANCE] {e}")