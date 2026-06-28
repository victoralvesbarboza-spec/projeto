from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'deaf_agendei_chave_secreta_2024'
app.config['SECRET_KEY'] = 'deaf_agendei_chave_secreta_2024'

os.makedirs('dados', exist_ok=True)

def carregar_dados(arquivo):
    caminho = f'dados/{arquivo}.json'
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_dados(arquivo, dados):
    with open(f'dados/{arquivo}.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def inicializar_dados():
    usuarios = carregar_dados('usuarios')
    if not usuarios:
        senha_hash = hashlib.sha256('123456'.encode()).hexdigest()
        salvar_dados('usuarios', [
            {'id': 1, 'nome': 'Victor', 'email': 'victor@deaf.com', 'senha': senha_hash}
        ])
    
    quadras = carregar_dados('quadras')
    if not quadras:
        salvar_dados('quadras', [
            {
                'id': 1,
                'nome': 'Arena Futebol',
                'localizacao': 'Av. Paulista, 1000',
                'esporte': 'Futebol',
                'preco': 120,
                'horarios': [
                    '08:00', '08:30', '09:00', '09:30',
                    '10:00', '10:30', '11:00', '11:30',
                    '12:00', '12:30', '13:00', '13:30',
                    '14:00', '14:30', '15:00', '15:30',
                    '16:00', '16:30', '17:00', '17:30',
                    '18:00', '18:30', '19:00', '19:30',
                    '20:00', '20:30', '21:00', '21:30',
                    '22:00'
                ]
            },
            {
                'id': 2,
                'nome': 'Quadra de Vôlei',
                'localizacao': 'R. Augusta, 500',
                'esporte': 'Vôlei',
                'preco': 80,
                'horarios': [
                    '08:00', '08:30', '09:00', '09:30',
                    '10:00', '10:30', '11:00', '11:30',
                    '12:00', '12:30', '13:00', '13:30',
                    '14:00', '14:30', '15:00', '15:30',
                    '16:00', '16:30', '17:00', '17:30',
                    '18:00', '18:30', '19:00', '19:30',
                    '20:00', '20:30', '21:00'
                ]
            },
            {
                'id': 3,
                'nome': 'Quadra de Basquete',
                'localizacao': 'Av. Brasil, 2000',
                'esporte': 'Basquete',
                'preco': 100,
                'horarios': [
                    '08:00', '08:30', '09:00', '09:30',
                    '10:00', '10:30', '11:00', '11:30',
                    '12:00', '12:30', '13:00', '13:30',
                    '14:00', '14:30', '15:00', '15:30',
                    '16:00', '16:30', '17:00', '17:30',
                    '18:00', '18:30', '19:00', '19:30',
                    '20:00', '20:30', '21:00', '21:30',
                    '22:00'
                ]
            },
        ])
    
    if not carregar_dados('agendamentos'):
        salvar_dados('agendamentos', [])

inicializar_dados()

@app.route('/')
def index():
    if 'usuario_id' in session:
        if session.get('usuario_id') == 1 or session.get('usuario_email') == 'victor@deaf.com':
            return redirect(url_for('admin_agendamentos'))
        else:
            return redirect(url_for('quadras'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        usuarios = carregar_dados('usuarios')
        
        for u in usuarios:
            if u['email'] == email and u.get('senha') == senha_hash:
                session['usuario_id'] = u['id']
                session['usuario_nome'] = u['nome']
                session['usuario_email'] = u['email']
                
                # ADMIN vai para o painel admin
                if u['id'] == 1 or u['email'] == 'victor@deaf.com':
                    return redirect(url_for('admin_agendamentos'))
                else:
                    return redirect(url_for('quadras'))
        
        return render_template('login.html', erro='Email ou senha inválidos')
    
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuarios = carregar_dados('usuarios')
        
        for u in usuarios:
            if u['email'] == email:
                return render_template('cadastro.html', erro='Email já cadastrado')
        
        novo_id = len(usuarios) + 1
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        usuarios.append({
            'id': novo_id,
            'nome': nome,
            'email': email,
            'senha': senha_hash,
            'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M')
        })
        salvar_dados('usuarios', usuarios)
        
        session['usuario_id'] = novo_id
        session['usuario_nome'] = nome
        session['usuario_email'] = email
        
        return redirect(url_for('quadras'))
    
    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/quadras')
def quadras():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    # Se for admin, redireciona para o painel admin
    if session['usuario_id'] == 1 or session.get('usuario_email') == 'victor@deaf.com':
        return redirect(url_for('admin_agendamentos'))
    
    quadras = carregar_dados('quadras')
    return render_template('quadras.html', quadras=quadras)

@app.route('/agendar/<int:quadra_id>', methods=['GET', 'POST'])
def agendar(quadra_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    # Admin não pode agendar, só ver
    if session['usuario_id'] == 1 or session.get('usuario_email') == 'victor@deaf.com':
        flash('❌ Administrador não pode agendar!', 'error')
        return redirect(url_for('admin_agendamentos'))
    
    quadras = carregar_dados('quadras')
    quadra = None
    for q in quadras:
        if q['id'] == quadra_id:
            quadra = q
            break
    
    if not quadra:
        return redirect(url_for('quadras'))
    
    agendamentos = carregar_dados('agendamentos')
    
    if request.method == 'POST':
        data = request.form.get('data')
        horario = request.form.get('horario')
        
        for a in agendamentos:
            if a['quadra_id'] == quadra_id and a['data'] == data and a['horario'] == horario:
                return render_template('agendar.html', quadra=quadra, 
                                     erro=f'❌ Horário {horario} do dia {data} já está ocupado!',
                                     hoje=datetime.now().strftime('%Y-%m-%d'),
                                     ocupados=[a['horario'] for a in agendamentos if a['quadra_id'] == quadra_id and a['data'] == data])
        
        if not data or not horario:
            return render_template('agendar.html', quadra=quadra, erro='Selecione data e horário!', 
                                 hoje=datetime.now().strftime('%Y-%m-%d'),
                                 ocupados=[a['horario'] for a in agendamentos if a['quadra_id'] == quadra_id and a['data'] == data])
        
        novo_id = len(agendamentos) + 1
        
        novo_agendamento = {
            'id': novo_id,
            'usuario_id': session['usuario_id'],
            'usuario_nome': session['usuario_nome'],
            'quadra_id': quadra_id,
            'quadra_nome': quadra['nome'],
            'data': data,
            'horario': horario,
            'valor_total': quadra['preco'],
            'status': 'confirmado',
            'data_agendamento': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'codigo': f"DEAF{datetime.now().strftime('%Y%m%d%H%M%S')}{novo_id}"
        }
        
        agendamentos.append(novo_agendamento)
        salvar_dados('agendamentos', agendamentos)
        
        print(f"✅ Agendamento: {quadra['nome']} - {data} {horario}")
        return redirect(url_for('meus_agendamentos'))
    
    data_selecionada = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))
    ocupados = [a['horario'] for a in agendamentos if a['quadra_id'] == quadra_id and a['data'] == data_selecionada]
    
    hoje = datetime.now().strftime('%Y-%m-%d')
    return render_template('agendar.html', quadra=quadra, hoje=hoje, ocupados=ocupados, data_selecionada=data_selecionada)

@app.route('/meus_agendamentos')
def meus_agendamentos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    agendamentos = carregar_dados('agendamentos')
    meus = [a for a in agendamentos if a['usuario_id'] == session['usuario_id']]
    meus.reverse()
    return render_template('meus_agendamentos.html', agendamentos=meus)

@app.route('/cancelar_agendamento/<int:id>')
def cancelar_agendamento(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    agendamentos = carregar_dados('agendamentos')
    agendamentos = [a for a in agendamentos if a['id'] != id]
    salvar_dados('agendamentos', agendamentos)
    return redirect(url_for('meus_agendamentos'))

@app.route('/perfil')
def perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    usuarios = carregar_dados('usuarios')
    usuario = None
    for u in usuarios:
        if u['id'] == session['usuario_id']:
            usuario = u
            break
    
    return render_template('perfil.html', usuario=usuario)

# ============= ROTAS ADMIN =============

@app.route('/admin/agendamentos')
def admin_agendamentos():
    if 'usuario_id' not in session:
        flash('❌ Faça login para continuar!', 'error')
        return redirect(url_for('login'))
    
    if session['usuario_id'] != 1 and session.get('usuario_email') != 'victor@deaf.com':
        flash('❌ Acesso negado!', 'error')
        return redirect(url_for('quadras'))
    
    agendamentos = carregar_dados('agendamentos')
    agendamentos.reverse()
    
    usuarios = carregar_dados('usuarios')
    quadras = carregar_dados('quadras')
    
    total_agendamentos = len(agendamentos)
    total_usuarios = len(usuarios)
    total_quadras = len(quadras)
    
    return render_template('admin_agendamentos.html', 
                         agendamentos=agendamentos,
                         total_agendamentos=total_agendamentos,
                         total_usuarios=total_usuarios,
                         total_quadras=total_quadras)

@app.route('/admin/deletar_agendamento/<int:id>', methods=['POST'])
def admin_deletar_agendamento(id):
    if 'usuario_id' not in session:
        flash('❌ Faça login para continuar!', 'error')
        return redirect(url_for('login'))
    
    if session['usuario_id'] != 1 and session.get('usuario_email') != 'victor@deaf.com':
        flash('❌ Acesso negado!', 'error')
        return redirect(url_for('admin_agendamentos'))
    
    agendamentos = carregar_dados('agendamentos')
    agendamento_encontrado = None
    
    for a in agendamentos:
        if a['id'] == id:
            agendamento_encontrado = a
            break
    
    if not agendamento_encontrado:
        flash('❌ Agendamento não encontrado!', 'error')
        return redirect(url_for('admin_agendamentos'))
    
    agendamentos = [a for a in agendamentos if a['id'] != id]
    salvar_dados('agendamentos', agendamentos)
    
    flash(f'✅ Agendamento de {agendamento_encontrado["quadra_nome"]} - {agendamento_encontrado["data"]} {agendamento_encontrado["horario"]} cancelado!', 'success')
    
    return redirect(url_for('admin_agendamentos'))

@app.route('/admin/usuarios')
def admin_usuarios():
    if 'usuario_id' not in session:
        flash('❌ Faça login para continuar!', 'error')
        return redirect(url_for('login'))
    
    if session['usuario_id'] != 1 and session.get('usuario_email') != 'victor@deaf.com':
        flash('❌ Acesso negado!', 'error')
        return redirect(url_for('quadras'))
    
    usuarios = carregar_dados('usuarios')
    agendamentos = carregar_dados('agendamentos')
    
    for u in usuarios:
        u['agendamentos_count'] = len([a for a in agendamentos if a.get('usuario_id') == u['id']])
    
    total_usuarios = len(usuarios)
    total_agendamentos = len(agendamentos)
    
    return render_template('admin_usuarios.html', 
                         usuarios=usuarios,
                         total_usuarios=total_usuarios,
                         total_agendamentos=total_agendamentos)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🏆 DEAF AGENDEI+")
    print("="*50)
    print("🚀 http://127.0.0.1:5000")
    print("🔑 victor@deaf.com / 123456 (ADMIN)")
    print("👑 Admin: http://127.0.0.1:5000/admin/agendamentos")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)