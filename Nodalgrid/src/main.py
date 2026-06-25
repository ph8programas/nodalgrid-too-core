from application.Entidades import Fazenda, Cooperativa, Transportadora, NodoAduaneiro
from application.Produtos import LoteSoja
from application.Blockchain import Blockchain, ComplianceListener

def main():
    # 1. Setup: Instanciação única do Ledger (Blockchain)
    # Nesse protótipo, a "blockchain" é essencialmente um descritor, nome mais correto seria "ledger" ou "registro imutável de eventos".
    # Mas a ideia é que seja de fato implementeado como uma blockchain, com hash encadeado e validação de integridade. 
    mockchain = Blockchain()
    auditor_digital = ComplianceListener(mockchain)
    
    mockchain.percorrer_historico()
    
    # 2. Setup: Instanciação das Entidades de Domínio
    fazenda_legal = Fazenda("Fazenda Progresso", "33.333.333/0001-22", "Lat:-15.5 Lon:-47.9", "CAR-GO-11111")
    fazenda_legal.registrar_listener(auditor_digital)  # A Fazenda notifica o auditor digital sobre eventos de interesse,o mesmo para as demais entidades
    fazenda_legal.criar_silo("SILO-001", 100)  # 100 toneladas
    # Acessar o silo criado: por exemplo, usando a chave do silo no dicionário interno
    # silo_001 = fazenda_legal.silos["SILO-001"]


    fazenda_irregular = Fazenda("Fazenda Irregular", "44.444.444/0001-33", "Lat:-15.4 Lon:-47.6", "CAR-GO-22222")
    fazenda_irregular.registrar_listener(auditor_digital)  
    fazenda_irregular.criar_silo("SILO-002", 50)   
    
    coop_intermediaria = Cooperativa("Coop Central", "22.222.222/0001-88", "Lat:-15.6 Lon:-47.8")
    coop_intermediaria.registrar_listener(auditor_digital)  
    coop_intermediaria.criar_silo("SILO-COOP-001", 200) 
    
    transportadora_intermediaria = Transportadora("Transportadora XYZ", "55.555.555/0001-44", "Lat:-15.8 Lon:-47.5")
    transportadora_intermediaria.registrar_listener(auditor_digital)  
    transportadora_intermediaria.criar_caminhao("CAMINHAO-001", 30) 
    
    porto_exportador = NodoAduaneiro("Porto de Exportação", "11.111.111/0001-99", "Lat:-15.7 Lon:-47.7")
    porto_exportador.registrar_listener(auditor_digital) 

    # 3. Execução: Ciclo de Vida do Produto
    # A Fazenda gera um Lote (Produto)
    print("\n[AÇÃO FÍSICA 1] O Trator está colhendo o Lote A...")
    soja_A = fazenda_legal.colher(LoteSoja, peso_kg=20000.0)
    fazenda_legal.armazenar_em_silo("SILO-001", soja_A)
    
    print("\n--- RASTREABILIDADE DO LOTE A (DAG / GRAFO DE ORIGEM) ---")
    grafo = mockchain.rastrear_lote(str(soja_A.id_lote))
    import json
    print(json.dumps(grafo, indent=2))
    
    print("\n--- HISTÓRICO DA BLOCKCHAIN ---")
    mockchain.percorrer_historico(True)
    
    print("\n[AÇÃO FÍSICA 2] O Trator está colhendo o Lote B...")
    soja_B = fazenda_legal.colher(LoteSoja, peso_kg=15000.0)
    # AQUI OCORRE A MISTURA NO MESMO SILO:
    fazenda_legal.armazenar_em_silo("SILO-001", soja_B)
    
    
    print("\n[AÇÃO FÍSICA 2] O Trator está colhendo o Lote C...")
    soja_C = fazenda_legal.colher(LoteSoja, peso_kg=5000.0)
    # AQUI OCORRE A MISTURA NO MESMO SILO:
    fazenda_legal.armazenar_em_silo("SILO-001", soja_C)
    
    print("\n--- RASTREABILIDADE DO LOTE C (DAG / GRAFO DE ORIGEM) ---")
    grafo = mockchain.rastrear_lote(str(soja_C.id_lote))
    import json
    print(json.dumps(grafo, indent=2))
        
    print("\n--- HISTÓRICO DA BLOCKCHAIN ---")
    mockchain.percorrer_historico(True)
    
    print(f"\nSilos da entidade {fazenda_legal.nome_razao_social}:")
    for silo in fazenda_legal.silos:
        print(silo.exibir_status())
    
    
    
    



if __name__ == "__main__":
    main()