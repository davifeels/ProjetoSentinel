# app.py (Versão Final, Robusta e com Persistência FAISS)

import os
import numpy as np
import faiss
from flask import Flask, request, render_template, url_for, redirect, flash, jsonify
from werkzeug.utils import secure_filename
import face_recognition
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

# --- CONFIGURAÇÃO INICIAL ---
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Configurações da Aplicação
# Usa a variável de ambiente para Docker/PostgreSQL, mas volta para SQLite se não estiver definida.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar'
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
DB_IMAGES_FOLDER = os.path.join(basedir, 'static', 'db_images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DB_IMAGES_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# --- CONFIGURAÇÃO DO SISTEMA DE LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

# --- CONFIGURAÇÃO DO FAISS ---
FAISS_DIMENSION = 128
faiss_index = faiss.IndexIDMap(faiss.IndexFlatL2(FAISS_DIMENSION))
FAISS_INDEX_PATH = os.path.join(basedir, 'faiss_index.bin')
# Limiar de similaridade (distância L2). 0.36 é o quadrado de 0.6 (distância Euclidiana)
FAISS_SIMILARITY_THRESHOLD = 0.36

# --- MODELOS DO BANCO DE DADOS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=True, default='Em Observação')
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(2), nullable=True)
    doc_number = db.Column(db.String(50), nullable=True, unique=True)
    notes = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(100), nullable=False, unique=True)
    face_encoding = db.Column(db.LargeBinary, nullable=False)
    registration_date = db.Column(db.DateTime, default=db.func.now())

# --- FUNÇÕES AUXILIARES ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def save_faiss_index():
    global faiss_index
    try:
        faiss.write_index(faiss_index, FAISS_INDEX_PATH)
        print(f"Índice FAISS salvo. Total de vetores: {faiss_index.ntotal}")
    except Exception as e:
        print(f"Erro ao salvar o índice FAISS: {e}")

def build_faiss_from_db():
    global faiss_index
    faiss_index = faiss.IndexIDMap(faiss.IndexFlatL2(FAISS_DIMENSION))
    with app.app_context():
        people = Person.query.all()
        if people:
            encodings = np.array([np.frombuffer(p.face_encoding, dtype=np.float64) for p in people]).astype('float32')
            ids = np.array([p.id for p in people])
            faiss_index.add_with_ids(encodings, ids)
    print(f"Índice FAISS (re)construído do banco de dados com {faiss_index.ntotal} vetores.")
    save_faiss_index()

def load_or_build_faiss_index():
    global faiss_index
    if os.path.exists(FAISS_INDEX_PATH):
        try:
            faiss_index = faiss.read_index(FAISS_INDEX_PATH)
            print(f"Índice FAISS carregado. Total de vetores: {faiss_index.ntotal}")
            with app.app_context():
                db_count = Person.query.count()
                if faiss_index.ntotal != db_count:
                    print(f"AVISO: Inconsistência detectada (FAISS: {faiss_index.ntotal}, DB: {db_count}). Reconstruindo índice...")
                    build_faiss_from_db()
        except Exception as e:
            print(f"Erro ao carregar índice FAISS: {e}. Reconstruindo do zero.")
            build_faiss_from_db()
    else:
        print("Arquivo de índice FAISS não encontrado. Construindo do zero.")
        build_faiss_from_db()

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- ROTAS DA APLICAÇÃO ---
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    total_profiles = Person.query.count()
    status_counts = db.session.query(Person.status, db.func.count(Person.status)).group_by(Person.status).all()
    status_labels = [status for status, count in status_counts]
    status_data = [count for status, count in status_counts]
    status_chart_data = {'labels': status_labels, 'data': status_data}
    recent_profiles = Person.query.order_by(Person.registration_date.desc()).limit(5).all()
    return render_template('dashboard.html', total_profiles=total_profiles, status_chart_data=status_chart_data, recent_profiles=recent_profiles)

