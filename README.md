# MERCON Contabilidade — Portal do Cliente

Protótipo de portal de atendimento construído com Flask, SQLite, HTML e CSS separado.

## Funcionalidades

- Formulário para registrar nome, e-mail e solicitação.
- Persistência dos registros em banco SQLite.
- Login para acesso ao painel administrativo.
- Listagem das solicitações e atualização de status.
- Layout responsivo com CSS em `static/css/style.css`.
- Token CSRF simples para proteger os formulários.

## Estrutura

```text
mercon_portal_contabil/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── instance/
│   └── (o banco portal.db é criado automaticamente)
├── static/
│   └── css/
│       └── style.css
└── templates/
    ├── index.html
    ├── login.html
    ├── admin.html
    └── erro.html
```

## Como executar no Windows

1. Instale Python 3.10 ou superior.
2. Abra o terminal dentro desta pasta.
3. Crie um ambiente virtual:

   ```bash
   python -m venv .venv
   ```

4. Ative o ambiente:

   ```bash
   .venv\Scripts\activate
   ```

5. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

6. Configure as variáveis de ambiente antes de iniciar. No PowerShell, por exemplo:

   ```powershell
   $env:MERCON_SECRET_KEY="substitua-por-uma-chave-aleatoria-grande"
   $env:MERCON_ADMIN_USER="admin"
   $env:MERCON_ADMIN_PASSWORD="defina-uma-senha-forte"
   ```

7. Inicie a aplicação:

   ```bash
   python app.py
   ```

8. Abra `http://127.0.0.1:5000/` no navegador.
9. O painel fica em `http://127.0.0.1:5000/admin/login`.

O banco SQLite será criado automaticamente em `instance/portal.db`. Os registros permanecem salvos após reiniciar o servidor.

## Observações de segurança

Este repositório é um protótipo para estudo e portfólio, não um sistema pronto para receber documentos ou dados contábeis reais. Não envie CPF, documentos pessoais, dados bancários, folha de pagamento ou informações sigilosas.

Antes de uso real, implemente e revise, no mínimo: HTTPS, gestão segura de segredos, armazenamento de senhas com hash, limitação de tentativas de login, política de sessão, logs e auditoria, backups, controle de acesso por usuário, validação de e-mail, política de privacidade e procedimentos LGPD. O servidor de desenvolvimento do Flask (`debug=True`) não deve ser usado em produção.

O painel usa credenciais definidas por variáveis de ambiente. Nunca coloque senhas reais no código ou no GitHub.
