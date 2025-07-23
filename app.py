# app.py (Versão Final com Controle de Acesso por Perfil)

import os
import uuid
import numpy as np
import faiss
from flask import Flask, request, render_template, url_for, redirect, flash, jsonify, abort
from werkzeug.utils import secure_filename
import face_recognition
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from datetime import date, datetime, timedelta

# --- CONFIGURAÇÃO INICIAL ---
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Configurações da Aplicação
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-for-local-use-only')

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
DB_IMAGES_FOLDER = os.path.join(basedir, 'static', 'db_images')
SIGHTING_IMAGES_FOLDER = os.path.join(basedir, 'static', 'sighting_images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DB_IMAGES_FOLDER, exist_ok=True)
os.makedirs(SIGHTING_IMAGES_FOLDER, exist_ok=True)
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
FAISS_SIMILARITY_THRESHOLD = float(os.environ.get('FAISS_SIMILARITY_THRESHOLD', 0.36))
FAISS_SIMILARITY_FOR_SUGGESTIONS = 0.45

# --- MODELOS DO BANCO DE DADOS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=True, default=None)
    # <-- MUDANÇA AQUI: Adiciona o campo de perfil (role)
    role = db.Column(db.String(80), nullable=False, default='USUARIO')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=True, default='Em Observação')
    doc_number = db.Column(db.String(50), nullable=True, unique=True)
    face_encoding = db.Column(db.LargeBinary, nullable=False)
    registration_date = db.Column(db.DateTime, default=db.func.now())
    notes = db.Column(db.Text, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    father_name = db.Column(db.String(100), nullable=True)
    mother_name = db.Column(db.String(100), nullable=True)
    spouse = db.Column(db.String(255), nullable=True)
    children = db.Column(db.Text, nullable=True)
    phones = db.Column(db.String(255), nullable=True)
    emails = db.Column(db.String(255), nullable=True)
    address = db.Column(db.Text, nullable=True)
    photos = db.relationship('Photo', backref='person', lazy=True, cascade="all, delete-orphan")
    # <-- MUDANÇA AQUI: Adiciona a relação com o usuário que criou o perfil
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False, unique=True)
    photo_type = db.Column(db.String(50), nullable=False, default='sighting')
    upload_date = db.Column(db.DateTime, default=db.func.now())
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)

# --- FUNÇÕES AUXILIARES ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def save_faiss_index():
    global faiss_index
    try:
        faiss.write_index(faiss_index, FAISS_INDEX_PATH)
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
    save_faiss_index()

def load_or_build_faiss_index():
    global faiss_index
    if os.path.exists(FAISS_INDEX_PATH):
        try:
            faiss_index = faiss.read_index(FAISS_INDEX_PATH)
            with app.app_context():
                db_count = Person.query.count()
                if faiss_index.ntotal != db_count:
                    build_faiss_from_db()
        except Exception as e:
            build_faiss_from_db()
    else:
        build_faiss_from_db()

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            if user.expiration_date is not None and user.expiration_date < datetime.utcnow():
                flash('Sua conta expirou. Por favor, contate um administrador.', 'error')
                return redirect(url_for('login'))
            
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
    # <-- MUDANÇA AQUI: Dashboard agora reflete os dados do usuário ou todos (se admin)
    if current_user.role == 'ADMIN':
        profiles_query = Person.query
    else:
        profiles_query = Person.query.filter_by(user_id=current_user.id)

    total_profiles = profiles_query.count()
    profile_ids = [p.id for p in profiles_query.all()]

    if profile_ids:
        status_counts = db.session.query(Person.status, db.func.count(Person.status)).filter(Person.id.in_(profile_ids)).group_by(Person.status).all()
    else:
        status_counts = []
    
    color_map = { 'Em Observação': 'rgba(240, 173, 78, 0.7)', 'Ativo': 'rgba(92, 184, 92, 0.7)', 'Procurado': 'rgba(248, 81, 73, 0.7)', 'Inativo': 'rgba(139, 148, 158, 0.7)', 'Não Especificado': 'rgba(88, 166, 255, 0.7)' }
    status_labels = [status if status else 'Não Especificado' for status, count in status_counts]
    status_data = [count for status, count in status_counts]
    background_colors = [color_map.get(label, 'rgba(139, 148, 158, 0.7)') for label in status_labels]
    status_chart_data = { 'labels': status_labels, 'data': status_data, 'colors': background_colors }
    recent_profiles = profiles_query.order_by(Person.registration_date.desc()).limit(5).all()
    
    return render_template('dashboard.html', total_profiles=total_profiles, status_chart_data=status_chart_data, recent_profiles=recent_profiles)

