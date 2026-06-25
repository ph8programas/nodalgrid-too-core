# Nodalgrid (nodalgrid-too-core)

O **Nodalgrid** é um ecossistema de rastreabilidade para cadeias de suprimentos agrícolas e de commodities, focado na garantia de procedência e conformidade socioambiental legal. O foco principal da aplicação é atender às exigências rígidas do regulamento **EUDR (European Union Deforestation Regulation)**, inviabilizando a exportação de produtos oriundos de áreas de desmatamento ilegal ou com embargos ambientais.

O coração do projeto é um simulador de **Blockchain em Memória** de alto desempenho, que evoluiu de uma lista ligada simples para uma topologia avançada de **Grafo Direcionado Acíclico (DAG)**, resolvendo o problema prático de balanço de massa e misturas de produtos em silos.

---

## 🛠️ Arquitetura e Padrões de Projeto

O sistema foi desenhado seguindo os pilares da Orientação a Objetos e padrões arquiteturais de nível de produção para garantir baixo acoplamento e alta coesão:

* **Arquitetura Orientada a Eventos (EDA):** Implementada através do padrão **Observer (Listeners)**. As entidades logísticas (como Fazendas e Cooperativas) são isoladas da infraestrutura de dados. Elas apenas emitem notificações de ações físicas, que são capturadas pelo `ComplianceListener` e imortalizadas no Ledger. Isso elimina completamente dependências circulares.
* **Grafo de Proveniência (DAG):** Adaptado de conceitos de locais de listas encadeadas com descritor em C++. A classe `Bloco` suporta múltiplos ponteiros anteriores (`blocos_origem`), permitindo rastrear recursivamente por busca em largura (BFS) a genealogia de lotes de grãos fundidos em um único silo.
* **Factory Method:** Centralizado na classe `FabricaEventos`, encapsulando a complexidade de instanciação dos payloads criptográficos e contratos de eventos.
* **Strategy no Motor de Riscos:** O módulo `Riscos.py` utiliza validação determinística simplificada através de um mapa estático de exceções personalizadas (`RiscoAmbientalException`, `RiscoSocialException`), eliminando condicionais aninhadas (`if/else`).
* **Herança Múltipla & Mixins:** Aplicação avançada de Mixins in Python para separar comportamentos físicos (`ComportamentoGranel` e `ComportamentoDiscreto`) de regras taxonômicas e biológicas de produtos ou tipos de mobilidade de recipientes.

---

## 📅 Histórico de Desenvolvimento (Pré-Entrega)

O projeto foi desenvolvido de forma intensiva ao longo da semana sob o seguinte cronograma:

* **Segunda-feira (22/06):** Análise e mapeamento das regras da EUDR. Definição de escopo amplo e estruturação do diagrama conceitual de alto nível (`early_schematics.pdf`).
* **Terça-feira (23/06):** Escrita dos esqueletos estáticos das classes de negócio e ensaio dos Mixins comportamentais.
* **Quarta-feira (24/06):** Refatoração massiva. Implementação do padrão de Listeners para curar o acoplamento circular. Quebra da linearidade da Blockchain para o formato de Grafo (DAG) para resolver misturas de massas.

---

## 🤖 Declaração de Uso de IA

Este repositório faz uso transparente e ético de ferramentas de IA Generativa (como o copiloto Gemini). A inteligência artificial atuou estritamente como **co-piloto arquitetural e ferramenta de revisão de código por pares**.
* **Histórico da Conversa:** https://gemini.google.com/share/b689bd073bd2

Toda a lógica de negócio do domínio EUDR, a escolha e amarração de padrões de projeto e o design do fluxo do `main.py` são de **autoria e responsabilidade humana exclusiva** do desenvolvedor. A IA auxiliou na depuração de exceções em tempo de execução (*RecursionError*), polimento de assinaturas e formatação de documentação em Mermaid.

---

## 🚀 O que ainda falta (Roadmap de Evolução)

O escopo ambicioso do projeto fez com que algumas implementações fossem postergadas para a entrega final:

1. **Caminho de Fluxo Completo:** Fechar a integração lógica ponta a ponta simulando a saída física da soja desde a colheita na fazenda até o embarque no Porto Aduaneiro.
2. **Expansão de Cargas Discretas:** Validar de forma robusta e prática os fluxos de desmembramento de lotes de madeira (DOF) e gado (GTA).
3. **Módulos de Transformação:** Criar o evento que simula a alteração biológica e industrial da matéria-prima (Ex: Soja industrializada transformando-se em Óleo de Soja).

---
**Passo Fundo, RS, Brasil, 2026.**