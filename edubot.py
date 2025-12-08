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
    if not GROQ_API_KEY:
        return "❌ API Key da IA não configurada."

    url = "https://api.groq.com/openai/v1/responses"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = """Você é um assistente educacional para estudantes de engenharia.
Responda sempre em português brasileiro, de forma clara e objetiva."""

    if contexto:
        system_prompt += f"\nContexto: {contexto}"

    data = {
        "model": "llama3-70b-8192",
        "input": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": pergunta
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Extrair texto da resposta
        resposta = result["output_text"]
        return resposta

    except Exception as e:
        return f"❌ Erro ao conectar com a IA: {str(e)}"


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
        "/provas_4_periodo - Provas do 4º período"
    )

async def provas_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 Provas - 1º Período\n\n"
        "🔹 Cálculo 1: https://drive.google.com/drive/folders/1ybUELl95JAvKEA2BUY3zrh6j92nPLDaN\n\n"
        "🔹 Geometria Analítica: https://drive.google.com/drive/folders/1AUD9Txk_q6hKLkiNKhp2AMU6hYhNW-0e\n\n"
        "🔹 Química: https://drive.google.com/drive/folders/1kBdvQ0cpD_QovwR_Fgj4xn1625zdZA-i\n\n"
        "Bons estudos! 📖"
    )
    await update.message.reply_text(texto)


async def provas_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 Provas - 2º Período\n\n"
        "🔹 Cálculo 2: https://drive.google.com/drive/folders/1huKyHXByNya6UOfpbm90mhWGSow70BWk\n\n"
        "🔹 Álgebra Linear: https://drive.google.com/drive/folders/17PmMaQKq-VY6PcXOQ-QiK150ig8Wg6B9\n\n"
        "🔹 Física 1: https://drive.google.com/drive/folders/1FteXNEk-TaIXQZAgkm7ni86wGTt6HlPB\n\n"
        "🔹 Expressão Gráfica: https://drive.google.com/drive/folders/1BVF_6htdX4V2IWSb4MJZZUtkTLPyc-hN\n\n"
        "🔹 Probabilidade e Estatística: https://drive.google.com/drive/folders/15psYZEs9GQWudgW8DhV0w_9ZuidUtNuU\n\n"
        "Bons estudos! 📖"
    )
    await update.message.reply_text(texto)


async def provas_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 Provas - 3º Período\n\n"
        "🔹 Cálculo 3: https://drive.google.com/drive/folders/10auVZ5mM2HBTIIOdC-OT6QjQdlhV3WHf\n\n"
        "🔹 Cálculo Numérico: https://drive.google.com/drive/folders/1STexzcxwXeMk9X-P0HhtYynT7FCpqfTM\n\n"
        "🔹 Desenho Universal: https://drive.google.com/drive/folders/1AUD9Txk_q6hKLkiNKhp2AMU6hYhNW-0e\n\n"
        "🔹 Física 2: https://drive.google.com/drive/folders/1TgCcB1FzNPh5akjVIc5dQL9S0VVlM672\n\n"
        "Bons estudos! 📖"
    )
    await update.message.reply_text(texto)


async def provas_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 Provas - 4º Período\n\n"
        "🔹 Cálculo 4: https://drive.google.com/drive/folders/1olPwxwZw5X1CBC9sJr-5a7gwlTnM0kgE\n\n"
        "🔹 Física 3: https://drive.google.com/drive/folders/1OTWU5UpiAChZ3c25W4mcFITf1qZ8iYfz\n\n"
        "🔹 Laboratório de Física Básica: https://drive.google.com/drive/folders/1AUD9Txk_q6hKLkiNKhp2AMU6hYhNW-0e\n\n"
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