@app.route('/search', methods=['POST'])
@login_required
def search():
    if 'image' not in request.files: return jsonify({'error': 'Nenhum arquivo de imagem selecionado.'}), 400
    file = request.files['image']
    if not file.filename: return jsonify({'error': 'Nome de arquivo inválido.'}), 400
    
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.stream.seek(0)
    file.save(temp_path)
    
    try:
        search_image = face_recognition.load_image_file(temp_path)
        search_encodings = face_recognition.face_encodings(search_image)
    except Exception as e:
        os.remove(temp_path)
        return jsonify({'error': f'Não foi possível processar a imagem: {e}'}), 500
    
    if not search_encodings: os.remove(temp_path); return jsonify({'status': 'Nenhum rosto detectado na imagem.'})
    if len(search_encodings) > 1: os.remove(temp_path); return jsonify({'error': f'Múltiplos rostos ({len(search_encodings)}) detectados.'}), 400
    
    search_encoding = np.array(search_encodings[0]).astype('float32').reshape(1, -1)
    if faiss_index.ntotal == 0: os.remove(temp_path); return jsonify({'status': 'Nenhum perfil cadastrado para comparação.'})
    
    distances, ids = faiss_index.search(search_encoding, 1)
    
    if ids[0][0] != -1 and distances[0][0] <= FAISS_SIMILARITY_THRESHOLD:
        person_id = int(ids[0][0])
        matched_person = Person.query.get(person_id)
        if matched_person:
            # <-- MUDANÇA AQUI: Verifica se o usuário tem permissão para ver o resultado da busca
            if matched_person.user_id != current_user.id and current_user.role != 'ADMIN':
                os.remove(temp_path)
                return jsonify({'status': 'Nenhuma correspondência encontrada.'})

            sighting_filename = f"sighting_{person_id}_{uuid.uuid4().hex[:8]}.jpg"
            sighting_path = os.path.join(SIGHTING_IMAGES_FOLDER, sighting_filename)
            os.rename(temp_path, sighting_path)
            new_sighting = Photo(filename=sighting_filename, photo_type='sighting', person_id=person_id)
            profile_photo = Photo.query.filter_by(person_id=matched_person.id, photo_type='profile').first()
            profile_photo_url = url_for('static', filename=f'db_images/{profile_photo.filename}') if profile_photo else ''
            db.session.add(new_sighting)
            db.session.commit()
            
            return jsonify({ 'status': 'success', 'person': { 'id': matched_person.id, 'name': matched_person.name, 'image_url': profile_photo_url, 'detail_url': url_for('person_detail', person_id=matched_person.id) } })
    
    os.remove(temp_path)
    return jsonify({'status': 'Nenhuma correspondência encontrada.'})

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        file = request.files.get('image')
        if not name or not file or not file.filename:
            flash('Nome e imagem são obrigatórios.', 'error')
            return redirect(request.url)

        profile_filename = secure_filename(f"profile_{name.replace(' ', '_').lower()}_{os.urandom(4).hex()}.jpg")
        path = os.path.join(DB_IMAGES_FOLDER, profile_filename)
        file.save(path)

        try:
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
        except Exception as e:
            os.remove(path); flash(f'Erro ao processar a imagem: {e}.', 'error'); return redirect(request.url)

        if not encodings or len(encodings) > 1:
            os.remove(path); flash('Nenhum rosto ou múltiplos rostos detectados.', 'warning'); return redirect(request.url)
        
        encoding_bytes = encodings[0].tobytes()
        dob_str = request.form.get('date_of_birth')
        date_of_birth_obj = date.fromisoformat(dob_str) if dob_str else None

        # <-- MUDANÇA AQUI: Associa o perfil criado ao usuário logado
        new_person = Person(name=name, face_encoding=encoding_bytes, status=request.form.get('status', 'Em Observação'), doc_number=request.form.get('doc_number'), date_of_birth=date_of_birth_obj, gender=request.form.get('gender'), address=request.form.get('address'), phones=request.form.get('phones'), emails=request.form.get('emails'), father_name=request.form.get('father_name'), mother_name=request.form.get('mother_name'), spouse=request.form.get('spouse'), children=request.form.get('children'), notes=request.form.get('notes'), user_id=current_user.id)
        
        try:
            db.session.add(new_person)
            db.session.flush()
            profile_photo = Photo(filename=profile_filename, photo_type='profile', person_id=new_person.id)
            db.session.add(profile_photo)
            db.session.commit()
            new_encoding = np.array(encodings[0]).astype('float32').reshape(1, -1)
            faiss_index.add_with_ids(new_encoding, np.array([new_person.id]))
            save_faiss_index()
            flash(f'Perfil de {name} cadastrado com sucesso!', 'success')
            return redirect(url_for('gallery'))
        except Exception as e:
            db.session.rollback(); os.remove(path); flash(f'Erro ao salvar no banco de dados: {e}.', 'error'); return redirect(request.url)

    return render_template('register.html')

