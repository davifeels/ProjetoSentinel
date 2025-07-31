# 👁️ SentinelVision - Sistema de Reconhecimento Facial e Gerenciamento de Perfis

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-AI_Search-0077B5?style=for-the-badge&logo=facebook&logoColor=white)

**Status:** ✅ Concluído
**Categoria:** Segurança, Inteligência Artificial (IA), Visão Computacional, Desenvolvimento Web Full-Stack

---

## 🚀 Visão Geral do Projeto

O **SentinelVision** é uma aplicação web completa e robusta, projetada para reconhecimento facial e gerenciamento de perfis. Construída com um stack moderno e profissional, ela oferece **alta performance** na identificação de indivíduos e uma **interface de dashboard administrativa intuitiva**.

Utilizando tecnologias de ponta como o framework **Flask** para o backend e a biblioteca **FAISS (Facebook AI Similarity Search)** para buscas biométricas eficientes, o sistema permite:

* **Cadastro detalhado de perfis** de indivíduos com suas informações e imagens faciais.
* **Análise de rostos em tempo real** para correspondência ultra-rápida com o banco de dados seguro.
* Um **gerenciamento completo de usuários** com controle de acesso por perfil (Administrador/Usuário), garantindo segurança e flexibilidade.

A aplicação é totalmente **containerizada com Docker e Docker Compose**, o que simplifica o ambiente de desenvolvimento e garante uma implantação consistente e confiável em qualquer servidor.

---

## 🖼️ Demonstrações Visuais

[**IMPORTANTE:** Para tornar seu portfólio verdadeiramente impactante, substitua os placeholders abaixo pelos **links diretos de GIFs animados ou vídeos curtos** que demonstrem as funcionalidades em ação. GIFs são ideais pois carregam automaticamente no GitHub.]

<p align="center">
  <strong>Dashboard de Inteligência</strong><br>
  <img src="URL_DA_SUA_IMAGEM_OU_GIF_DO_DASHBOARD_AQUI.gif" alt="Dashboard de Inteligência" width="80%">
  <br>
  <em>Visualize estatísticas e insights rápidos sobre os perfis cadastrados através de gráficos interativos.</em>
</p>

<p align="center">
  <strong>Galeria de Perfis</strong><br>
  <img src="URL_DA_SUA_IMAGEM_OU_GIF_DA_GALERIA_AQUI.gif" alt="Galeria de Perfis" width="80%">
  <br>
  <em>Navegue e gerencie todos os indivíduos cadastrados em um formato de grid paginado, com opções de busca e filtro.</em>
</p>

<p align="center">
  <strong>Dossiê Detalhado do Indivíduo</strong><br>
  <img src="URL_DA_SUA_IMAGEM_OU_GIF_DO_DOSSIE_AQUI.gif" alt="Dossiê do Indivíduo" width="80%">
  <br>
  <em>Acesse uma tela completa com todas as informações de um perfil, incluindo histórico de avistamentos e perfis similares.</em>
</p>

<p align="center">
  <strong>Reconhecimento Facial em Ação</strong><br>
  <img src="URL_DA_SUA_IMAGEM_OU_GIF_DO_RECONHECIMENTO_AQUI.gif" alt="Reconhecimento Facial em Ação" width="80%">
  <br>
  <em>(Opcional, mas Altamente Recomendado) Demonstração do upload de uma imagem e a exibição do resultado da busca biométrica.</em>
</p>

---

## ✨ Funcionalidades Principais

* **Sistema de Login Seguro:** Autenticação robusta para acesso ao painel administrativo, com senhas criptografadas para proteger os dados.
* **Cadastro Detalhado de Perfis:** Interface completa para registrar novos indivíduos com múltiplos campos de dados, incluindo nome, idade, status (ativo, procurado), localização, documentos, contatos, parentesco e notas, além de uma imagem facial de referência.
* **Busca por Reconhecimento Facial Ultrarrápida:** Utiliza a biblioteca **FAISS** para realizar comparações de vetores faciais em milissegundos, permitindo buscas eficientes em bancos de dados massivos de milhares de perfis sem perda de performance.
* **Dashboard de Inteligência:** Painel visual com estatísticas e gráficos interativos (via Chart.js) sobre a distribuição e o status dos perfis cadastrados, oferecendo insights rápidos e acionáveis.
* **Galeria de Perfis com Paginação:** Visualização organizada de todos os indivíduos cadastrados em um formato de grid, com sistema de paginação para suportar grandes volumes de dados de forma otimizada.
* **Página de Dossiê Completo:** Tela de detalhes dedicada para cada perfil, exibindo todas as informações cadastradas de forma organizada, incluindo fotos de avistamentos e perfis semelhantes.
* **Gerenciamento Completo de Perfis (CRUD):** Funcionalidades intuitivas para **Criar (C)**, **Ler (R)**, **Atualizar (U - edição)** e **Deletar (D)** perfis do sistema.
* **Gerenciamento de Usuários (APENAS ADMIN):** Interface para criar, editar e deletar contas de usuário, com a possibilidade de definir nomes de usuário e gerar senhas seguras, além de gerenciar prazos de expiração para contas.
* **Página "Minha Conta":** Funcionalidade para o usuário logado alterar suas próprias credenciais (nome de usuário e senha), com exigência da senha atual para confirmação de segurança.

