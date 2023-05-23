import os
import secrets
from comunidadeflask import app, bcrypt, database
from comunidadeflask.forms import FormCriarConta, FormLogin, FormEditarPerfil
from comunidadeflask.models import Usuario
from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user, login_user, logout_user, login_required
from PIL import Image

lista_usuarios = ['Gesiel', 'Ariadne', 'Luna']


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/contato")
def contato():
    return render_template('contato.html')


@app.route("/usuarios")
@login_required
def usuarios():
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criar_conta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login feito com sucesso no e-mail: {form_login.email.data}', 'alert-success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash("Falha no login. E-mail ou senha incorretos", 'alert-danger')

    if form_criar_conta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        usuario = Usuario(username=form_criar_conta.username.data,
                          email=form_criar_conta.email.data,
                          senha=bcrypt.generate_password_hash(form_criar_conta.senha.data))
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada com sucesso para o e-mail: {form_criar_conta.email.data}', 'alert-success')
        return redirect(url_for('home'))

    return render_template('login.html', form_login=form_login, form_criar_conta=form_criar_conta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash(f'Logout Feito com Sucesso', 'alert-success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)


def salvar_foto_perfil(imagem):
    # Gerando código único para foto
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao

    # Caminho onde a imagem vai ser salva
    caminho_completo = os.path.join(
        app.root_path, 'static/fotos_perfil', nome_arquivo
    )

    # Diminuir foto para salvar
    tamanho_foto = (400, 400)
    foto_reduzida = Image.open(imagem)
    foto_reduzida.thumbnail(tamanho_foto)

    # Salvar foto
    foto_reduzida.save(caminho_completo)
    return nome_arquivo


def atualizar_conhecimentos(form):
    lista_conhecimentos = []
    for campo in form:
        if 'conhecimento_' in campo.name:
            if campo.data:
                lista_conhecimentos.append(campo.label.text)
    return ';'.join(lista_conhecimentos)


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editarperfil():
    form_editar_perfil = FormEditarPerfil()
    if form_editar_perfil.validate_on_submit():
        current_user.email = form_editar_perfil.email.data
        current_user.username = form_editar_perfil.username.data
        if form_editar_perfil.foto_perfil.data:
            nome_foto = salvar_foto_perfil(form_editar_perfil.foto_perfil.data)
            current_user.foto_perfil = nome_foto
        current_user.cursos = atualizar_conhecimentos(form_editar_perfil)
        database.session.commit()
        flash('Perfil atualizado com Sucesso', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == "GET":
        form_editar_perfil.email.data = current_user.email
        form_editar_perfil.username.data = current_user.username
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form_editar_perfil=form_editar_perfil)


@app.route('/post/criar')
@login_required
def criar_post():
    return render_template('criarpost.html')
