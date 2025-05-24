# 🧠 Veritas API

## 📡 Contexto do Projeto

A **Veritas API** é uma ferramenta inteligente projetada para identificar e classificar automaticamente conteúdos online com base em sua veracidade. O objetivo principal é **combater a desinformação**, oferecendo uma solução acessível e escalável para plataformas, empresas e usuários finais.

## 🎯 Objetivo Geral

Desenvolver uma API que analisa conteúdos textuais, utilizando algoritmos e modelos de linguagem para verificar a veracidade das informações. Nosso foco vai além do simples 'verdadeiro' ou 'falso': a Veritas API busca fornecer uma **análise granular e crítica**, distinguindo as nuances da informação online para empoderar o usuário a consumir conteúdo de forma mais consciente.

---

## 🧠 Funcionalidades

* **Análise de Conteúdo Textual Avançada:** Processa textos via requisições, utilizando o poder de Modelos de Linguagem de Grande Escala (LLMs).
* **Classificação Nuanceada:** Vai além da dicotomia simples, classificando o conteúdo em categorias detalhadas como `fake_news`, `verdadeiro`, `sátira`, `opinião`, `parcial` e `indefinido`.
* **Indicação Visual por Cor:** Retorna classificações em formato de código de cor intuitivo para rápida compreensão.
* **Comparação com Fontes Confiáveis:** Integração futura via scraping para referenciar e validar informações.
* **API RESTful Completa:** Interface clara e documentada via Swagger UI (`/docs`) para fácil integração e gerenciamento de análises.

---

## 🟡 Classificações por Cor

Para fornecer uma representação visual rápida e intuitiva da natureza do conteúdo, cada classificação gerada pelos modelos de linguagem é mapeada para uma cor específica:

* 🟢 **Verde**: Conteúdo **verdadeiro**, factual, verificável e preciso, baseado em evidências ou dados confirmados.
* 🔴 **Vermelho**: **Fake news** ou desinformação, conteúdo comprovadamente falso ou enganoso, criado para manipular.
* ⚪ **Branco/Cinzento**: **Sátira**, conteúdo humorístico, irônico ou que utiliza o exagero e a paródia. **Não tem intenção de enganar**, mas de divertir ou criticar de forma cômica.
* 🔵 **Azul**: **Opinião**, expressão de um ponto de vista pessoal, crença ou interpretação. Geralmente se declara como tal e **não busca disfarçar sua natureza subjetiva.**
* 🟠 **Laranja**: Conteúdo **parcial** ou tendencioso, que apresenta um viés claro, favorecendo ou desfavorecendo um lado, uma ideia ou um grupo. Pode usar linguagem carregada e **tenta parecer objetivo ou neutro, mas não é.**
* ⚫ **Preto**: **Indefinido** ou erro, para conteúdo ambíguo, sem contexto, com informações insuficientes para uma classificação clara, ou quando ocorre um erro técnico na análise.

---

## 📁 Estrutura de Endpoints

* `POST /analyze` – Recebe texto ou URL, processa via LLM e retorna uma classificação por cor.
* `GET /analysis/{analysis_id}` – Consulta uma análise específica pelo seu ID no banco de dados.
* `PUT /analysis/{analysis_id}/status` – Atualiza o status de uma análise (ex: de 'pending' para 'completed').
* `DELETE /analysis/{analysis_id}` – Deleta uma análise do banco de dados.
* `GET /status/:id` – Consulta o status de uma análise anterior. (Planejado/Futuro)
* `POST /feedback` – Coleta retorno humano sobre uma análise para refinar os modelos. (Planejado/Futuro)
* `GET /history` – Retorna o histórico de análises por usuário. (Planejado/Futuro)

---

## 🧩 Tecnologias Utilizadas