---

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído com uma stack moderna e profissional, focando em performance, segurança e escalabilidade:

| Categoria                | Tecnologia                 | Descrição Detalhada                                                                                                |
| :----------------------- | :------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| **Backend** | Python 3.11+               | Linguagem de programação principal para a lógica do servidor.                                                    |
|                          | Flask                      | Microframework web utilizado para a construção da API, rotas e toda a lógica de servidor da aplicação.            |
|                          | Flask-SQLAlchemy           | ORM (Object-Relational Mapper) que facilita a interação entre a aplicação Flask e o banco de dados PostgreSQL.     |
|                          | Flask-Login                | Extensão para Flask que gerencia sessões de usuário, autenticação e autorização baseada em roles.                  |
|                          | `face-recognition`         | Biblioteca robusta para detecção de rostos e geração de codificações faciais (vetores de 128 dimensões) a partir de imagens. |
|                          | `FAISS (Meta AI)`          | Biblioteca otimizada para indexação e busca de vetores de similaridade em alta velocidade, crucial para o reconhecimento facial em grandes datasets. |
|                          | Gunicorn                   | Servidor WSGI (Web Server Gateway Interface) recomendado para servir a aplicação Flask em ambiente de produção.  |
| **Frontend** | HTML5                      | Linguagem de marcação para a estruturação semântica e conteúdo das páginas web.                                    |
|                          | CSS3                       | Linguagem de estilo para a criação do design responsivo, layouts (com Flexbox e Grid), cores e tipografia da interface do usuário. |
|                          | JavaScript (Vanilla)       | Linguagem de script para a interatividade do lado do cliente, manipulação do DOM e requisições assíncronas (AJAX). |
|                          | Chart.js                   | Biblioteca JavaScript utilizada para a criação de gráficos interativos e visuais no dashboard administrativo.        |
| **Banco de Dados** | PostgreSQL 16              | Sistema de gerenciamento de banco de dados relacional (SGBD) robusto e de código aberto, utilizado no ambiente de produção para armazenamento persistente dos dados. |
|                          | SQLite                     | Banco de dados leve e baseado em arquivo, utilizado como fallback opcional para desenvolvimento e testes locais simplificados. |
| **Infraestrutura/Deploy**| Docker                     | Plataforma de containerização que permite empacotar a aplicação e suas dependências em contêineres isolados, garantindo consistência. |
|                          | Docker Compose             | Ferramenta para definir e orquestrar aplicações Docker multi-contêineres, facilitando a configuração e o gerenciamento dos serviços (`web` e `db`). |
| **Utilitários** | `numpy`                    | Biblioteca essencial para operações numéricas de alto desempenho, amplamente utilizada no processamento de vetores de reconhecimento facial. |
|                          | `Pillow`                   | Biblioteca de processamento de imagens, usada para manipulação e otimização das fotos.                             |
|                          | `psycopg2-binary`          | Adaptador de banco de dados PostgreSQL para Python.                                                                |
|                          | `python-dotenv`            | Utilizado para carregar variáveis de ambiente de arquivos `.env`, gerenciando configurações sensíveis do projeto.     |

---

## 🚀 Como Rodar o Projeto (Usando Docker)

Este é o método recomendado, pois configura e orquestra todo o ambiente de desenvolvimento (aplicação + banco de dados) de forma automatizada e consistente.

### Pré-requisitos

* **Docker Desktop** (ou Docker Engine + Docker Compose) instalado e em execução no seu sistema operacional.
* **Git** instalado para clonar o repositório.

### Passos de Instalação e Execução

1.  **Clone o Repositório:**
    Abra seu terminal ou prompt de comando e execute os seguintes comandos:
    ```bash
    git clone [https://github.com/davifeels/ProjetoSentinel.git](https://github.com/davifeels/ProjetoSentinel.git)
    cd ProjetoSentinel
    ```
    *(**Atenção:** Se o nome do seu repositório for `face_app`, use `cd face_app`.)*