@app.route('/gallery/')
@app.route('/gallery/page/<int:page>')
@login_required
def gallery(page=1):
    search_query = request.args.get('query', '')
    
    # <-- MUDANÇA AQUI: Filtra a galeria por usuário ou mostra tudo para o ADMIN
    if current_user.role == 'ADMIN':
        base_query = Person.query
    else:
        base_query = Person.query.filter_by(user_id=current_user.id)

    if search_query:
        search_term = f"%{search_query}%"
        base_query = base_query.filter(or_(Person.name.ilike(search_term), Person.doc_number.ilike(search_term), Person.status.ilike(search_term), Person.address.ilike(search_term)))
    
    people = base_query.order_by(Person.registration_date.desc()).paginate(page=page, per_page=12)
    return render_template('gallery.html', people=people, search_query=search_query)

@app.route('/person/<int:person_id>')
@login_required
def person_detail(person_id):
    person = Person.query.get_or_404(person_id)

    # <-- MUDANÇA AQUI: Checagem de permissão baseada em perfil
    if person.user_id != current_user.id and current_user.role != 'ADMIN':
        abort(403)

    similar_people = []
    if faiss_index.ntotal > 1:
        person_encoding = np.frombuffer(person.face_encoding, dtype=np.float64).astype('float32').reshape(1, -1)
        distances, ids = faiss_index.search(person_encoding, k=10)
        possible_ids = []
        for i, dist in enumerate(distances[0]):
            match_id = ids[0][i]
            if match_id != person.id and match_id != -1 and dist <= FAISS_SIMILARITY_FOR_SUGGESTIONS:
                possible_ids.append(match_id)
        if possible_ids:
            if current_user.role == 'ADMIN':
                similar_people = Person.query.filter(Person.id.in_(possible_ids)).all()
            else:
                # Usuário comum só vê sugestões dos perfis que ele mesmo cadastrou
                similar_people = Person.query.filter(Person.id.in_(possible_ids), Person.user_id == current_user.id).all()

    return render_template('person_detail.html', person=person, similar_people=similar_people)

