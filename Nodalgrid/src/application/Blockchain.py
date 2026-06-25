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
    def __init__(self, evento: EventoLogistico, bloco_anterior: Optional['Bloco'], blocos_origem: List['Bloco']):        # 1. Payload Logístico (O Domínio)
        self.evento = evento
        
        # 2. Ponteiro Reversivo (A Infraestrutura)
        self.bloco_anterior = bloco_anterior
        
        # 3. Ponteiros do Domínio (A Árvore Genealógica do Lote)
        self.blocos_origem = blocos_origem
        # Ordenar os hashes de origem é obrigatório para não gerar hashes diferentes se a lista mudar de ordem
        self.hashes_origem = sorted([b.hash_atual for b in blocos_origem]) if blocos_origem else []
        
        # 4. Atributos Criptográficos
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
            "id_evento": str(self.evento.id_evento),
            "id_lote_principal": str(self.evento.lote_envolvido.id_lote),
            "hash_anterior": self.hash_anterior,
            "hashes_origem": self.hashes_origem,
            "timestamp": self.timestamp_bloco
        }
        
        # json.dumps com sort_keys garante que a ordem das chaves não mude o hash
        bloco_string = json.dumps(dados_para_hash, sort_keys=True)
        return hashlib.sha256(bloco_string.encode()).hexdigest()


