from bottle import template, request, redirect, response
import json
import os
import bcrypt
import time # Import the time module

class User:
    # __init__ é usado para criar NOVOS usuários (ex: no cadastro)
    def __init__(self, email, password, username, profile_image, id=None):
        if not email or not password or not username:
            raise ValueError("Email, senha e nome de usuário não podem ser vazios")
        self.id = id
        self.email = email
        self.username = username
        self.profile_image = profile_image
        # Gera o hash da senha ao criar o usuário
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        # Verifica se a senha fornecida corresponde ao hash armazenado
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "profile_image": self.profile_image,
            "password_hash": self.password_hash.decode('utf-8')
        }

    # from_dict é usado para carregar usuários do JSON (onde a senha já está em hash)
    @classmethod
    def from_dict(cls, data):
        # Se um usuário no JSON não tiver email ou hash, é inválido e será ignorado.
        if not data.get('email') or not data.get('password_hash'):
            return None

        # Criamos uma instância vazia para preencher com os dados do JSON.
        # Isso evita chamar o __init__, que espera uma senha em texto plano.
        user = cls.__new__(cls)
        user.id = data.get('id')
        user.email = data.get('email')
        # Adiciona valores padrão para campos que podem não existir em usuários antigos.
        user.username = data.get('username', 'Usuário')
        user.profile_image = data.get('profile_image', '/static/img/profile/default.png')
        user.password_hash = data.get('password_hash').encode('utf-8')
        return user


class Game:
    def __init__(self, id, title, description, cover_image):
        if not title or not description:
            raise ValueError("Título e descrição não podem ser vazios")
        self.id = id
        self.title = title
        self.description = description
        self.cover_image = cover_image

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "cover_image": self.cover_image
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            title=data.get('title'),
            description=data.get('description'),
            cover_image=data.get('cover_image')
        )

