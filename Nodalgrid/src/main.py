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
    print("\n[AÇÃO FÍSICA 1] O Trator está colhendo...")
    soja_legal = fazenda_legal.colher(LoteSoja, peso_kg=50000.0)
    detalhes_soja_legal = soja_legal.mostrar_detalhes()
    detalhes_mockchain = mockchain.percorrer_historico()
    print(f"Detalhes da Mockchain após a colheita: {detalhes_mockchain}")
    print(f"Detalhes do Lote Colhido: {detalhes_soja_legal}")
    fazenda_legal.armazenar_em_silo("SILO-001", soja_legal)
    detalhes_soja_legal = soja_legal.mostrar_detalhes()
    print(f"Detalhes do Lote Armazenado: {detalhes_soja_legal}")
    detalhes_mockchain = mockchain.percorrer_historico()
    print(f"Detalhes da Mockchain após o armazenamento: {detalhes_mockchain}")
    

    
    



if __name__ == "__main__":
    main()