2.  **Crie o Arquivo de Ambiente (`.env`):**
    Na raiz do projeto (na mesma pasta onde estão `app.py` e `docker-compose.yml`), crie um arquivo chamado `.env`. Preencha-o com as variáveis de ambiente necessárias, substituindo os valores entre `[]` por suas informações seguras:
    ```dotenv
    # Variáveis de Ambiente para o SentinelVision
    DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db/sentinelvision_db
    SECRET_KEY=[SUA_CHAVE_SECRETA_ALEATORIA_LONGA] # Gere uma string longa e aleatória para segurança do Flask
    FAISS_SIMILARITY_THRESHOLD=0.36 # Limiar de similaridade para o reconhecimento facial (0.0 a 1.0)
    POSTGRES_PASSWORD=[SUA_SENHA_FORTE_POSTGRES] # Senha segura para o usuário 'postgres' do banco de dados
    ```

3.  **Construa e Inicie os Contêineres Docker:**
    Este comando irá construir as imagens Docker da sua aplicação web e do serviço de banco de dados, e em seguida iniciá-los em segundo plano.
    ```bash
    docker compose up -d --build
    ```
    * `-d`: Roda os contêineres em modo "detached" (em segundo plano).
    * `--build`: Reconstrói as imagens, garantindo que todas as alterações recentes no código sejam aplicadas.

4.  **Inicialize o Banco de Dados e Crie o Usuário Administrador Padrão:**
    Após iniciar os contêineres (aguarde alguns segundos para o banco de dados estar totalmente pronto), execute os comandos abaixo para criar as tabelas necessárias no banco de dados e um usuário administrador inicial.
    ```bash
    docker compose exec web flask init-db
    docker compose exec web flask create-admin
    ```
    * **Importante:** O usuário administrador padrão será `admin` e a senha `admin`. Por **segurança**, é fundamental que você altere essa senha imediatamente após o primeiro login!

5.  **Verifique o Status dos Contêineres:**
    Para confirmar se todos os serviços estão rodando corretamente, execute:
    ```bash
    docker compose ps
    ```
    Ambos os serviços, `sentinelvision_web` e `sentinelvision_db`, devem estar no status `Up`.

### Como Acessar a Aplicação

Abra seu navegador web e acesse o seguinte endereço:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

**Credenciais de Acesso Inicial:**
* **Usuário:** `admin`
* **Senha:** `admin`

**Recomendação de Segurança:** Após o primeiro login, acesse a página "Minha Conta" dentro do sistema e altere o nome de usuário e a senha do administrador para credenciais mais seguras.

---

## 🗺️ Roadmap de Futuras Implementações

Estamos sempre buscando aprimorar o SentinelVision. Aqui estão algumas funcionalidades planejadas:

* **Análise de Vídeo em Tempo Real:** Integrar a capacidade de analisar feeds de webcam ao vivo usando OpenCV para detecção e reconhecimento contínuos.
* **Sistema de Alertas Dinâmicos:** Implementar um sistema para disparar alertas visuais e/ou sonoros (via WebSockets) automaticamente ao detectar perfis com status "Procurado" ou outros indicadores críticos.
* **Análise de Atributos Faciais:** Expandir as capacidades de IA para extrair e exibir atributos como idade estimada, gênero e até emoções a partir dos rostos detectados, utilizando bibliotecas como DeepFace.
* **Edição Completa de Perfis:** Aprimorar a funcionalidade de edição para permitir que administradores modifiquem todas as informações de um perfil já cadastrado diretamente pela interface.
* **Otimização para GPUs:** Avaliar a integração com `faiss-gpu` para performance ainda maior em sistemas com hardware dedicado.

---

## 🤝 Contribuição

Contribuições são muito bem-vindas! Se você tiver sugestões de melhoria, encontrar bugs ou desejar adicionar novas funcionalidades, sinta-se à vontade para:

1.  Abrir uma [Issue](https://github.com/[seu-usuario]/[nome-do-repo-sentinelvision]/issues) para descrever bugs ou propor novas funcionalidades.
2.  Enviar um [Pull Request](https://github.com/[seu-usuario]/[nome-do-repo-sentinelvision]/pulls) com suas modificações.

---

## 📄 Licença

Este projeto está licenciado sob a licença [MIT License](https://opensource.org/licenses/MIT). Veja o arquivo `LICENSE` no repositório para mais detalhes.

---

## 💡 Créditos

Feito com ❤️ por **Dvi Anderson**