@app.route('/search', methods=['POST'])
@login_required
def search():
    if 'image' not in request.files or not request.files['image'].filename:
        return jsonify({'error': 'Nenhum arquivo de imagem selecionado.'}), 400
    
    file = request.files['image']
    search_path = ""
    try:
        search_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(search_path)
        search_image = face_recognition.load_image_file(search_path)
        search_encodings = face_recognition.face_encodings(search_image)
    except Exception as e:
        return jsonify({'error': f'Não foi possível processar a imagem: {e}'}), 500
    finally:
        # Garante que a imagem temporária seja sempre deletada, mesmo se houver erro
        if os.path.exists(search_path):
            os.remove(search_path)

    if not search_encodings:
        return jsonify({'status': 'Nenhum rosto detectado na imagem.'})
    
    search_encoding = np.array(search_encodings[0]).astype('float32').reshape(1, -1)
    
    if faiss_index.ntotal == 0:
        return jsonify({'status': 'Nenhum perfil cadastrado para comparação.'})
    
    distances, ids = faiss_index.search(search_encoding, 1)
    
    print(f"Distância encontrada: {distances[0][0]}, Limiar: {FAISS_SIMILARITY_THRESHOLD}")

    if ids[0][0] != -1 and distances[0][0] <= FAISS_SIMILARITY_THRESHOLD:
        person_id = int(ids[0][0])
        matched_person = Person.query.get(person_id)
        if matched_person:
            return jsonify({'status': 'success', 'person': {'id': matched_person.id, 'name': matched_person.name, 'image_url': url_for('static', filename=f'db_images/{matched_person.image_filename}'), 'detail_url': url_for('person_detail', person_id=matched_person.id)}})
        else:
            return jsonify({'status': 'Erro: Correspondência encontrada, mas perfil não existe no DB.'})
    else:
        return jsonify({'status': 'Nenhuma correspondência encontrada.'})

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        status = request.form.get('status')
        city = request.form.get('city')
        state = request.form.get('state')
        doc_number = request.form.get('doc_number')
        notes = request.form.get('notes')
        file = request.files.get('image')

        if not name or not file or not file.filename:
            flash('Nome e imagem são obrigatórios.', 'error')
            return redirect(request.url)

        filename = secure_filename(f"{name.replace(' ', '_').lower()}_{os.urandom(4).hex()}.jpg")
        path = os.path.join(DB_IMAGES_FOLDER, filename)
        file.save(path)

        try:
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
        except Exception as e:
            os.remove(path)
            flash(f'Erro ao processar a imagem: {e}. Cadastro cancelado.', 'error')
            return redirect(request.url)

        if not encodings:
            os.remove(path)
            flash('Nenhum rosto detectado na imagem. Cadastro cancelado.', 'warning')
            return redirect(request.url)
        
        encoding_bytes = encodings[0].tobytes()
        
        new_person = Person(name=name, age=int(age) if age else None, status=status, city=city, state=state, doc_number=doc_number, notes=notes, image_filename=filename, face_encoding=encoding_bytes)
        
        try:
            db.session.add(new_person)
            db.session.commit()
            
            new_encoding = np.array(encodings[0]).astype('float32').reshape(1, -1)
            faiss_index.add_with_ids(new_encoding, np.array([new_person.id]))
            save_faiss_index() # Salva o índice atualizado
            
            flash(f'Perfil de {name} cadastrado com sucesso!', 'success')
            return redirect(url_for('gallery'))
        except Exception as e:
            db.session.rollback()
            os.remove(path)
            flash(f'Erro ao salvar o perfil no banco de dados: {e}.', 'error')
            return redirect(request.url)

    return render_template('register.html')

@app.route('/gallery/')
@app.route('/gallery/page/<int:page>')
@login_required
def gallery(page=1):
    search_query = request.args.get('query', '')
    base_query = Person.query
    if search_query:
        search_term = f"%{search_query}%"
        base_query = base_query.filter(or_(Person.name.ilike(search_term), Person.doc_number.ilike(search_term), Person.city.ilike(search_term), Person.status.ilike(search_term)))
    people = base_query.order_by(Person.registration_date.desc()).paginate(page=page, per_page=12)
    return render_template('gallery.html', people=people, search_query=search_query)

@app.route('/person/<int:person_id>')
@login_required
def person_detail(person_id):
    person = Person.query.get_or_404(person_id)
    return render_template('person_detail.html', person=person)

@app.route('/delete/<int:person_id>', methods=['POST'])
@login_required
def delete(person_id):
    person_to_delete = Person.query.get_or_404(person_id)
    
    if faiss_index.ntotal > 0:
        try:
            faiss_index.remove_ids(np.array([person_to_delete.id]))
            save_faiss_index() # Salva o índice atualizado
        except Exception as e:
            print(f"Erro ao remover ID {person_to_delete.id} do FAISS: {e}")

    image_path = os.path.join(DB_IMAGES_FOLDER, person_to_delete.image_filename)
    if os.path.exists(image_path):
        os.remove(image_path)
    
    db.session.delete(person_to_delete)
    db.session.commit()
    flash(f'{person_to_delete.name} foi deletado com sucesso.', 'success')
    return redirect(url_for('gallery'))

# --- INICIALIZAÇÃO E COMANDOS CLI ---
@app.cli.command("init-db")
def init_db_command():
    with app.app_context():
        db.create_all()
    print("Banco de dados inicializado e tabelas criadas com sucesso.")

@app.cli.command("create-admin")
def create_admin():
    with app.app_context():
        if User.query.filter_by(username='admin').first():
            print("Usuário 'admin' já existe.")
            return
        admin = User(username='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
    print("Usuário 'admin' criado com sucesso. Senha: 'admin'")

if __name__ == '__main__':
    with app.app_context():
        load_or_build_faiss_index()
    app.run(debug=True)
