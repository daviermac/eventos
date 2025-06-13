# Sistema de Eventos Culturais

Sistema web desenvolvido em Python com Flask para gerenciamento de eventos culturais locais, destinado à Secretaria de Turismo.

## 🎯 Funcionalidades

- **Cadastro de Eventos**: Registro completo de shows, feiras, peças teatrais, exposições, etc.
- **Calendário Interativo**: Visualização dos eventos em formato de calendário
- **Listagem e Filtros**: Lista de eventos com filtros por categoria, mês e busca
- **Detalhes Completos**: Visualização detalhada de cada evento
- **Interface Responsiva**: Design adaptável para desktop e mobile
- **API REST**: Endpoints para integração com outras aplicações


## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.8+ com Flask
- **Banco de Dados**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Calendário**: FullCalendar.js
- **ORM**: SQLAlchemy


## 📋 Pré-requisitos

- Python 3.8 ou superior
- MySQL 5.7 ou superior
- pip (gerenciador de pacotes Python)


## 🚀 Instalação e Configuração

### 1. Crie um ambiente virtual

```shellscript
python -m venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Instale as dependências

```shellscript
pip install -r requirements.txt
```

### 3. Configure o banco de dados

Abra o MySQL Command Line Client:

```shellscript
mysql -u root -p
```

Execute os comandos para criar o banco:

```sql
-- Criar o banco de dados
CREATE DATABASE IF NOT EXISTS eventos_culturais 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Verificar se foi criado
SHOW DATABASES;
```

### 4. Configure a aplicação

No arquivo `app.py`, ajuste a string de conexão com suas credenciais:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:SUA_SENHA@localhost/eventos_culturais'
```

### 5. Execute a aplicação

```shellscript
python app.py
```

A aplicação estará disponível em `http://localhost:5328`

## 📱 Como Usar

### Página Inicial

- Visão geral do sistema com estatísticas
- Acesso rápido às principais funcionalidades
- Próximos eventos em destaque


### Cadastro de Eventos

1. Acesse "Novo Evento" no menu
2. Preencha as informações obrigatórias (título, categoria, data, horário, local)
3. Adicione informações opcionais (descrição, organizador, preço, etc.)
4. Clique em "Cadastrar Evento"


### Visualização no Calendário

- Acesse "Calendário" no menu
- Navegue entre meses, semanas ou dias
- Clique em um evento para ver detalhes
- Use os controles para navegar entre períodos


### Gerenciamento de Eventos

- Liste todos os eventos em "Eventos"
- Use filtros por categoria, mês ou busca por texto
- Visualize detalhes completos de cada evento
- Edite ou exclua eventos conforme necessário


## 🔧 Estrutura do Projeto

```plaintext
eventos-culturais-flask/
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── templates/             # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── calendario.html
│   ├── eventos.html
│   ├── novo_evento.html
│   ├── detalhes_evento.html
│   └── editar_evento.html
```

## 🌐 API Endpoints

- `GET /api/eventos` - Lista todos os eventos ativos
- `GET /api/eventos/<id>` - Detalhes de um evento específico


## 🎨 Categorias de Eventos

- Show
- Feira
- Teatro
- Exposição
- Festival
- Workshop
- Outro


## 📊 Funcionalidades Administrativas

- Estatísticas em tempo real
- Filtros avançados
- Controle de status dos eventos
- Interface intuitiva para gestão


## 🔒 Segurança

- Validação de dados no frontend e backend
- Proteção contra SQL Injection via SQLAlchemy
- Sanitização de entradas do usuário
- Configuração segura de sessões


## 🤝 Contribuição

Este é um projeto de extensão acadêmica. Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request


## 📄 Licença

Este projeto foi desenvolvido para fins educacionais como parte de um projeto de extensão em DevOps.

## 👥 Equipe

Projeto desenvolvido pela equipe de extensão DevOps para a Secretaria de Turismo.

## 📞 Suporte

Para dúvidas ou suporte, entre em contato com a equipe de desenvolvimento.
