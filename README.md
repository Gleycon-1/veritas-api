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