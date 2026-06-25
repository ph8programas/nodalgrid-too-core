from application.Entidades import Fazenda, Cooperativa, Transportadora, NodoAduaneiro
from application.Produtos import LoteSoja
from application.Blockchain import Blockchain, ComplianceListener

def main():
    print("=== CONFIGURANDO O LEDGER E INFRAESTRUTURA NODALGRID ===")
    
    mockchain = Blockchain()
    auditor_digital = ComplianceListener(mockchain)
    
    fazenda_legal = Fazenda("Fazenda Progresso", "33.333.333/0001-22", "Lat:-15.5 Lon:-47.9", "CAR-GO-11111")
    fazenda_legal.criar_silo("SILO-FAZ-001", capacidade_toneladas=100)
    
    coop_intermediaria = Cooperativa("Coop Central", "22.222.222/0001-88", "Lat:-15.6 Lon:-47.8")
    coop_intermediaria.criar_silo("SILO-COOP-001", capacidade_toneladas=200)
    
    transportadora = Transportadora("Transportadora XYZ", "55.555.555/0001-44", "Lat:-15.8 Lon:-47.5")
    caminhao_graneleiro = transportadora.criar_caminhao_continuo("CAMINHAO-GRANEL-01", capacidad_toneladas=30.0) 
    
    
    # Conexão dos atores ao Listener da Blockchain
    fazenda_legal.registrar_listener(auditor_digital)
    coop_intermediaria.registrar_listener(auditor_digital)
    transportadora.registrar_listener(auditor_digital)

   # ---------------------------------------------------------------------
    print("\n🌾 [PASSO 1] Colheita e MISTURA Homogênea no Silo da Fazenda")
    lote1 = fazenda_legal.colher(LoteSoja, peso_kg=15000.0)
    lote2 = fazenda_legal.colher(LoteSoja, peso_kg=20000.0)
    lote3 = fazenda_legal.colher(LoteSoja, peso_kg=10000.0)

    # Os 3 lotes entram no mesmo silo e misturam-se fisicamente
    fazenda_legal.armazenar_em_silo("SILO-FAZ-001", lote1)
    fazenda_legal.armazenar_em_silo("SILO-FAZ-001", lote2)
    fazenda_legal.armazenar_em_silo("SILO-FAZ-001", lote3)
    
    silo_fazenda = fazenda_legal.silos[0]
    print(f"-> Status do Silo da Fazenda: {silo_fazenda.exibir_status()}")

    # ---------------------------------------------------------------------
    print("\n🚛 [PASSO 2] Extração Física: Camião conecta-se ao Silo e evoca Fracionamento")
    # O camião retira 25 toneladas diretamente do misturado do silo
    lote_transporte = caminhao_graneleiro.extrair_mistura_de_recipiente(
        entidade_origem=fazenda_legal, 
        recipiente_origem=silo_fazenda, 
        peso_a_movimentar=25000.0, 
        classe_produto=LoteSoja
    )
    
    print(f"-> Status do Silo da Fazenda PÓS-EXTRAÇÃO: {silo_fazenda.exibir_status()}")
    print(f"-> Status do Camião Graneleiro: {caminhao_graneleiro.exibir_status()}")
    print(f"-> DNA da Carga: Vinculado a {len(lote_transporte.ids_origem_mistura)} lotes ancestrais.")

    # ---------------------------------------------------------------------
    print("\n🛣️ [PASSO 3] Transporte Logístico e Descarga na Cooperativa")
    caminhao_graneleiro.descarregar_mistura(
        lote_fracao=lote_transporte, 
        peso_a_remover=25000.0, 
        entidade_destino=coop_intermediaria
    )

    print(f"-> Status do Silo da Cooperativa: {coop_intermediaria.silos[0].exibir_status()}")
    print(f"-> Status do Camião Graneleiro pós-descarga: {caminhao_graneleiro.exibir_status()}")

    # ---------------------------------------------------------------------
    print("\n📜 [PASSO 4] Auditoria Geral do Livro-Razão (Ledger Criptográfico)")
    mockchain.percorrer_historico(exibir_console=True)


if __name__ == "__main__":
    main()