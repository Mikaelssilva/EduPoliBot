from os import getenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading
import requests
import json

token = getenv("BOT_TOKEN")
GROQ_API_KEY = getenv("GROQ_API_KEY")

bot_username = "@EduPoliBot"

# ===== SERVIDOR WEB PARA RENDER =====
app_server = Flask(__name__)


@app_server.route("/")
def home():
    return "✅ EduBot está online!"


@app_server.route("/health")
def health():
    return "OK", 200


def start_server():
    port = int(getenv("PORT", 10000))
    app_server.run(host="0.0.0.0", port=port)


# ===== FUNÇÃO DE IA =====
def perguntar_ia(pergunta, contexto=""):
    """Faz pergunta para a IA"""

    if not GROQ_API_KEY:
        return "❌ API Key da IA não configurada."

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Prompt do sistema - define o comportamento da IA
    system_prompt = """Você é um assistente educacional para estudantes de engenharia. 
Seja objetivo, claro e educado. Ajude com dúvidas sobre:
- Cálculo, Física, Álgebra
- Explicações de conceitos
- Resolução de exercícios
- Dicas de estudo

Sempre responda em português brasileiro."""

    if contexto:
        system_prompt += f"\n\nContexto adicional: {contexto}"

    data = {
        "model": "llama-3.3-70b-versatile", # Modelo correto
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": pergunta}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)

        # Debug - ver o que a API retornou
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")

        response.raise_for_status()

        resultado = response.json()
        resposta = resultado['choices'][0]['message']['content']
        return resposta

    except requests.exceptions.HTTPError as e:
        error_msg = f"Erro HTTP {response.status_code}"
        try:
            error_detail = response.json()
            error_msg += f": {error_detail.get('error', {}).get('message', 'Erro desconhecido')}"
        except:
            error_msg += f": {response.text[:200]}"
        return f"❌ {error_msg}"
    except requests.exceptions.Timeout:
        return "⏱️ A IA demorou muito para responder. Tente novamente."
    except requests.exceptions.RequestException as e:
        return f"❌ Erro ao conectar: {str(e)}"
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"

# ===== COMANDOS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🤖 Bem vindo ao Edu Poli Bot!\n\n'
        '/ia - Perguntar para a IA\n'
        '/resolver - Resolver exercício\n'
        '/explicar - Explicar conceito\n\n'
        '/provas_1_periodo  - Ver provas\n'
        '/provas_2_periodo  - Ver provas\n'
        '/provas_3_periodo  - Ver provas\n'
        '/provas_4_periodo  - Ver provas\n\n'
        "/livros - Coleção de livros\n\n"
        'Ou apenas envie sua dúvida diretamente!'
    )


async def comando_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ia pergunta"""
    if not context.args:
        await update.message.reply_text(
            '❓ Use assim: `/ia sua pergunta aqui`\n\n'
            'Exemplo: `/ia o que é derivada?`',
            parse_mode='Markdown'
        )
        return

    pergunta = ' '.join(context.args)

    # Mostrar que está processando
    msg = await update.message.reply_text('🤔 Pensando...')

    # Perguntar para IA
    resposta = perguntar_ia(pergunta)

    # Enviar resposta
    await msg.edit_text(f'🤖 *Resposta da IA:*\n\n{resposta}', parse_mode='Markdown')


async def resolver_exercicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /resolver exercício"""
    if not context.args:
        await update.message.reply_text(
            '📝 Use: `/resolver seu exercício`\n\n'
            'Exemplo: `/resolver calcule a derivada de x²`',
            parse_mode='Markdown'
        )
        return

    exercicio = ' '.join(context.args)
    msg = await update.message.reply_text('📊 Resolvendo...')

    contexto = "Resolva o exercício passo a passo, explicando cada etapa."
    resposta = perguntar_ia(exercicio, contexto)

    await msg.edit_text(f'✏️ *Solução:*\n\n{resposta}', parse_mode='Markdown')


async def explicar_conceito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /explicar conceito"""
    if not context.args:
        await update.message.reply_text(
            '💡 Use: `/explicar conceito`\n\n'
            'Exemplo: `/explicar integrais`',
            parse_mode='Markdown'
        )
        return

    conceito = ' '.join(context.args)
    msg = await update.message.reply_text('📚 Explicando...')

    contexto = "Explique de forma simples e didática, com exemplos práticos."
    resposta = perguntar_ia(f"Explique: {conceito}", contexto)

    await msg.edit_text(f'📖 *Explicação:*\n\n{resposta}', parse_mode='Markdown')


# Responder mensagens diretas (opcional)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde mensagens normais com IA"""
    text = update.message.text
    user_id = update.message.chat.id

    # Ignorar em grupos (só responde em privado)
    if update.message.chat.type != 'private':
        return

    msg = await update.message.reply_text('🤔 Analisando sua dúvida...')
    resposta = perguntar_ia(text)
    await msg.edit_text(f'🤖 {resposta}')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Comandos disponíveis:\n\n"
        "/start - Iniciar o bot\n"
        "/ia - Perguntar algo para a IA\n"
        "/resolver - Resolver exercício\n"
        "/explicar - Explicar conceito\n"
        "/provas_1_periodo - Provas do 1º período\n"
        "/provas_2_periodo - Provas do 2º período\n"
        "/provas_3_periodo - Provas do 3º período\n"
        "/provas_4_periodo - Provas do 4º período\n"
        "/livros - Coleção de livros"
    )


