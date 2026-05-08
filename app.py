import logging
import random
import re
from datetime import datetime, time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== CONFIGURACIÓN - ¡PONÉ ACÁ TU TOKEN! ==========
TELEGRAM_TOKEN = "8381144172:AAGoFeNWrV98plvu38jwXnYExme52SPn0Eo"
# Ejemplo: "8381144172:AAGoFeNWrV98plvu38jwXNYExme52SpNoE0"
# =========================================================

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Horario
OPEN_TIME = time(9, 0)
CLOSE_TIME = time(17, 0)

def is_open():
    now = datetime.now().time()
    return OPEN_TIME <= now <= CLOSE_TIME

# Servicios
SERVICIOS = {
    'corte_dama': {'nombre': '💇‍♀️ Corte de dama', 'precio': 10000},
    'corte_caballero': {'nombre': '💇‍♂️ Corte de caballero', 'precio': 7000},
    'corte_niños': {'nombre': '👧 Corte de niños', 'precio': 5000},
    'color': {'nombre': '🎨 Coloración', 'precio': 15000},
    'mechas': {'nombre': '✨ Mechas', 'precio': 20000},
    'peinado': {'nombre': '💅 Peinado fiesta', 'precio': 12000},
    'barba': {'nombre': '🧔 Barba', 'precio': 4000},
}

# Memoria por usuario
conversation_memory = {}

def add_to_memory(user_id, role, content):
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []
    conversation_memory[user_id].append({"role": role, "content": content})
    if len(conversation_memory[user_id]) > 10:
        conversation_memory[user_id] = conversation_memory[user_id][-10:]

# ========== RESPUESTAS INTELIGENTES ==========
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name
    mensaje_lower = mensaje.lower()
    
    # Guardar en memoria
    add_to_memory(user_id, "user", mensaje)
    
    # ========== DETECTAR INTENCIÓN ==========
    
    # Saludos
    if re.search(r'^(hola|buenas|hey|qué tal|saludos)$', mensaje_lower):
        respuesta = f"✨ ¡Hola {user_name}! Bienvenida a Estilo & Belleza. ¿En qué te puedo ayudar hoy? 😊"
    
    # Precios
    elif re.search(r'\b(precio|cuanto cuesta|valor|cuesta|cobran|tarifa)\b', mensaje_lower):
        respuesta = "✂️ *Nuestros precios:*\n\n"
        for s in SERVICIOS.values():
            respuesta += f"{s['nombre']}: ${s['precio']:,}\n"
        respuesta += "\n¿Te interesa alguno? 😊"
    
    # Horario
    elif re.search(r'\b(horario|abren|cierran|a que hora|cuando abren)\b', mensaje_lower):
        estado = "🟢 ABIERTOS" if is_open() else "🔴 CERRADOS"
        respuesta = f"📅 *Horario:* 9 AM a 5 PM\n⏰ Último turno: 4:30 PM\n📆 Todos los días\n\n{estado}"
    
    # Ubicación
    elif re.search(r'\b(direccion|ubicacion|donde queda|como llego)\b', mensaje_lower):
        respuesta = "📍 *Dirección:* Av. Siempreviva 742\n🗺️ *Referencia:* A media cuadra de la plaza principal\n🚗 *Estacionamiento:* Disponible atrás"
    
    # Corte de pelo
    elif re.search(r'\b(corte|cortar|corto|pelo corto)\b', mensaje_lower):
        respuesta = f"✂️ ¡Qué lindo {user_name}! Tenemos cortes desde $7.000.\n\n¿Tenés alguna referencia de cómo lo querés? Podés pasar por una consulta gratis 😊"
    
    # Color/Tinte
    elif re.search(r'\b(color|tinte|pintar|teñir|mechas)\b', mensaje_lower):
        respuesta = f"🎨 El cambio de color es emocionante {user_name}.\n\nOpciones:\n• Color permanente: $15.000\n• Reflejos/Mechas: desde $20.000\n• Matización: $5.000\n\n¿Qué color tenés ahora y cuál querés lograr?"
    
    # Evento/Fiesta
    elif re.search(r'\b(fiesta|casamiento|boda|evento|15 años|peinado)\b', mensaje_lower):
        respuesta = f"🎉 ¡Qué importante {user_name}! Para tu evento te recomiendo:\n\n• Peinado elaborado: $12.000\n• Prueba de peinado: $5.000 (se descuenta)\n• Maquillaje: $8.000\n\n¿Qué fecha es tu evento?"
    
    # Pelo dañado
    elif re.search(r'\b(dañado|maltratado|quemado|seco|puntas)\b', mensaje_lower):
        respuesta = f"🌿 Entiendo {user_name}, el pelo dañado tiene solución.\n\nTe recomiendo:\n• Corte de puntas: $3.000\n• Tratamiento de keratina: desde $15.000\n• Baño de crema: $8.000\n\n¿Querés venir a una consulta gratis para evaluar tu cabello?"
    
    # Turno/Reserva
    elif re.search(r'\b(turno|cita|reservar|agendar|quiero ir|puedo ir)\b', mensaje_lower):
        dias = {'lunes': 'lunes', 'martes': 'martes', 'miércoles': 'miércoles', 
                'jueves': 'jueves', 'viernes': 'viernes', 'sábado': 'sábado', 'domingo': 'domingo',
                'hoy': 'hoy', 'mañana': 'mañana'}
        
        dia_encontrado = None
        for dia in dias:
            if dia in mensaje_lower:
                dia_encontrado = dias[dia]
                break
        
        hora_match = re.search(r'(\d{1,2})', mensaje_lower)
        
        if dia_encontrado or hora_match:
            respuesta = f"✅ ¡Perfecto {user_name}! Te anoto para el {dia_encontrado or 'día indicado'} a las {hora_match.group(0) if hora_match else 'la hora que necesites'}.\n\n📝 Confirmame tu nombre completo y servicio. ¡Te esperamos! ✨"
        else:
            respuesta = f"📅 Claro {user_name}! ¿Para qué día querés el turno?\n\nAtendemos de 9 AM a 5 PM. Decime día y horario y te confirmo disponibilidad. 😊"
    
    # Gracias
    elif re.search(r'\bgracias\b', mensaje_lower):
        respuesta = f"¡A ti {user_name}! 😊 ¿Algo más en lo que pueda ayudarte?"
    
    # Despedida
    elif re.search(r'\b(chau|adios|nos vemos|bye|hasta luego)\b', mensaje_lower):
        respuesta = f"¡Chau {user_name}! Que tengas un lindo día. Cuando quieras, acá estoy. ✂️😊"
    
    # Respuesta por defecto
    else:
        respuestas_generales = [
            f"😊 Cuéntame más {user_name}, ¿querés cortarte, cambiar de color, o algo especial para un evento? Así te ayudo mejor.",
            f"¡Hola {user_name}! 💇‍♀️ ¿Venís por un corte, color, peinado o tratamiento? Dime y te cuento todo.",
            f"Hola {user_name} ✨ ¿Qué te gustaría hacerte? Tenemos muchas opciones y te puedo recomendar según lo que busques.",
            f"🤔 No entendí bien {user_name}. Podés preguntarme por precios, horarios, o decirme 'quiero un turno'. ¿En qué te ayudo?"
        ]
        respuesta = random.choice(respuestas_generales)
    
    # Guardar respuesta en memoria
    add_to_memory(user_id, "assistant", respuesta)
    
    # Enviar respuesta
    await update.message.reply_text(respuesta, parse_mode="Markdown")

