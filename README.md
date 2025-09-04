👁️ SentinelVision
Um sistema de reconhecimento facial e gerenciamento de perfis desenvolvido com Python, Flask e PostgreSQL.

🚀 Sobre o Projeto
O SentinelVision é uma aplicação web monolítica projetada para a gestão de perfis e verificação biométrica em tempo real. O sistema permite cadastrar novos indivíduos, gerenciar dossiês com informações detalhadas e realizar buscas faciais para identificar pessoas no banco de dados.

Ele utiliza uma arquitetura baseada em contêineres Docker, com um backend robusto em Python (Flask) e um banco de dados PostgreSQL, otimizados para um ambiente de desenvolvimento e implantação eficiente.

✨ Funcionalidades Principais
Dashboard Interativo: Uma visão geral com estatísticas dos perfis e registros recentes.

Análise Biométrica em Tempo Real: Envie uma imagem para buscar e identificar rostos correspondentes no banco de dados.

Gestão de Perfis: Cadastre novos indivíduos com informações completas e fotos, e atualize os dados em seus dossiês.

Banco de Dados de Perfis: Visualize todos os indivíduos cadastrados em uma galeria paginada, com filtros de busca por nome, documento ou status.

Gerenciamento de Usuários: Funcionalidade restrita a administradores para criar, redefinir senhas e excluir contas de acesso ao sistema.

🛠️ Tecnologias Utilizadas
Backend: Python com Flask

Banco de Dados: PostgreSQL 16

Infraestrutura: Docker e Docker Compose

Reconhecimento Facial: dlib e face_recognition

Índice de Busca: faiss-cpu para busca de similaridade em alta velocidade

Frontend: HTML, CSS, JavaScript e Jinja2 para a renderização dinâmica das páginas.

📁 Estrutura de Pastas
.
├── .flaskenv
├── .gitignore
├── app.py
├── docker-compose.yml
├── Dockerfile
├── faiss_index.bin
├── init_db_logs.txt
├── requirements.txt
├── static/
│   ├── css/
│   │   ├── base.css
│   │   ├── dashboard.css
│   │   ├── detail.css
│   │   ├── detail_gallery.css
│   │   ├── gallery.css
│   │   ├── login.css
│   │   ├── manage_users.css
│   │   ├── my_account.css
│   │   ├── register.css
│   │   ├── reset_password.css
│   │   ├── search.css
│   │   └── style.css
│   ├── db_images/
│   ├── images/
│   ├── sighting_images/
│   ├── manifest.json
│   └── service-worker.js
└── templates/
    ├── dashboard.html
    ├── edit_person.html
    ├── gallery.html
    ├── index.html
    ├── layout.html
    ├── login.html
    ├── manage_users.html
    ├── my_account.html
    ├── person_detail.html
    ├── register.html
    └── reset_password.html
⚙️ Como Executar Localmente
Siga estes passos para configurar e executar a aplicação em sua máquina.

Pré-requisitos
Certifique-se de ter o Docker e o Docker Compose instalados.

Clonar o Repositório

Bash

git clone [URL_DO_SEU_REPOSITORIO]
cd ProjetoSentinel
Configurar Variáveis de Ambiente
Crie um arquivo chamado .env na pasta raiz do projeto. Ele será usado para configurar o acesso ao banco de dados e a chave secreta da aplicação. As variáveis de ambiente do PostgreSQL estão definidas no seu docker-compose.yml e a URL de conexão é referenciada no app.py.

Snippet de código

# .env
DATABASE_URL=postgresql://postgres:admin@db/sentinelvision_db
SECRET_KEY=dev-secret-key-for-local-use-only
(A senha admin está definida no docker-compose.yml e pode ser alterada lá).

Construir e Iniciar os Contêineres
A aplicação e o banco de dados serão criados e iniciados a partir das configurações do seu Dockerfile e docker-compose.yml.

Bash

docker-compose up --build
Isso pode levar alguns minutos na primeira vez para instalar todas as dependências do requirements.txt.

Inicializar o Banco de Dados e Criar Usuário Admin
Com os contêineres em execução, você precisa inicializar o banco de dados e criar o usuário administrador padrão. Execute os seguintes comandos em outro terminal a partir da pasta raiz do projeto:

Bash

docker-compose exec web flask init-db
docker-compose exec web flask create-admin
O comando init-db cria todas as tabelas necessárias e carrega o índice FAISS. O create-admin cria um usuário admin com a senha padrão admin.

Acessar a Aplicação
Após a inicialização, a aplicação estará disponível em http://localhost:5000 e a tela de login será exibida.

Usuário: admin

Senha: admin
