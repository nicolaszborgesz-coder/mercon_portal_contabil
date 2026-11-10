import os
import re
import secrets
import sqlite3
from functools import wraps
from pathlib import Path

from flask import (
    Flask, abort, flash, redirect, render_template,
    request, session, url_for
)

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE = INSTANCE_DIR / "portal.db"

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ.get(
        "MERCON_SECRET_KEY",
        "troque-esta-chave-no-desenvolvimento"
    ),
    MAX_CONTENT_LENGTH=16 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("MERCON_HTTPS", "0") == "1",
)

# CREDENCIAIS DO ADMINISTRADOR
ADMIN_USER = "Nicolas"
ADMIN_PASSWORD = "12345678"

def conectar_banco():
    INSTANCE_DIR.mkdir(exist_ok=True)

    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row

    return conexao

def inicializar_banco():
    with conectar_banco() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS solicitacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                solicitacao TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Nova',
                criada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

# PROTEÇÃO CSRF
def token_csrf():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_urlsafe(32)

    return session["_csrf_token"]

app.jinja_env.globals["csrf_token"] = token_csrf

def validar_csrf():
    enviado = request.form.get("_csrf_token", "")
    salvo = session.get("_csrf_token", "")

    if not salvo or not secrets.compare_digest(enviado, salvo):
        abort(
            400,
            description="Token de segurança inválido. Atualize a página e tente novamente."
        )

# PROTEÇÃO DO PAINEL ADMINISTRATIVO
def exige_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logado"):
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper

# PÁGINA INICIAL
@app.route("/")
def inicio():
    return render_template("index.html")

# CADASTRO DE SOLICITAÇÕES
@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    validar_csrf()

    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    solicitacao = request.form.get("solicitacao", "").strip()

    if not nome or not email or not solicitacao:
        flash("Preencha todos os campos.", "erro")
        return redirect(url_for("inicio"))

    if len(nome) > 120 or len(email) > 150 or len(solicitacao) > 2000:
        flash("Um ou mais campos ultrapassaram o limite permitido.", "erro")
        return redirect(url_for("inicio"))

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        flash("Informe um endereço de e-mail válido.", "erro")
        return redirect(url_for("inicio"))

    with conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO solicitacoes (nome, email, solicitacao)
            VALUES (?, ?, ?)
            """,
            (nome, email, solicitacao)
        )

    flash(
        "Solicitação recebida. A equipe poderá entrar em contato pelo e-mail informado.",
        "sucesso"
    )

    return redirect(url_for("inicio"))

# LOGIN ADMINISTRATIVO
@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logado"):
        return redirect(url_for("admin"))

    if request.method == "POST":
        validar_csrf()

        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        if (
            secrets.compare_digest(usuario, ADMIN_USER)
            and secrets.compare_digest(senha, ADMIN_PASSWORD)
        ):
            session.clear()
            session["admin_logado"] = True

            flash("Acesso autorizado.", "sucesso")

            return redirect(url_for("admin"))

        flash("Usuário ou senha incorretos.", "erro")

    return render_template("login.html")

# PAINEL ADMINISTRATIVO
@app.route("/admin")
@exige_login
def admin():
    with conectar_banco() as conexao:
        clientes = conexao.execute(
            """
            SELECT id, nome, email, solicitacao, status, criada_em
            FROM solicitacoes
            ORDER BY id DESC
            """
        ).fetchall()

    return render_template("admin.html", clientes=clientes)

# ATUALIZAR STATUS
@app.route("/admin/status/<int:cliente_id>", methods=["POST"])
@exige_login
def atualizar_status(cliente_id):
    validar_csrf()

    status = request.form.get("status", "")

    permitidos = {"Nova", "Em análise", "Concluída"}

    if status not in permitidos:
        abort(400)

    with conectar_banco() as conexao:
        conexao.execute(
            "UPDATE solicitacoes SET status = ? WHERE id = ?",
            (status, cliente_id)
        )

    flash("Status atualizado.", "sucesso")

    return redirect(url_for("admin"))

# EXCLUIR SOLICITAÇÃO
@app.route("/admin/excluir/<int:cliente_id>", methods=["POST"])
@exige_login
def excluir(cliente_id):
    validar_csrf()

    with conectar_banco() as conexao:
        conexao.execute(
            "DELETE FROM solicitacoes WHERE id = ?",
            (cliente_id,)
        )

    flash("Solicitação excluída.", "sucesso")

    return redirect(url_for("admin"))

# SAIR DO PAINEL
@app.route("/admin/sair", methods=["POST"])
@exige_login
def sair():
    validar_csrf()

    session.clear()

    return redirect(url_for("login"))

# PÁGINA DE ERRO
@app.errorhandler(400)
def erro_requisicao(erro):
    return render_template(
        "erro.html",
        mensagem=getattr(
            erro,
            "description",
            "Solicitação inválida."
        )
    ), 400

# INICIALIZAR BANCO DE DADOS
inicializar_banco()

if __name__ == "__main__":
    # Apenas para desenvolvimento local.
    app.run(debug=True)