@app.route('/person/<int:person_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_person(person_id):
    person = Person.query.get_or_404(person_id)
    
    # <-- MUDANÇA AQUI: Checagem de permissão baseada em perfil
    if person.user_id != current_user.id and current_user.role != 'ADMIN':
        abort(403)

    if request.method == 'POST':
        try:
            person.name = request.form.get('name')
            person.status = request.form.get('status')
            person.doc_number = request.form.get('doc_number')
            dob_str = request.form.get('date_of_birth')
            person.date_of_birth = date.fromisoformat(dob_str) if dob_str else None
            person.gender = request.form.get('gender')
            person.father_name = request.form.get('father_name')
            person.mother_name = request.form.get('mother_name')
            person.spouse = request.form.get('spouse')
            person.children = request.form.get('children')
            person.phones = request.form.get('phones')
            person.emails = request.form.get('emails')
            person.address = request.form.get('address')
            person.notes = request.form.get('notes')
            
            db.session.commit()
            flash('Dossiê atualizado com sucesso!', 'success')
            return redirect(url_for('person_detail', person_id=person.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar o dossiê: {e}', 'error')
    return render_template('edit_person.html', person=person)

@app.route('/delete/<int:person_id>', methods=['POST'])
@login_required
def delete(person_id):
    person_to_delete = Person.query.get_or_404(person_id)
    
    # <-- MUDANÇA AQUI: Checagem de permissão baseada em perfil
    if person_to_delete.user_id != current_user.id and current_user.role != 'ADMIN':
        abort(403)

    if faiss_index.ntotal > 0:
        try:
            faiss_index.remove_ids(np.array([person_to_delete.id]))
            save_faiss_index()
        except Exception as e:
            print(f"Alerta: ID {person_to_delete.id} não encontrado no índice FAISS. Reconstruindo...")
            build_faiss_from_db()

    for photo in person_to_delete.photos:
        folder = SIGHTING_IMAGES_FOLDER if photo.photo_type == 'sighting' else DB_IMAGES_FOLDER
        image_path = os.path.join(folder, photo.filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(person_to_delete)
    db.session.commit()
    flash(f'{person_to_delete.name} foi deletado com sucesso.', 'success')
    return redirect(url_for('gallery'))


# --- INÍCIO DA IMPLEMENTAÇÃO DE GERENCIAMENTO DE USUÁRIOS ---

@app.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    # <-- MUDANÇA AQUI: Acesso apenas para o perfil ADMIN
    if current_user.role != 'ADMIN':
        abort(403)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        expiration_type = request.form.get('expiration_type')

        if not username or not password or not expiration_type:
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('manage_users'))

        if User.query.filter_by(username=username).first():
            flash('Este nome de usuário já existe.', 'error')
            return redirect(url_for('manage_users'))

        new_user = User(username=username)
        new_user.set_password(password)

        if expiration_type == '1_day':
            new_user.expiration_date = datetime.utcnow() + timedelta(days=1)
        elif expiration_type == '1_month':
            new_user.expiration_date = datetime.utcnow() + timedelta(days=30)
        elif expiration_type == '1_year':
            new_user.expiration_date = datetime.utcnow() + timedelta(days=365)

        db.session.add(new_user)
        db.session.commit()
        flash(f'Usuário {username} criado com sucesso!', 'success')
        return redirect(url_for('manage_users'))

    users = User.query.order_by(User.id).all()
    return render_template('manage_users.html', users=users)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    # <-- MUDANÇA AQUI: Acesso apenas para o perfil ADMIN
    if current_user.role != 'ADMIN':
        abort(403)
    
    user_to_delete = User.query.get_or_404(user_id)

    # <-- MUDANÇA AQUI: Protege a conta de administrador principal de ser deletada
    if user_to_delete.id == 1:
        flash('A conta de administrador principal não pode ser deletada.', 'warning')
        return redirect(url_for('manage_users'))

    db.session.delete(user_to_delete)
    db.session.commit()
    flash('Usuário deletado com sucesso.', 'success')
    return redirect(url_for('manage_users'))

# --- FIM DA IMPLEMENTAÇÃO ---


# --- INICIALIZAÇÃO E COMANDOS CLI ---
@app.cli.command("init-db")
def init_db_command():
    with app.app_context():
        db.create_all()
    print("Banco de dados inicializado.")

@app.cli.command("create-admin")
def create_admin():
    if User.query.filter_by(username='admin').first():
        print("Usuário 'admin' já existe.")
        return
    # <-- MUDANÇA AQUI: Define o perfil do usuário admin como 'ADMIN'
    admin = User(username='admin', role='ADMIN')
    admin.set_password('admin')
    db.session.add(admin)
    db.session.commit()
    print("Usuário 'admin' criado com sucesso. Senha padrão: admin")

if __name__ == '__main__':
    with app.app_context():
        load_or_build_faiss_index()
    app.run(debug=True)