* **Linguagem**: Python
* **Framework**: FastAPI
* **Banco de Dados**: SQLite (padrão atual, configurável para MongoDB ou PostgreSQL no futuro)
* **Modelos de Linguagem**: Google Gemini (gemini-1.5-flash), OpenAI API (gpt-3.5-turbo, gpt-4), com flexibilidade para integração de outros LLMs.
* **Web Scraping**: Coleta de dados de portais confiáveis (Lógica a ser implementada/expandida)

---

## 🧱 Arquitetura do Projeto

O projeto segue uma arquitetura modular, separando responsabilidades para facilitar escalabilidade e manutenção. Esta estrutura clara permite que a API seja robusta e fácil de expandir: 

veritas-api/
├── src/
│   ├── main.py                     # Inicialização da aplicação e roteamento principal
│   ├── api/
│   │   ├── routes_analyze.py       # Endpoint: /analyze (Análise com LLMs)
│   │   ├── routes_crud.py          # Endpoints: /analysis/... (Operações CRUD de análises)
│   │   ├── routes_status.py        # Endpoint: /status (Status da API ou de análises)
│   │   ├── routes_feedback.py      # Endpoint: /feedback (Coleta de feedback)
│   │   └── routes_history.py       # Endpoint: /history (Histórico de análises)
│   ├── models/
│   │   └── analysis.py             # Schemas Pydantic e modelos de dados para a API
│   ├── core/
│   │   ├── config.py               # Carrega variáveis de ambiente e configurações globais
│   │   ├── llm_integration.py      # Lógica de integração e comunicação com LLMs (Gemini, OpenAI)
│   │   └── verification.py         # Futuro: Lógica de verificação de conteúdo aprofundada
│   ├── db/
│   │   ├── crud_operations.py      # Funções para operações CRUD no banco de dados
│   │   ├── database.py             # Configuração da conexão e sessão do banco de dados (SQLAlchemy)
│   │   └── models.py               # Definições de modelos de banco de dados (SQLAlchemy ORM)
│   └── utils/
│       └── scraping.py             # Futuro: Utilitários para coleta de dados externos confiáveis
├── .env                            # Variáveis de ambiente (API Keys, URL do DB, etc.)
└── requirements.txt                # Dependências do projeto Python
└── README.md                       # Este arquivo (documentação do projeto)


---

## 🔗 Token – Veritas Token (Plano Blockchain)

Será criado um token próprio para:

* **Autenticação Premium:** Conceder acesso a funcionalidades avançadas e maior limite de requisições.
* **Sistema de Reputação por Feedback Humano:** Recompensar usuários por feedback preciso e útil na validação de análises.
* **Recompensas por Validações Confiáveis:** Incentivar a participação da comunidade na curadoria de informações.
* **Futuras Integrações com Plataformas Descentralizadas:** Facilitar a interoperabilidade em ecossistemas Web3.

---

## 🚀 Visão de Futuro

* **Plugins de Integração:** Desenvolver plugins para plataformas populares como WordPress, Shopify e redes sociais para análise de conteúdo em tempo real.
* **Uso Corporativo:** Expandir para análise de reputação de marcas, monitoramento de notícias e validação de informações em ambientes empresariais.
* **Expansão Setorial:** Levar a análise de conteúdo para os setores **educacional** (verificação de material didático), **jurídico** (análise de precedentes e documentos) e **político** (monitoramento de discursos e propostas), auxiliando na tomada de decisões informadas.
* **Parcerias Estratégicas:** Buscar colaborações com grandes empresas de tecnologia e plataformas de notícias para ampliar o alcance e impacto da Veritas API.

---

## 📎 Contribuição

Contribuições são muito bem-vindas! Se você tem ideias para melhorias, novas funcionalidades ou encontrou algum problema:

* Sinta-se à vontade para abrir **issues** no repositório para relatar bugs ou sugerir funcionalidades.
* Envie **pull requests** com suas contribuições de código.

Vamos juntos combater a desinformação com tecnologia e inteligência! 💡

---