# ========== COMANDOS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    user_id = str(update.effective_user.id)
    conversation_memory[user_id] = []
    
    keyboard = [
        ["📋 Ver precios", "🕘 Ver horario"],
        ["📅 Reservar turno", "📍 Ubicación"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✨ ¡Hola {user_name}! ✨\n\n"
        f"Soy *Estela*, tu asistente de *Estilo & Belleza*. 💇‍♀️\n\n"
        f"**¿Qué necesitas?**\n"
        f"• Ver precios y servicios\n"
        f"• Consultar horarios\n"
        f"• Reservar un turno\n"
        f"• Recomendaciones para tu cabello\n\n"
        f"📅 *Horario:* 9 AM a 5 PM (todos los días)\n\n"
        f"¡Hablame como si fuera una amiga! 😊",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def precios_comando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    respuesta = "✂️ *Nuestros precios:*\n\n"
    for s in SERVICIOS.values():
        respuesta += f"{s['nombre']}: ${s['precio']:,}\n"
    respuesta += "\n¿Te interesa alguno? 😊"
    await update.message.reply_text(respuesta, parse_mode="Markdown")

async def horario_comando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    estado = "🟢 ABIERTOS ahora" if is_open() else "🔴 Ahora CERRADOS"
    await update.message.reply_text(
        f"📅 *Horario:* 9 AM a 5 PM\n"
        f"⏰ *Último turno:* 4:30 PM\n"
        f"📆 *Días:* Lunes a Domingo\n\n"
        f"{estado}\n\n"
        f"¿Querés reservar un turno? 😊",
        parse_mode="Markdown"
    )

async def ubicacion_comando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📍 *Dirección:* Av. Siempreviva 742\n"
        f"🗺️ *Referencia:* A media cuadra de la plaza principal\n"
        f"🚗 *Estacionamiento:* Disponible atrás\n\n"
        f"¡Te esperamos! 🚕",
        parse_mode="Markdown"
    )

async def reservar_comando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📅 *Reservar turno*\n\n"
        f"Decime:\n"
        f"• ¿Qué servicio querés?\n"
        f"• ¿Qué día y horario te queda bien?\n\n"
        f"Ejemplo: *'Quiero un corte de dama el martes a las 11am'*\n\n"
        f"¡Te confirmo disponibilidad al toque! 😊",
        parse_mode="Markdown"
    )

# ========== MANEJAR BOTONES ==========
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    
    if "precios" in texto.lower():
        await precios_comando(update, context)
    elif "horario" in texto.lower():
        await horario_comando(update, context)
    elif "turno" in texto.lower() or "reservar" in texto.lower():
        await reservar_comando(update, context)
    elif "ubicación" in texto.lower() or "ubicacion" in texto.lower():
        await ubicacion_comando(update, context)
    else:
        await manejar_mensaje(update, context)

# ========== MAIN ==========
def main():
    # Verificar token
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "AQUI_VA_TU_TOKEN_DE_TELEGRAM":
        print("\n❌ ERROR: No configuraste el TOKEN de Telegram!")
        print("Editá el archivo y poné tu token en TELEGRAM_TOKEN\n")
        return
    
    # Mostrar información del bot (sin usar TOKEN que no existe)
    print("\n🤖 BOT INICIADO CORRECTAMENTE")
    print("📱 Tu bot está listo para recibir mensajes")
    print("💬 El bot detecta: precios, horarios, turnos, cortes, colores, eventos, pelo dañado\n")
    
    # Crear y ejecutar la aplicación
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("precios", precios_comando))
    app.add_handler(CommandHandler("horario", horario_comando))
    app.add_handler(CommandHandler("ubicacion", ubicacion_comando))
    app.add_handler(CommandHandler("reservar", reservar_comando))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, botones))
    
    app.run_polling()

if __name__ == "__main__":
    main()
