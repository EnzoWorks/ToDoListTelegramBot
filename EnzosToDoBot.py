from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import os
from dotenv import load_dotenv
from db import init_db, add_task, get_tasks, delete_task, clear_tasks, edit_task

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("tasks", list_tasks_command))
    app.add_handler(CommandHandler("add", add_task_command))
    app.add_handler(CommandHandler("delete", delete_task_command))
    app.add_handler(CommandHandler("edit", edit_task_command))
    app.add_handler(CommandHandler("clear", clear_tasks_command))
    app.add_handler(CallbackQueryHandler(handle_clear_confirmation))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Im your secretary. Type /help, to see my commands.")

async def list_tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = get_tasks(user_id)

    if not tasks:
        await update.message.reply_text("You dont have any tasks yet")
        return
    
    task_list = "\n".join(f"{i+1}. {task}" for i, task in enumerate(tasks))
    await update.message.reply_text(f"Your tasks:\n{task_list}")


async def add_task_command(update: Update,context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    task_text = ' '.join(context.args)

    if not task_text.strip():
        await update.message.reply_text("Task can't be blank")
        return

    add_task(user_id, task_text)
    await update.message.reply_text(f"Task succesfully added: {task_text}")

async def delete_task_command(update: Update,context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = get_tasks(user_id)
    
    if not context.args:
        await update.message.reply_text("Use /delete 'number of your task'")
        return
    
    try:
        index = int(context.args[0]) - 1
    except ValueError:
        await update.message.reply_text("Insert proper number of a task.")
        return
    
    if not tasks:
        await update.message.reply_text("You dont have any tasks yet")
        return
    
    if index < 0 or index >= len(tasks):
        await update.message.reply_text("You dont have any tasks under this number. ")
        return
    
    removed_task = tasks[index]
    delete_task(user_id, index)
    await update.message.reply_text(f"Deleted task: {removed_task}")

async def edit_task_command(update: Update,context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = get_tasks(user_id)

    if len(context.args) < 2:
        await update.message.reply_text("Use: /edit <task number> <new task>")
        return
    
    try:
        index = int(context.args[0]) - 1
    except ValueError:
        await update.message.reply_text("Insert proper number of task")
        return
    
    if not tasks:
        await update.message.reply_text("You dont have any tasks yet")
        return
    
    if index < 0 or index >= len(tasks):
        await update.message.reply_text("You dont have any tasks under this number. ")
        return
    
    new_text = ' '.join(context.args[1:])
    old_text = tasks[index]
    edit_task(user_id, index, new_text)

    await update.message.reply_text(f"Edited task number {index+1}: \nFrom: {old_text} \nTo: {new_text}")
    
async def clear_tasks_command(update: Update,context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = get_tasks(user_id)
    
    if not tasks:
        await update.message.reply_text("You dont have any tasks yet")
        return
    
    keyboard = [
        [
            InlineKeyboardButton("✅Yes", callback_data="confirm_clear"),
            InlineKeyboardButton("❌No", callback_data="cancel_clear")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Are you sure?", 
        reply_markup=reply_markup
    )

async def handle_clear_confirmation(update: Update,context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data

    if choice == "confirm_clear":
        clear_tasks(user_id)
        await query.edit_message_text("All tasks have been deleted.")
    elif choice == "cancel_clear":
        await query.edit_message_text("Task deletion canceled.")

async def help_command(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - start bot\n"
        "/tasks - your tasks\n"
        "/add <task> - add task\n"
        "/edit <number> <new task> - edit <number> task\n"
        "/delete <number> - delete <number> task\n"
        "/clear - clear all of your tasks\n"
    )

if __name__ == "__main__":
    init_db()
    main()