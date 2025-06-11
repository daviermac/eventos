from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import Numeric
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from config import config
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(config['default'])

if not app.config.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = 'sua-chave-secreta-muito-segura-aqui'

db = SQLAlchemy(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Você precisa fazer login para acessar esta página.'
login_manager.login_message_category = 'warning'

# Modelo de usuário para autenticação
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nome_completo = db.Column(db.String(200), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_active(self):
        return self.ativo

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Modelo de dados para eventos
class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    data_evento = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time)
    local = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.String(300))
    categoria = db.Column(db.String(50), nullable=False)
    organizador = db.Column(db.String(100))
    contato = db.Column(db.String(100))
    preco = db.Column(Numeric(10, 2))
    capacidade = db.Column(db.Integer)
    status = db.Column(db.String(20), default='ativo')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.titulo,
            'start': f"{self.data_evento}T{self.hora_inicio}",
            'end': f"{self.data_evento}T{self.hora_fim}" if self.hora_fim else None,
            'description': self.descricao,
            'location': self.local,
            'category': self.categoria,
            'organizer': self.organizador,
            'contact': self.contato,
            'price': float(self.preco) if self.preco else None,
            'capacity': self.capacidade,
            'status': self.status
        }

# ÁREA PÚBLICA 

@app.route('/')
def site_home():
    return render_template('public/home.html')

@app.route('/eventos')
def site_eventos():
    categoria = request.args.get('categoria')
    if categoria:
        eventos = Evento.query.filter_by(status='ativo', categoria=categoria).order_by(Evento.data_evento.asc()).all()
    else:
        eventos = Evento.query.filter_by(status='ativo').order_by(Evento.data_evento.asc()).all()
    return render_template('public/eventos.html', eventos=eventos)

@app.route('/evento/<int:id>')
def site_evento_detalhes(id):
    evento = Evento.query.get_or_404(id)
    return render_template('public/evento_detalhes.html', evento=evento)

@app.route('/calendario')
def site_calendario():
    return render_template('public/calendario.html')