class Application():
    def __init__(self):
        self.pages = {
            'GAMEVERSE': self.GAMEVERSE,
            'games': self.list_games,
            'add_game': self.add_game,
            'edit_game': self.edit_game
        }
        self.games_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'games.json')
        self.upload_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'img', 'covers')
        self.profile_upload_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'img', 'profile')
        self.users_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'users.json')

        if not os.path.exists(self.upload_path):
            os.makedirs(self.upload_path)
        if not os.path.exists(self.profile_upload_path):
            os.makedirs(self.profile_upload_path)

    #funcoes para login
    def _load_users(self):
        if not os.path.exists(self.users_db_path):
            return []
        with open(self.users_db_path, 'r', encoding='utf-8') as f:
            try:
                users_data = json.load(f)
                if not isinstance(users_data, list): # Garante que o JSON é uma lista
                    return []
            except json.JSONDecodeError:
                return [] # Retorna lista vazia se o JSON estiver mal formatado

            # Processa os usuários e filtra entradas inválidas (que retornaram None)
            loaded_users = [User.from_dict(data) for data in users_data]
            return [user for user in loaded_users if user is not None]

    def _save_users(self, users):
        users_as_dicts = [user.to_dict() for user in users]
        with open(self.users_db_path, 'w', encoding='utf-8') as f:
            json.dump(users_as_dicts, f, indent=2, ensure_ascii=False)

    # funcao para os jogos
    def _load_games(self):
        if not os.path.exists(self.games_db_path):
            os.makedirs(os.path.dirname(self.games_db_path), exist_ok=True)
            with open(self.games_db_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

        with open(self.games_db_path, 'r', encoding='utf-8') as f:
            games_data = json.load(f)
            return [Game.from_dict(data) for data in games_data]

    def _save_games(self, games):
        games_as_dicts = [game.to_dict() for game in games]
        with open(self.games_db_path, 'w', encoding='utf-8') as f:
            json.dump(games_as_dicts, f, indent=2, ensure_ascii=False)

    def render(self, page, **kwargs):
       content = self.pages.get(page, self.helper)
       return content(**kwargs)

    def helper(self):
        return template('app/views/html/helper')

    def GAMEVERSE(self):
        user_email = request.get_cookie("user_email", secret='uma-chave-secreta-muito-forte')
        user = None
        if user_email:
            users = self._load_users()
            user = next((u for u in users if u.email == user_email), None)
        return template('app/views/html/GAMEVERSE.html', user=user)

    # --- CRUD para Jogos ---
    def list_games(self):
        games = self._load_games()
        user_email = request.get_cookie("user_email", secret='uma-chave-secreta-muito-forte')
        user = None
        if user_email:
            users = self._load_users()
            user = next((u for u in users if u.email == user_email), None)
        return template('app/views/html/games.html', games=games, user=user)

    def list_games_public(self):
        games = self._load_games()
        return template('app/views/html/games_public.html', games=games)

    def add_game(self):
        if request.method == 'POST':
            games = self._load_games()
            upload = request.files.get('cover_image')
            cover_image_url = '/static/img/GVV.png'
            if upload and upload.filename:
                # Gerar nome de arquivo único para a capa do jogo
                name, ext = os.path.splitext(upload.filename)
                unique_filename = f"{name}_{int(time.time())}{ext}"
                save_path = os.path.join(self.upload_path, unique_filename)
                upload.save(save_path)
                cover_image_url = f"/static/img/covers/{unique_filename}"

            new_id = max((game.id for game in games), default=0) + 1
            new_game = Game(
                id=new_id,
                title=request.forms.get('title'),
                description=request.forms.get('description'),
                cover_image=cover_image_url
            )
            games.append(new_game)
            self._save_games(games)
            redirect('/games')
        return template('app/views/html/add_game.html')

    def edit_game(self, game_id):
        games = self._load_games()
        game_to_edit = next((game for game in games if game.id == game_id), None)
        if not game_to_edit:
            return "Jogo não encontrado!"

        if request.method == 'POST':
            game_to_edit.title = request.forms.get('title')
            game_to_edit.description = request.forms.get('description')
            upload = request.files.get('cover_image')
            if upload and upload.filename:
                # Gerar nome de arquivo único para a capa do jogo (também na edição)
                name, ext = os.path.splitext(upload.filename)
                unique_filename = f"{name}_{int(time.time())}{ext}"
                save_path = os.path.join(self.upload_path, unique_filename)
                
                # Apagar imagem antiga se não for a padrão
                if game_to_edit.cover_image and 'GVV.png' not in game_to_edit.cover_image:
                    old_image_path = os.path.join(os.path.dirname(__file__), '..', game_to_edit.cover_image.lstrip('/'))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                upload.save(save_path)
                game_to_edit.cover_image = f"/static/img/covers/{unique_filename}"

            self._save_games(games)
            redirect('/games')
        return template('app/views/html/edit_game.html', game=game_to_edit)

    def delete_game(self, game_id):
        games = self._load_games()
        game_to_delete = next((game for game in games if game.id == game_id), None)

        if game_to_delete:
            cover_path = game_to_delete.cover_image
            if cover_path and 'GVV.png' not in cover_path:
                file_path = os.path.join(os.path.dirname(__file__), '..', cover_path.lstrip('/'))
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except OSError as e:
                    print(f"Erro ao deletar o arquivo {file_path}: {e}")

        games_to_keep = [game for game in games if game.id != game_id]
        self._save_games(games_to_keep)
        redirect('/games')

    def register(self):
        error = None
        if request.method == 'POST':
            email = request.forms.get('email')
            password = request.forms.get('password')
            username = request.forms.get('username')
            users = self._load_users()

            if any(user.email == email for user in users):
                error = "Este email já está cadastrado."
            else:
                profile_image_url = '/static/img/profile/default.png'
                upload = request.files.get('profile_image')
                if upload and upload.filename:
                    # >>> AQUI ESTÁ A CORREÇÃO <<<
                    # Pega o nome e a extensão do arquivo
                    name, ext = os.path.splitext(upload.filename)
                    # Cria um nome de arquivo único adicionando o tempo atual (timestamp)
                    unique_filename = f"{name}_{int(time.time())}{ext}"
                    # Define o caminho para salvar com o novo nome
                    save_path = os.path.join(self.profile_upload_path, unique_filename)
                    
                    upload.save(save_path) # Salva o arquivo com o nome único
                    
                    # Armazena o caminho com o nome único no banco de dados
                    profile_image_url = f"/static/img/profile/{unique_filename}"

                new_id = max((user.id for user in users), default=0) + 1
                new_user = User(id=new_id, email=email, password=password, username=username, profile_image=profile_image_url)
                users.append(new_user)
                self._save_users(users)
                redirect('/login')

        return template('app/views/html/register.html', error=error)

    def login(self):
        error = None
        if request.method == 'POST':
            email = request.forms.get('email')
            password = request.forms.get('password')
            users = self._load_users()

            user = next((u for u in users if u.email == email), None)

            if user and user.check_password(password):
                response.set_cookie("user_email", user.email, secret='uma-chave-secreta-muito-forte')
                redirect('/GAMEVERSE')
            else:
                error = "Email ou senha inválidos."
        
        # O template é renderizado fora do if, mas com a variável de erro, se houver
        return template('app/views/html/GAMEVERSE.html', login_error=error)

    def logout(self):
        response.delete_cookie("user_email")
        redirect('/GAMEVERSE')