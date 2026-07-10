import io
import math
import telebot
import google.generativeai as genai

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8831883079:AAFVN7IBLx9rUPODFZMUbTRJaXY7QiSZNNw"
GEMINI_API_KEY = "AQ.Ab8RN6LZFH6XNb4v7DEA7trTDa-jttX2WJJrpFmL0a4fXEcrSA"

# Bot aur Gemini setup
bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🤖 **SPYDER AI SQUAD SCANNER ON** 🤖\n\n"
        "Bhai, Render cloud par tumhara permanent server active hai!\n"
        "Apne FC Mobile team ka clear screenshot direct chat par send karo.\n\n"
        "AI poore 11 players ka Base OVR aur Ranks scan karke instantly next OVR ka exact target bata dega!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    status_msg = bot.reply_to(message, "🔍 Spyder AI aapka squad screenshot scan kar raha hai... Please wait.")
    
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "Analyze this FC Mobile squad screenshot. Identify the 11 active starting players. "
            "Extract their Base OVR (number between 60-110) and their Rank Up level (count the colored gem rank: 0 if no rank, 1 for Green, 2 for Blue, 3 for Purple, 4 for Red, 5 for Orange). "
            "Output ONLY the raw data in this exact format for 11 players, nothing else:\n"
            "P1: OVR,Rank\n"
            "P2: OVR,Rank\n"
            "... up to P11."
        )

        cookie_image = {"mime_type": "image/jpeg", "data": downloaded_file}
        result = model.generate_content([prompt, cookie_image])
        ai_output = result.text.strip()
        
        print(f"[AI RAW RESPONSE]:\n{ai_output}")

        total_base = 0
        total_rank = 0
        player_count = 0

        lines = ai_output.split('\n')
        for line in lines:
            if line.startswith('P') and ':' in line:
                try:
                    data_part = line.split(':')[1].strip()
                    parts = data_part.split(',')
                    if len(parts) == 2:
                        total_base += float(parts[0])
                        total_rank += float(parts[1])
                        player_count += 1
                except:
                    continue

        if player_count == 11:
            base_avg = total_base / 11
            rank_avg = total_rank / 11

            final_base = math.ceil(base_avg)
            final_rank = math.ceil(rank_avg)
            final_team_ovr = final_base + final_rank

            next_base_target = final_base if base_avg != final_base else final_base + 1
            base_points_needed = (next_base_target * 11) - total_base

            next_rank_target = final_rank if rank_avg != final_rank else final_rank + 1
            rank_points_needed = (next_rank_target * 11) - total_rank

            report = (
                f"🤖 *SPYDER AI SQUAD REPORT* 🤖\n\n"
                f"🛡️ *Calculated Team OVR: {final_team_ovr}*\n\n"
                f"📊 *Current Breakdown:*\n"
                f"• Base Avg: {base_avg:.2f} -> ({final_base})\n"
                f"• Rank Avg: {rank_avg:.2f} -> ({final_rank})\n\n"
                f"🎯 *Next OVR Target ({final_team_ovr + 1}):*\n"
                f"• Squad mein kul *+{int(base_points_needed)} Base OVR* badhana hoga.\n"
                f"👉 _YA PHIR_\n"
                f"• Squad mein kul *+{int(rank_points_needed)} Rank Up* points badhane honge.\n\n"
                f"_Processed 24x7 via Render Cloud without Ads._"
            )
            bot.edit_message_text(report, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text("❌ AI screenshot se poore 11 players scan nahi kar paya. Kripya ek clear aur bina crop kiya hua screenshot bhejein.", chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        print(f"[ERROR]: {e}")
        bot.edit_message_text("❌ Error aaya processing mein. Kripya screenshot clear bhejein.", chat_id=message.chat.id, message_id=status_msg.message_id)

if __name__ == '__main__':
    print("Bot is starting...")
    bot.infinity_polling()
