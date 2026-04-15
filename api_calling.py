from google import genai
from dotenv import load_dotenv
import os, io
from gtts import gTTS

load_dotenv()
my_api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=my_api_key)
except Exception as e:
    raise RuntimeError(f"Gemini client initialize করতে সমস্যা হয়েছে: {e}")


# ── Language Detector ─────────────────────────────────────────────────────────
def detect_language(images):
    """
    Image গুলো দেখে Bangla না English তা detect করে।
    Return করে: "bn" (Bangla) অথবা "en" (English)
    """
    prompt = """
    Look at the text content in the provided image(s).
    Determine the PRIMARY language of the written text.

    Reply with ONLY one of these two words, nothing else:
    - "Bengali" → if the text is primarily written in Bengali/Bangla script
    - "English" → if the text is primarily written in English or any other Latin script
    """
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[images, prompt]
        )
        result = response.text.strip().lower()
        return "bn" if "bengali" in result else "en"

    except Exception as e:
        # detect না হলে default English
        return "en"


# ── Note Generator ────────────────────────────────────────────────────────────
def note_generator(images):
    """
    PIL image list নিয়ে structured markdown note তৈরি করে।
    Image Bangla হলে Bangla তে, English হলে English এ লেখে।
    Returns: (note_text, detected_lang)
    """
    lang = detect_language(images)

    if lang == "bn":
        prompt = """
        তুমি একজন দক্ষ শিক্ষার্থী এবং নোট-রাইটার। প্রদত্ত ছবি(গুলো) মনোযোগ দিয়ে বিশ্লেষণ করো এবং সুসংগঠিত, সংক্ষিপ্ত নোট তৈরি করো।

        নির্দেশনা:
        - নোটটি সম্পূর্ণ **বাংলায়** লেখো
        - সঠিক Markdown formatting ব্যবহার করো:
            - `#` মূল বিষয়/শিরোনামের জন্য
            - `##` প্রধান অনুচ্ছেদের জন্য
            - `###` উপ-অনুচ্ছেদের জন্য (প্রয়োজন হলে)
            - Bullet points (`-`) গুরুত্বপূর্ণ তথ্য বা তালিকার জন্য
            - **Bold** গুরুত্বপূর্ণ শব্দ বা সংজ্ঞার জন্য
        - মোট দৈর্ঘ্য **১৫০–২০০ শব্দের** মধ্যে রাখো — বিস্তারিত কিন্তু সংক্ষিপ্ত
        - সবচেয়ে গুরুত্বপূর্ণ ধারণা, সংজ্ঞা এবং তথ্য তুলে ধরো
        - সূত্র বা কঠিন শব্দ থাকলে সেগুলো স্পষ্টভাবে অন্তর্ভুক্ত করো
        - শেষে একটি সংক্ষিপ্ত **"মূল বিষয়"** অনুচ্ছেদ যোগ করো (১–২ বাক্য)

        শুধুমাত্র formatted নোটটি output করো, অন্য কিছু নয়।
        """
    else:
        prompt = """
        You are an expert academic note-taker. Analyze the provided image(s) carefully and generate 
        a well-structured, concise summary note.

        Instructions:
        - Write the note in **clear academic English**
        - Use proper Markdown formatting:
            - `#` for the main topic/title
            - `##` for major sections
            - `###` for sub-sections if needed
            - Bullet points (`-`) for key facts or lists
            - **Bold** for important terms or keywords
        - Keep the total length between **150–200 words** — detailed but concise
        - Extract and highlight the **most important concepts, definitions, and facts**
        - If there are formulas or technical terms, include them clearly
        - End with a short **"Key Takeaway"** section (1–2 sentences)

        Output only the formatted note, nothing else.
        """

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[images, prompt]
        )
        return response.text, lang

    except Exception as e:
        raise RuntimeError(f"Note generate করতে সমস্যা হয়েছে: {e}")


# ── Audio Transcription ───────────────────────────────────────────────────────
def audio_transcription(text, lang="en"):
    """
    Text নিয়ে gTTS দিয়ে audio বানায়।
    lang="bn" হলে Bangla audio, "en" হলে English audio।
    """
    if not text or not text.strip():
        raise ValueError("Audio তৈরির জন্য text খালি হতে পারবে না।")

    # Markdown symbols সরানো যাতে audio smooth হয়
    symbols_to_remove = ["#", "*", "-", "'", "(", ")", "`", ">", "_", "~", "|", "✅"]
    clean_text = text
    for symbol in symbols_to_remove:
        clean_text = clean_text.replace(symbol, "")
    clean_text = " ".join(clean_text.split())  # extra whitespace সরানো

    try:
        speech = gTTS(clean_text, lang=lang, slow=False)
        audio_buffer = io.BytesIO()
        speech.write_to_fp(audio_buffer)
        audio_buffer.seek(0)  # buffer এর শুরুতে ফিরে আসা — না হলে audio play হয় না
        return audio_buffer

    except Exception as e:
        raise RuntimeError(f"Audio generate করতে সমস্যা হয়েছে: {e}")