async def books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 Livros - Coleção de livros\n\n"
        "1° Período: https://drive.google.com/drive/folders/17alVRsBedli2YWLvZMv27JZP2U3IH3A9?hl=pt-br\n\n"
        "2° Período: https://drive.google.com/drive/folders/10vsd7N5exiLe5umwYomsqSe9KtMVpmJh?hl=pt-br\n\n"
        "3° Período: https://drive.google.com/drive/folders/1m0Y4xUtcMv4aiSFwuNz4InSgu7z9h8ZF?hl=pt-br\n\n"
        "4° Período: https://drive.google.com/drive/folders/18xiU2Ec6g_1uCD8L0gPNov6K1bcGBYJw?hl=pt-br\n\n"
        "Bons estudos! 📖"
    )
    await update.message.reply_text(text)

async def provas_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 Provas - 1º Período\n\n"
        "Cálculo I: https://drive.google.com/drive/folders/1XeT4_rdT4Iu7DvdhERVaMlzHxvru0hAH?hl=pt-br\n\n"
        "Geometria Analítica: https://drive.google.com/drive/folders/1VEBq3lkDF5sA5SZcZLX7jAOhAnv77CHh?hl=pt-br\n\n"
        "Química: https://drive.google.com/drive/folders/17jprpf8AK0ZPEF-Ub2UVVot4Vca2I0CS?hl=pt-br\n\n"
        "Bons estudos! 📖"
    )
    await update.message.reply_text(texto)

async def provas_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 Provas - 2º Período\n\n"
        "Cálculo II: https://drive.google.com/drive/folders/1Q3820oSZ7ToB7fULESpfArbSUa9cCFmR?hl=pt-br\n\n"
        "Álgebra Linear: https://drive.google.com/drive/folders/1oBMiN7TNL9jG4K4P1lOSN2TjwSy2XkVK?hl=pt-br\n\n"
        "Física I: https://drive.google.com/drive/folders/1FteXNEk-TaIXQZAgkm7ni86wGTt6HlPB\n\n"
        "Expressão Gráfica I: https://drive.google.com/drive/folders/1TagQeNmjuwaQTbrvp66L92OSqw2UOvHN?hl=pt-br\n\n"
        "Probabilidade e Estatística: https://drive.google.com/drive/folders/15psYZEs9GQWudgW8DhV0w_9ZuidUtNuU?hl=pt-br\n\n"
        "Bons estudos! 📖"
    )
    await update.message.reply_text(texto)


async def provas_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 Provas - 3º Período\n\n"
        "Cálculo III: https://drive.google.com/drive/folders/16uCxyi9JLtn02mdjjvKRxozUV-zOshUA?hl=pt-br\n\n"
        "Cálculo Numérico: https://drive.google.com/drive/folders/1u_PE8NdAItIfgKkUJrYe6iUS4Apyike6?hl=pt-br\n\n"
        "Desenho Universal: https://drive.google.com/drive/folders/1U6WvWj-KyW8AK9fCc-sUvypnPNqB0goo?hl=pt-br\n\n"
        "Física II: https://drive.google.com/drive/folders/1AlEeaITMTuiWgsy8Mn3S5BCT14y9WCz4?hl=pt-br\n\n"
        "Bons estudos! 📖"
    )
    await update.message.reply_text(texto)


async def provas_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 Provas - 4º Período\n\n"
        "Cálculo IV: https://drive.google.com/drive/folders/1EjEG7GUfMWySbXBWTd9Uak8QlOM-Goep?hl=pt-br\n\n"
        "Física III: https://drive.google.com/drive/folders/1-_a6seL2E5kxhbej32rL7y7pC6xaVlbn?hl=pt-br\n\n"
        "Laboratório de Física Básica: https://drive.google.com/drive/folders/14B8JXNLBenmkpI30ZUhPmssquEWZeOi2?hl=pt-br\n\n"
        "Bons estudos! 📖"
    )
    await update.message.reply_text(texto)


# Gerenciar mensagens
def handle_message(text: str) -> str:
    processed_text = text.lower()

    if 'olá' in processed_text or 'oi' in processed_text:
        return 'Olá! Use /help para ver os comandos disponíveis! 👋'

    if 'tudo bem' in processed_text:
        return 'Tudo ótimo! E você? 😊'

    if 'obrigado' in processed_text:
        return 'Por nada! Bons estudos! 📚'

    if 'prova' in processed_text:
        return 'Use os comandos /provas_1_periodo, /provas_2_periodo, etc. para ver as provas! 📝'

    return 'Use /help para ver os comandos disponíveis! 🤖'


async def handle_message_async(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    print(f'Usuário ({update.message.chat.id}) em {message_type}: "{text}"')

    if message_type == 'group':
        if bot_username in text:
            new_text = text.replace(bot_username, '').strip()
            response = handle_message(new_text)
        else:
            return
    else:
        response = handle_message(text)

    print(f'Bot: {response}')
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'❌ Erro: {context.error}')


# ===== INICIAR BOT =====
def start_bot():
    print('🤖 Iniciando bot...')

    if not token:
        print('❌ ERRO: BOT_TOKEN não encontrado!')
        return

    app = Application.builder().token(token).build()

    # Comandos
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ia', comando_ia))
    app.add_handler(CommandHandler('resolver', resolver_exercicio))
    app.add_handler(CommandHandler('explicar', explicar_conceito))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('provas_1_periodo', provas_1))
    app.add_handler(CommandHandler('provas_2_periodo', provas_2))
    app.add_handler(CommandHandler('provas_3_periodo', provas_3))
    app.add_handler(CommandHandler('provas_4_periodo', provas_4))
    app.add_handler(CommandHandler('livros', books))

    # Mensagens
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_async))

    # Erros
    app.add_error_handler(error)

    print('✅ Bot rodando!')
    app.run_polling(poll_interval=3)


# ===== MAIN =====
if __name__ == '__main__':
    # Iniciar servidor web em thread separada
    print('🌐 Iniciando servidor web...')
    threading.Thread(target=start_server, daemon=True).start()

    # Iniciar bot
    start_bot()
