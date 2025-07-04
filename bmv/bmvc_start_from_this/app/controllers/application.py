from bottle import template, request, redirect
import json
import os

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

        if not os.path.exists(self.upload_path):
            os.makedirs(self.upload_path)

    def _load_games(self):

        if not os.path.exists(self.games_db_path):
            os.makedirs(os.path.dirname(self.games_db_path), exist_ok=True)
            with open(self.games_db_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        with open(self.games_db_path, 'r', encoding='utf-8') as f:
            games_data = json.load(f)
            #converte cada dicionário da lista em um objeto Game
            return [Game.from_dict(data) for data in games_data]

    def _save_games(self, games):
        
        #converte a lista de objetos para uma lista de dicionários antes de salvar
        games_as_dicts = [game.to_dict() for game in games]
        with open(self.games_db_path, 'w', encoding='utf-8') as f:
            json.dump(games_as_dicts, f, indent=2, ensure_ascii=False)

    def render(self, page, **kwargs):
       content = self.pages.get(page, self.helper)
       return content(**kwargs)

    def helper(self):
        return template('app/views/html/helper')
    
    def GAMEVERSE(self):
        return template('app/views/html/GAMEVERSE')

    # --- CRUD para Jogos (Atualizado para usar a classe Game) ---

    def list_games(self):
        """(READ) Lista todos os jogos."""
        games = self._load_games()
        return template('app/views/html/games.html', games=games)

    def add_game(self):
        #cria uma nova instância da classe game com os dados do formulário, adiciona à lista e salva
        if request.method == 'POST':
            games = self._load_games()
            
            upload = request.files.get('cover_image')
            cover_image_url = '/static/img/GVV.png'
            if upload and upload.filename:
                save_path = os.path.join(self.upload_path, upload.filename)
                upload.save(save_path)
                cover_image_url = f"/static/img/covers/{upload.filename}"

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
        #acessa o .id do objeto
        game_to_edit = next((game for game in games if game.id == game_id), None)
        if not game_to_edit:
            return "Jogo não encontrado!"

        if request.method == 'POST':
            #atualiza os atributos do objeto diretamente
            game_to_edit.title = request.forms.get('title')
            game_to_edit.description = request.forms.get('description')

            upload = request.files.get('cover_image')
            if upload and upload.filename:
                if game_to_edit.cover_image and 'GVV.png' not in game_to_edit.cover_image:
                    old_image_path = os.path.join(os.path.dirname(__file__), '..', game_to_edit.cover_image.lstrip('/'))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                save_path = os.path.join(self.upload_path, upload.filename)
                upload.save(save_path)
                game_to_edit.cover_image = f"/static/img/covers/{upload.filename}"

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

        #compara o .id do objeto para filtrar a lista
        games_to_keep = [game for game in games if game.id != game_id]
        self._save_games(games_to_keep)
        redirect('/games')