# ── Quiz Generator ────────────────────────────────────────────────────────────
def quize_generator(images, difficulty, lang="en"):
    """
    PIL image list ও difficulty level নিয়ে MCQ quiz তৈরি করে।
    lang="bn" হলে Bangla তে quiz, "en" হলে English এ।
    """

    if lang == "bn":
        difficulty_labels = {
            "Easy": "সহজ — মূল সংজ্ঞা ও সরল তথ্য মনে রাখার প্রশ্ন",
            "Medium": "মাঝারি — ধারণার প্রয়োগ ও যুক্তিভিত্তিক প্রশ্ন",
            "Hard": "কঠিন — বিশ্লেষণ, তুলনা ও গভীর বোঝাপড়ার প্রশ্ন"
        }
        guideline = difficulty_labels.get(difficulty, "মাঝারি — ধারণার প্রয়োগ ও যুক্তিভিত্তিক প্রশ্ন")

        prompt = f"""
        তুমি একজন দক্ষ প্রশ্নকর্তা। প্রদত্ত ছবি(গুলো)-র বিষয়বস্তুর উপর ভিত্তি করে ঠিক **৫টি বহুনির্বাচনী প্রশ্ন (MCQ)** তৈরি করো।
        কঠিনতার মাত্রা: **{difficulty}** ({guideline})

        প্রতিটি প্রশ্ন ঠিক এই format এ লেখো:

        ---
        **প্র[নম্বর]. [প্রশ্নের বাক্য]**

        - ক) [বিকল্প ক]
        - খ) [বিকল্প খ]
        - গ) [বিকল্প গ]
        - ঘ) [বিকল্প ঘ]

        ✅ **উত্তর: [সঠিক বিকল্পের অক্ষর]) [সঠিক উত্তরের বাক্য]**

        *ব্যাখ্যা: [১–২ বাক্যে কেন এই উত্তর সঠিক তা বাংলায় বলো]*

        ---

        নিয়মাবলী:
        - সব প্রশ্ন অবশ্যই ছবির বিষয়বস্তু থেকে হতে হবে
        - প্রতিটি প্রশ্নে ঠিক ৪টি বিকল্প (ক, খ, গ, ঘ) থাকতে হবে
        - শুধুমাত্র একটি বিকল্প সঠিক হবে
        - ভুল বিকল্পগুলো যুক্তিসংগত কিন্তু স্পষ্টভাবে ভুল হওয়া উচিত
        - প্রশ্নের ধরন বৈচিত্র্যময় রাখো (সংজ্ঞা, প্রয়োগ, তুলনা ইত্যাদি)
        - একই ধরনের প্রশ্ন পুনরাবৃত্তি করবে না
        - সম্পূর্ণ বাংলায় লেখো

        শুধুমাত্র ৫টি formatted প্রশ্ন output করো, অন্য কিছু নয়।
        """
    else:
        difficulty_guidelines = {
            "Easy": "basic recall questions, straightforward definitions, simple concepts",
            "Medium": "application-based questions, moderate reasoning, concept connections",
            "Hard": "analysis and evaluation questions, complex reasoning, edge cases, deeper understanding"
        }
        guideline = difficulty_guidelines.get(difficulty, "moderate reasoning and concept understanding")

        prompt = f"""
        You are an expert quiz creator. Based on the content in the provided image(s), generate exactly 
        **5 multiple-choice questions (MCQ)** at **{difficulty}** difficulty level.

        Difficulty guideline for {difficulty}: {guideline}

        Format each question EXACTLY like this:

        ---
        **Q[number]. [Question text]**

        - A) [Option A]
        - B) [Option B]
        - C) [Option C]
        - D) [Option D]

        ✅ **Answer: [Correct option letter]) [Correct answer text]**

        *Explanation: [1–2 sentence explanation of why this answer is correct]*

        ---

        Rules:
        - All questions must be directly based on the image content
        - Each question must have exactly 4 options (A, B, C, D)
        - Only one option should be correct
        - Distractors (wrong options) should be plausible but clearly incorrect
        - Vary the question types (definition, application, comparison, etc.)
        - Do NOT repeat similar questions
        - Ans formate ta button die hide rakho.

        Output only the 5 formatted questions, nothing else.
        """

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[images, prompt]
        )
        return response.text

    except Exception as e:
        raise RuntimeError(f"Quiz generate করতে সমস্যা হয়েছে: {e}")