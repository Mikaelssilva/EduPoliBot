from os import getenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

token = getenv("BOT_TOKEN")

# Comandos
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Olá. Eu sou o Edu Poli Bot 🤖')


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Como posso te ajudar?\n\n'
        'Comandos disponíveis:\n'
        '/start - Iniciar o bot\n'
        '/help - Ver esta mensagem\n'
        '/custom - Comando personalizado'
    )


async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Custom command executado! ✅')


async def provas_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 *Provas - 1º Período*\n\n"
        "🔹 Cálculo 1: https://drive.google.com/drive/folders/1ybUELl95JAvKEA2BUY3zrh6j92nPLDaN\n\n"
        "🔹 Sociologia: https://seulink.com/sociologia\n\n"
        "🔹 Geometria Analítica: https://drive.google.com/drive/folders/1AUD9Txk_q6hKLkiNKhp2AMU6hYhNW-0e\n\n"
        "🔹 Química: https://drive.google.com/drive/folders/1kBdvQ0cpD_QovwR_Fgj4xn1625zdZA-i"
    )
    await update.message.reply_text(texto)


async def provas_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 *Provas - 2º Período*\n\n"
        "🔹 Cálculo 2: https://drive.google.com/drive/folders/1huKyHXByNya6UOfpbm90mhWGSow70BWk\n\n"
        "🔹 Algebra Linear: https://drive.google.com/drive/folders/17PmMaQKq-VY6PcXOQ-QiK150ig8Wg6B9\n\n"
        "🔹 Física 1: https://drive.google.com/drive/folders/1FteXNEk-TaIXQZAgkm7ni86wGTt6HlPB\n\n"
        "🔹 Expressão Gráfica: https://drive.google.com/drive/folders/1BVF_6htdX4V2IWSb4MJZZUtkTLPyc-hN\n\n"
        "🔹 Probabilidade e Estatística: https://drive.google.com/drive/folders/15psYZEs9GQWudgW8DhV0w_9ZuidUtNuU"
    )
    await update.message.reply_text(texto)


async def provas_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 *Provas - 3º Período*\n\n"
        "🔹 Cálculo 3: https://drive.google.com/drive/folders/10auVZ5mM2HBTIIOdC-OT6QjQdlhV3WHf\n\n"
        "🔹 Cálculo Númerico: https://drive.google.com/drive/folders/1STexzcxwXeMk9X-P0HhtYynT7FCpqfTM\n\n"
        "🔹 Desenho Universal: https://drive.google.com/drive/folders/1AUD9Txk_q6hKLkiNKhp2AMU6hYhNW-0e\n\n"
        "🔹 Física 2: https://drive.google.com/drive/folders/1TgCcB1FzNPh5akjVIc5dQL9S0VVlM672\n\n"

    )
    await update.message.reply_text(texto)


async def provas_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "📚 *Provas - 4º Período*\n\n"
        "🔹 Cálculo 4: https://drive.google.com/drive/folders/1olPwxwZw5X1CBC9sJr-5a7gwlTnM0kgE\n\n"
        "🔹 Física 3: https://drive.google.com/drive/folders/1OTWU5UpiAChZ3c25W4mcFITf1qZ8iYfz\n\n"
        "🔹 Laboratório de Física Básica: https://drive.google.com/drive/folders/1AUD9Txk_q6hKLkiNKhp2AMU6hYhNW-0e"
    )
    await update.message.reply_text(texto)


# Gerenciar mensagens
def handle_message(text: str) -> str:
    # Processar o texto recebido
    processed_text = text.lower()

    if 'olá' in processed_text or 'oi' in processed_text:
        return 'Olá! Como posso ajudar?'

    if 'tudo bem' in processed_text:
        return 'Tudo ótimo! E você?'

    if 'obrigado' in processed_text:
        return 'Por nada! 😊'

    # Resposta padrão
    return f'Você disse: {text}'


async def handle_message_async(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Pegar informações da mensagem
    message_type = update.message.chat.type
    text = update.message.text

    print(f'Usuário ({update.message.chat.id}) em {message_type}: "{text}"')

    # Se for em grupo, só responde se mencionar o bot
    if message_type == 'group':
        if bot_username in text:
            new_text = text.replace(bot_username, '').strip()
            response = handle_message(new_text)
        else:
            return  # Ignora mensagens que não mencionam o bot
    else:
        response = handle_message(text)

    # Enviar resposta
    print(f'Bot: {response}')
    await update.message.reply_text(response)


# Tratamento de erros
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Erro causado por update {update}: {context.error}')


# Main - Iniciar o bot
if __name__ == '__main__':
    print('Iniciando bot...')

    # Criar aplicação
    app = Application.builder().token(token).build()

    # Registrar comandos
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('custom', custom))
    app.add_handler(CommandHandler('provas_1_periodo', provas_1))
    app.add_handler(CommandHandler('provas_2_periodo', provas_2))
    app.add_handler(CommandHandler('provas_3_periodo', provas_3))
    app.add_handler(CommandHandler('provas_4_periodo', provas_4))

    # Registrar handler de mensagens
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_async))

    # Registrar handler de erros
    app.add_error_handler(error)

    # Iniciar polling
    print('Bot rodando...')
    app.run_polling(poll_interval=3)

# ===== SERVER PARA RENDER NÃO MATAR O SERVIÇO =====
from flask import Flask
import threading
import os

app_server = Flask("server")

@app_server.route("/")
def home():
    return "EduBot está vivo!"

def start_server():
    port = int(os.environ.get("PORT", 10000))
    app_server.run(host="0.0.0.0", port=port)

threading.Thread(target=start_server).start()
