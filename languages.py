translations = {
    "Hello! I'm your Sofen chat bot, I can help you to to download youtube videos\n use the command /download then send me the youtube link \n I will reply back with a direct download link ! \n Have a good time.": "مرحبًا! أنا بوت الدردشة Sofen الخاص بك، يمكنني مساعدتك في تنزيل مقاطع الفيديو من يوتيوب. استخدم الأمر /download ثم أرسل لي رابط الفيديو، وسأرد عليك برابط التحميل المباشر! أتمنى لك وقتًا طيبًا.",
    "What is your preferred language?": "ما هي اللغة التي تفضلها؟",
    "AR": "العربية",
    "EN": "الإنجليزية",
    "Invalid option. Please try again.": "خيار غير صالح. يرجى المحاولة مرة أخرى.",
    "Your preferred language is ": "لغتك المفضلة هي ",
    "Welcome to Sofen bot": "مرحبًا بك في بوت Sofen",
    "Use the command /download then send me the youtube/ instagram link \n I will reply back with the video or direct download link! \n Have a good time.": "استخدم الأمر /download ثم أرسل لي رابط الفيديو، وسأرد عليك بالفيديو او برابط التحميل المباشر! أتمنى لك وقتًا طيبًا."
}

def translate_text(text, preferred_lang):
    if preferred_lang == "AR":
        return translations.get(text, text)
    else:
        return text