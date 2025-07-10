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

@app.route('/GAMEVERSE', method=['GET'])
def action_GAMEVERSE():
    return ctl.render('GAMEVERSE')

@app.route('/register', method=['GET', 'POST'])
def register():
    return ctl.register()

@app.route('/login', method=['GET', 'POST'])
def login():
    return ctl.login()

@app.route('/logout', method=['GET'])
def logout():
    return ctl.logout()

# --- Novas Rotas para o CRUD de Jogos ---

@app.route('/games', method=['GET'])
def list_games():
    """Rota para listar todos os jogos."""
    return ctl.list_games()

# Em route.py
@app.route('/games/add', method=['GET', 'POST'])
def add_game():
    user_email = request.get_cookie("user_email", secret='uma-chave-secreta-muito-forte')
    if not user_email:
        redirect('/GAMEVERSE') # Ou para uma página de login específica
    return ctl.add_game()

@app.route('/games/edit/<game_id:int>', method=['GET', 'POST'])
def edit_game(game_id):
    user_email = request.get_cookie("user_email", secret='uma-chave-secreta-muito-forte')
    if not user_email:
        redirect('/GAMEVERSE')
    return ctl.edit_game(game_id)

@app.route('/games/delete/<game_id:int>', method=['GET'])
def delete_game(game_id):
    user_email = request.get_cookie("user_email", secret='uma-chave-secreta-muito-forte')
    if not user_email:
        redirect('/GAMEVERSE')
    return ctl.delete_game(game_id)


#-----------------------------------------------------------------------------


if __name__ == '__main__':

    run(app, host='localhost', port=8080)
