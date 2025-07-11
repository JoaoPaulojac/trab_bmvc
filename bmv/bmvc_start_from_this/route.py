print("--- O SERVIDOR FOI REINICIADO COM O CÓDIGO MAIS RECENTE ---")

from app.controllers.application import Application
from bottle import Bottle, route, run, request, static_file, TEMPLATE_PATH
from bottle import redirect, template, response

TEMPLATE_PATH.insert(0, './app/views/html/')

app = Bottle()
ctl = Application()

#-----------------------------------------------------------------------------
# Rotas:

@app.route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./app/static')

@app.route('/helper')
def helper(info= None):
    return ctl.render('helper')

#-----------------------------------------------------------------------------
# Suas rotas aqui:

@app.route('/')
def root():
    """Redireciona a rota raiz para a página principal."""
    redirect('/GAMEVERSE')

@app.route('/GAMEVERSE')
def action_GAMEVERSE():
    return ctl.GAMEVERSE()

@app.route('/register', method=['GET', 'POST'])
def register():
    return ctl.register()

@app.route('/login', method=['GET', 'POST'])
def login():
    return ctl.login()

@app.route('/logout')
def logout():
    return ctl.logout()

# --- Rotas para o CRUD de Jogos ---

@app.route('/games')
def list_games():
    """Rota para listar todos os jogos com CRUD (privado)."""
    user_email = request.get_cookie("user_email", secret='uma-chave-secreta-muito-forte')
    if not user_email:
        redirect('/GAMEVERSE?login=true')
    return ctl.list_games()

@app.route('/games_public')
def list_games_public():
    """Rota para listar todos os jogos publicamente."""
    return ctl.list_games_public()

@app.route('/games/add', method=['GET', 'POST'])
def add_game():
    user_email = request.get_cookie("user_email", secret='uma-chave-secreta-muito-forte')
    if not user_email:
        redirect('/GAMEVERSE')
    return ctl.add_game()

@app.route('/games/edit/<game_id:int>', method=['GET', 'POST'])
def edit_game(game_id):
    user_email = request.get_cookie("user_email", secret='uma-chave-secreta-muito-forte')
    if not user_email:
        redirect('/GAMEVERSE')
    return ctl.edit_game(game_id)

@app.route('/games/delete/<game_id:int>')
def delete_game(game_id):
    user_email = request.get_cookie("user_email", secret='uma-chave-secreta-muito-forte')
    if not user_email:
        redirect('/GAMEVERSE')
    return ctl.delete_game(game_id)

# --- Rotas da Conta do Usuário ---

@app.route('/account')
def user_account():
    return ctl.user_account()

@app.route('/account/edit', method=['POST'])
def edit_user():
    return ctl.edit_user()

@app.route('/account/delete')
def delete_user():
    return ctl.delete_user()

#-----------------------------------------------------------------------------

if __name__ == '__main__':
    run(app, host='localhost', port=8080, reloader=True)