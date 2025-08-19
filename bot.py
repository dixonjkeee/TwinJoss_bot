import logging
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замените на токен от @BotFather
WEBAPP_URL = "YOUR_WEBAPP_URL_HERE"  # Замените на URL вашего Web App
ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID"  # ID для получения заказов (опционально)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Создаем кнопку для открытия Web App
    keyboard = [
        [InlineKeyboardButton("🛍 Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
👋 Добро пожаловать в магазин украшений ручной работы, {user.first_name}!

✨ У нас вы найдете:
• Уникальные серьги
• Изящные браслеты
• Стильные кольца
• Красивые ожерелья

Все изделия созданы с любовью вручную из качественных материалов.

Нажмите кнопку ниже, чтобы открыть каталог:
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик данных от Web App"""
    try:
        # Получаем данные от Web App
        web_app_data = update.message.web_app_data.data
        order_data = json.loads(web_app_data)
        
        user = update.effective_user
        
        # Формируем сообщение о заказе
        order_message = f"""
🛍 **НОВЫЙ ЗАКАЗ**

👤 **Покупатель:**
• Имя: {user.first_name} {user.last_name or ''}
• Username: @{user.username or 'не указан'}
• ID: {user.id}

📦 **Товар:**
• Название: {order_data.get('name', 'Не указано')}
• Цена: {order_data.get('price', 0)} ₽
• Описание: {order_data.get('description', 'Не указано')}

📞 **Контакт:** @{user.username or user.first_name}
        """
        
        # Отправляем подтверждение покупателю
        await update.message.reply_text(
            f"✅ **Заказ принят!**\n\n"
            f"📦 Товар: {order_data.get('name')}\n"
            f"💰 Цена: {order_data.get('price')} ₽\n\n"
            f"🕐 Мы свяжемся с вами в ближайшее время для уточнения деталей доставки и оплаты.\n\n"
            f"Спасибо за ваш заказ! 💎",
            parse_mode='Markdown'
        )
        
        # Отправляем заказ администратору (если настроен ADMIN_CHAT_ID)
        if ADMIN_CHAT_ID and ADMIN_CHAT_ID != "YOUR_ADMIN_CHAT_ID":
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=order_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Ошибка отправки заказа админу: {e}")
        
        logger.info(f"Новый заказ от {user.username}: {order_data}")
        
    except json.JSONDecodeError:
        await update.message.reply_text(
            "❌ Ошибка обработки заказа. Попробуйте еще раз."
        )
    except Exception as e:
        logger.error(f"Ошибка обработки веб-приложения: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка. Попробуйте позже или обратитесь к администратору."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = """
🆘 **Помощь**

Доступные команды:
• /start — Запуск бота и открытие магазина
• /help — Показать это сообщение

❓ **Как сделать заказ:**
1. Нажмите "🛍 Открыть магазин"
2. Выберите понравившееся украшение
3. Нажмите "🛒 Заказать"
4. Дождитесь подтверждения

📞 **Связь с нами:**
По всем вопросам пишите в этот чат.
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")

def main() -> None:
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()