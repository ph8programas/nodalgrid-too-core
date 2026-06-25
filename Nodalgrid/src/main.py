from application.Entidades import Fazenda, Cooperativa
from application.Produtos import LoteSoja
from application.Factories import FabricaEventos
from application.Blockchain import Blockchain

def main():
    # 1. Setup: Instanciação única do Ledger (Blockchain)
    blockchain = Blockchain()
    
    # 2. Setup: Instanciação das Entidades de Domínio
    fazenda_legal = Fazenda("Fazenda Progresso", "33.333.333/0001-22", "Lat:-15.5 Lon:-47.9", "CAR-GO-11111")
    coop_recebedora = Cooperativa("Coop Central", "22.222.222/0001-88", "Lat:-15.6 Lon:-47.8")

    # 3. Execução: Ciclo de Vida do Produto
    # A Fazenda gera um Lote (Produto)
    soja = fazenda_legal.gerar_lote(LoteSoja, peso_kg=50000.0)

    # 4. Orquestração: Factory cria o Evento e o motor de Validação verifica
    try:
        # A Factory encapsula a complexidade da criação
        evento_colheita = FabricaEventos.criar_colheita(fazenda_legal, soja)
        
        # O Evento orquestra sua própria validação (Encapsulamento)
        if evento_colheita.validar_regras():
            # Se válido, a Blockchain o imortaliza
            blockchain.adicionar_bloco(evento_colheita)
            print("✅ Evento de Colheita registrado com sucesso!")

    except Exception as e:
        print(f"❌ Falha no Compliance: {e}")

    # 5. Exibição: Histórico de Auditoria
    print("\n--- RELATÓRIO DE AUDITORIA (BLOCKCHAIN) ---")
    for bloco in blockchain.percorrer_historico():
        print(bloco)

if __name__ == "__main__":
    main()