class Blockchain:
    """
    Fachada para a lista encadeada reversa de blocos, com suporte a DAG para rastreabilidade de lotes.
    """
    def __init__(self):
        # A blockchain só conhece o bloco mais recente. O resto é descoberto navegando para trás.
        self.ultimo: Optional[Bloco] = None
        self.tamanho: int = 0
        # Índice de acesso rápido O(1) para saber qual foi o último bloco que alterou um lote específico
        self.estado_lotes: Dict[str, Bloco] = {}

    def adicionar_bloco(self, evento: EventoLogistico, ids_lotes_origem: List[str] = None) -> None:
        """
        Acopla um novo evento à corrente se, e somente se, ele passar na auditoria do domínio.
        """
        if not evento.validar_regras():
            raise ValueError(f"Bloco Rejeitado: O evento possui inconformidades.")
    
        # 1. Executa a ação de fato do evento
        evento.executar_acao()

        pais_do_lote = []
        id_lote_atual = str(evento.lote_envolvido.id_lote)

        # Se for um evento de mistura, busca os blocos das pontas dos lotes ancestrais
        if ids_lotes_origem:
            for l_id in ids_lotes_origem:
                if l_id in self.estado_lotes:
                    pais_do_lote.append(self.estado_lotes[l_id])
        else:
            # Fluxo linear ordinário do mesmo lote
            if id_lote_atual in self.estado_lotes:
                pais_do_lote.append(self.estado_lotes[id_lote_atual])

        #  Injeção explícita de 'pais_do_lote' como o terceiro parâmetro obrigatório
        novo_bloco = Bloco(evento, self.ultimo, pais_do_lote)
        
        # Atualiza os ponteiros do Ledger global
        self.ultimo = novo_bloco
        self.tamanho += 1
        
        # Atualiza o índice de estados para apontar a ponta do lote para este bloco recente
        self.estado_lotes[id_lote_atual] = novo_bloco
        print(f"🔗 [BLOCKCHAIN] Bloco {novo_bloco.hash_atual[:8]} adicionado! Lote: {id_lote_atual[:8]}")
        
    def rastrear_lote(self, id_lote: str) -> List[Dict]:
        """Faz a busca em largura (BFS) no DAG para remontar a árvore do lote e de suas misturas."""
        if id_lote not in self.estado_lotes:
            return []
            
        historico = []
        fila = [self.estado_lotes[id_lote]]
        visitados = set()

        while fila:
            bloco_atual = fila.pop(0)
            
            # Previne loops infinitos caso a estrutura tenha sido comprometida
            if bloco_atual.hash_atual in visitados:
                continue
                
            visitados.add(bloco_atual.hash_atual)
            
            historico.append({
                "hash_bloco": bloco_atual.hash_atual,
                "evento_tipo": bloco_atual.evento.__class__.__name__,
                "id_lote": str(bloco_atual.evento.lote_envolvido.id_lote),
                "timestamp": bloco_atual.timestamp_bloco
            })
            
            # Adiciona os pais geológicos à fila de pesquisa
            fila.extend(bloco_atual.blocos_origem)
            
        return historico        
        
    def percorrer_historico(self, exibir_console: bool = False) -> List[Dict]:
        """
        Varre a blockchain de trás para frente e inverte o resultado para exibição cronológica (Dashboard),
        incluindo os vínculos de genealogia física (hashes de origem).
        """
        historico_reverso = []
        bloco_atual = self.ultimo
        
        # Navegação via ponteiro anterior O(n) na cadeia linear global
        while bloco_atual is not None:
            registro = {
                "hash_bloco": bloco_atual.hash_atual,
                "hash_anterior": bloco_anterior.hash_atual if (bloco_anterior := bloco_atual.bloco_anterior) else "0" * 64,
                "evento_tipo": bloco_atual.evento.__class__.__name__,
                "id_evento": str(bloco_atual.evento.id_evento),
                "id_lote": str(bloco_atual.evento.lote_envolvido.id_lote),
                "timestamp": bloco_atual.timestamp_bloco,
                "selo_procedencia": bloco_atual.evento.selo_procedencia,
                # NOVO: Exporta a genealogia física do lote no dicionário do histórico
                "hashes_origem": bloco_atual.hashes_origem
            }
            historico_reverso.append(registro)
            bloco_atual = bloco_atual.bloco_anterior
            
        historico = historico_reverso[::-1]

        if exibir_console:
            print("\n📜 [HISTÓRICO DA BLOCKCHAIN / LEDGER GLOBAL]")
            for indice, bloco in enumerate(historico, start=1):
                # Formata a exibição das origens físicas do grafo
                origens_str = ", ".join([h[:8] for h in bloco['hashes_origem']]) if bloco['hashes_origem'] else "GÊNESE"
                
                print(
                    f" {indice}. [{bloco['evento_tipo']}] | Evento ID: {bloco['id_evento'][:8]}... | Lote ID: {bloco['id_lote'][:8]}...\n"
                    f"    Selo ESG: {bloco['selo_procedencia']} | Timestamp: {bloco['timestamp']}\n"
                    f"    Ancestrais Físicos (Misturas): {origens_str}\n"
                    f"    Hash Bloco: {bloco['hash_bloco']}\n"
                    f"    Hash Anterior Global: {bloco['hash_anterior']}"
                )
                if indice != len(historico):
                    print("    " + "-" * 72)

        return historico

    def validar_integridade_cadeia(self) -> bool:
        bloco_atual = self.ultimo
        while bloco_atual is not None:
            if bloco_atual.hash_atual != bloco_atual._calcular_hash():
                return False
            if bloco_atual.bloco_anterior is not None:
                if bloco_atual.hash_anterior != bloco_atual.bloco_anterior.hash_atual:
                    return False
            bloco_atual = bloco_atual.bloco_anterior
        return True
    
class ComplianceListener:
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
                elif acao == "ARMAZENAMENTO_MISTURA":
                    id_silo = kwargs.get("id_silo")
                    lotes_misturados = kwargs.get("ids_lotes_origem")
                    evento = FabricaEventos.criar_armazenamento(entidade, lote, id_silo)
                    self.blockchain.adicionar_bloco(evento, ids_lotes_origem=lotes_misturados)    
                elif acao == "EXTRAÇÃO_MISTURA":
                    lote_mistura = kwargs.get("lote")
                    ids_origem = kwargs.get("ids_lotes_origem")
                    qtd = kwargs.get("quantidade")
                    
                    # Invoca a Factory para criar o fracionamento do lote virtual (mistura)
                    evento = FabricaEventos.criar_fracionamento(entidade, lote_mistura, lote_mistura, qtd)
                    
                    # Conecta o novo bloco à Blockchain, repassando o "DNA" dos lotes originais
                    self.blockchain.adicionar_bloco(evento, ids_lotes_origem=ids_origem)
                                    
                elif acao == "TRANSFERENCIA":
                    destino = kwargs.get("destino")
                    evento = FabricaEventos.criar_transferencia(entidade, lote, destino)
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