# AUTENTICAÇÃO 

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = bool(request.form.get('remember'))
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        if usuario and usuario.check_password(password) and usuario.is_active():
            usuario.ultimo_login = datetime.utcnow()
            db.session.commit()
            login_user(usuario, remember=remember)
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin_home')
            
            flash(f'Bem-vindo, {usuario.nome_completo}!', 'success')
            return redirect(next_page)
        else:
            flash('Usuário ou senha inválidos.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('admin_login'))

# ÁREA ADMINISTRATIVA 

@app.route('/admin')
@login_required
def admin_home():
    return render_template('admin/index.html')

@app.route('/admin/eventos')
@login_required
def admin_eventos():
    eventos = Evento.query.filter_by(status='ativo').order_by(Evento.data_evento.asc()).all()
    return render_template('admin/eventos.html', eventos=eventos)

@app.route('/admin/calendario')
@login_required
def admin_calendario():
    return render_template('admin/calendario.html')

@app.route('/admin/estatisticas')
@login_required
def admin_estatisticas():
    try:
        total_eventos = Evento.query.filter_by(status='ativo').count()
        
        eventos_por_mes = db.session.query(
            db.extract('month', Evento.data_evento).label('mes'),
            db.func.count(Evento.id).label('total')
        ).filter_by(status='ativo').group_by(db.extract('month', Evento.data_evento)).all()
        
        eventos_por_categoria = db.session.query(
            Evento.categoria,
            db.func.count(Evento.id).label('total')
        ).filter_by(status='ativo').group_by(Evento.categoria).all()
        
        eventos_por_status = db.session.query(
            Evento.status,
            db.func.count(Evento.id).label('total')
        ).group_by(Evento.status).all()
        
        hoje = datetime.now().date()
        proximos_30_dias = hoje + timedelta(days=30)
        
        proximos_eventos = Evento.query.filter(
            Evento.status == 'ativo',
            Evento.data_evento >= hoje,
            Evento.data_evento <= proximos_30_dias
        ).order_by(Evento.data_evento.asc()).limit(10).all()
        
        ultimos_30_dias = hoje - timedelta(days=30)
        eventos_passados = Evento.query.filter(
            Evento.status == 'ativo',
            Evento.data_evento >= ultimos_30_dias,
            Evento.data_evento < hoje
        ).count()
        
        eventos_gratuitos = Evento.query.filter(
            Evento.status == 'ativo',
            db.or_(Evento.preco == None, Evento.preco == 0)
        ).count()
        
        eventos_pagos = Evento.query.filter(
            Evento.status == 'ativo',
            Evento.preco > 0
        ).count()
        
        return render_template('admin/estatisticas.html',
            total_eventos=total_eventos,
            eventos_por_mes=eventos_por_mes,
            eventos_por_categoria=eventos_por_categoria,
            eventos_por_status=eventos_por_status,
            proximos_eventos=proximos_eventos,
            eventos_passados=eventos_passados,
            eventos_gratuitos=eventos_gratuitos,
            eventos_pagos=eventos_pagos
        )
        
    except Exception as e:
        flash(f'Erro ao carregar estatísticas: {str(e)}', 'error')
        return redirect(url_for('admin_home'))

@app.route('/admin/evento/novo', methods=['GET', 'POST'])
@login_required
def admin_novo_evento():
    if request.method == 'POST':
        try:
            evento = Evento(
                titulo=request.form['titulo'],
                descricao=request.form['descricao'],
                data_evento=datetime.strptime(request.form['data_evento'], '%Y-%m-%d').date(),
                hora_inicio=datetime.strptime(request.form['hora_inicio'], '%H:%M').time(),
                hora_fim=datetime.strptime(request.form['hora_fim'], '%H:%M').time() if request.form['hora_fim'] else None,
                local=request.form['local'],
                endereco=request.form['endereco'],
                categoria=request.form['categoria'],
                organizador=request.form['organizador'],
                contato=request.form['contato'],
                preco=float(request.form['preco']) if request.form['preco'] else None,
                capacidade=int(request.form['capacidade']) if request.form['capacidade'] else None,
                usuario_id=current_user.id
            )
            
            db.session.add(evento)
            db.session.commit()
            flash('Evento cadastrado com sucesso!', 'success')
            return redirect(url_for('admin_eventos'))
        
        except Exception as e:
            flash(f'Erro ao cadastrar evento: {str(e)}', 'error')
            
    return render_template('admin/novo_evento.html')

@app.route('/admin/evento/<int:id>')
@login_required
def admin_detalhes_evento(id):
    evento = Evento.query.get_or_404(id)
    return render_template('admin/detalhes_evento.html', evento=evento)

@app.route('/admin/evento/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def admin_editar_evento(id):
    evento = Evento.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            evento.titulo = request.form['titulo']
            evento.descricao = request.form['descricao']
            evento.data_evento = datetime.strptime(request.form['data_evento'], '%Y-%m-%d').date()
            evento.hora_inicio = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
            evento.hora_fim = datetime.strptime(request.form['hora_fim'], '%H:%M').time() if request.form['hora_fim'] else None
            evento.local = request.form['local']
            evento.endereco = request.form['endereco']
            evento.categoria = request.form['categoria']
            evento.organizador = request.form['organizador']
            evento.contato = request.form['contato']
            evento.preco = float(request.form['preco']) if request.form['preco'] else None
            evento.capacidade = int(request.form['capacidade']) if request.form['capacidade'] else None
            
            db.session.commit()
            flash('Evento atualizado com sucesso!', 'success')
            return redirect(url_for('admin_detalhes_evento', id=id))
        
        except Exception as e:
            flash(f'Erro ao atualizar evento: {str(e)}', 'error')
            
    return render_template('admin/editar_evento.html', evento=evento)

@app.route('/admin/evento/<int:id>/deletar', methods=['POST'])
@login_required
def admin_deletar_evento(id):
    evento = Evento.query.get_or_404(id)
    evento.status = 'inativo'
    db.session.commit()
    flash('Evento removido com sucesso!', 'success')
    return redirect(url_for('admin_eventos'))

@app.route('/admin/perfil')
@login_required
def admin_perfil():
    return render_template('admin/perfil.html')

@app.route('/admin/perfil/editar', methods=['GET', 'POST'])
@login_required
def admin_editar_perfil():
    if request.method == 'POST':
        try:
            current_user.nome_completo = request.form['nome_completo']
            current_user.email = request.form['email']
            
            # Alterar senha se fornecida
            if request.form['nova_senha']:
                if current_user.check_password(request.form['senha_atual']):
                    current_user.set_password(request.form['nova_senha'])
                else:
                    flash('Senha atual incorreta.', 'error')
                    return render_template('admin/editar_perfil.html')
            
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('admin_perfil'))
        
        except Exception as e:
            flash(f'Erro ao atualizar perfil: {str(e)}', 'error')
    
    return render_template('admin/editar_perfil.html')

# APIs 

@app.route('/api/eventos')
def api_eventos():
    try:
        eventos = Evento.query.filter_by(status='ativo').all()
        eventos_json = [evento.to_dict() for evento in eventos]
        return jsonify(eventos_json)
    except Exception as e:
        print(f"Erro na API: {e}")
        return jsonify([])

@app.route('/api/eventos/<int:id>')
def api_evento_detalhes(id):
    evento = Evento.query.get_or_404(id)
    return jsonify(evento.to_dict())

@app.route('/api/estatisticas')
def api_estatisticas():
    try:
        eventos_categoria = db.session.query(
            Evento.categoria,
            db.func.count(Evento.id).label('total')
        ).filter_by(status='ativo').group_by(Evento.categoria).all()
        
        eventos_mes = db.session.query(
            db.extract('month', Evento.data_evento).label('mes'),
            db.func.count(Evento.id).label('total')
        ).filter_by(status='ativo').group_by(db.extract('month', Evento.data_evento)).all()
        
        return jsonify({
            'categorias': [{'categoria': cat, 'total': total} for cat, total in eventos_categoria],
            'meses': [{'mes': int(mes), 'total': total} for mes, total in eventos_mes]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

# INICIALIZAÇÃO 

def criar_usuario_admin():
    """Cria um usuário administrador padrão se não existir"""
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(
            username='admin',
            email='admin@eventosculturais.com',
            nome_completo='Administrador do Sistema'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Usuário administrador criado:")
        print("Username: admin")
        print("Senha: admin123")
        print("IMPORTANTE: Altere a senha após o primeiro login!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        criar_usuario_admin()
    app.run(debug=True, port=5328)
