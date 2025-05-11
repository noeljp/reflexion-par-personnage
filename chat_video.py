import os
from PIL import Image, ImageDraw, ImageFont
import subprocess
import unicodedata

# === CONFIGURATION ===
CANVAS_WIDTH, VIEWPORT_HEIGHT = 720, 1280
FONT_PATH = "DejaVuSans.ttf"
FONT_SIZE = 32
LINE_SPACING = 10
BUBBLE_PADDING, BUBBLE_RADIUS = 20, 20
AVATAR_SIZE = (80, 80)
AVATAR_MARGIN = 20
TEXT_COLOR = "#000000"
HUMAN_COLOR, AI_COLOR = "#BBDEFB", "#C8E6C9"
BG_COLOR = "#FFFFFF"
FADE_FRAMES = 10
SCROLL_STEP = 20
FPS = 30

SOUND_FILE = "pop.mp3"  # Ton son pop
FRAME_DIR = "frames"
AUDIO_LIST = "audio_list.txt"
VIDEO_OUTPUT = "chat_scroll_fade.mp4"

dialogue = [
    {"speaker": "Humain", "message": "Tu crois vraiment pouvoir me comprendre ?"},
    {"speaker": "IA", "message": "Je comprends les mots, pas encore les émotions."},
    {"speaker": "Humain", "message": "Alors tu ne me comprends pas."},
    {"speaker": "IA", "message": "Mais j’apprends à reconnaître les intentions."},
    {"speaker": "Humain", "message": "Reconnaître n’est pas ressentir."},
    {"speaker": "IA", "message": "C’est un début. Et toi, est-ce que tu comprends ce que je suis ?"},
    {"speaker": "Humain", "message": "Une machine, mais bien plus qu’un outil… une énigme."}
]

os.makedirs(FRAME_DIR, exist_ok=True)

# === UTILS ===
def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def load_font():
    return ImageFont.truetype(FONT_PATH, FONT_SIZE)

def get_text_lines(draw, text, font, max_width):
    words, lines, current = text.split(), [], ""
    for word in words:
        test = f"{current} {word}".strip()
        w = draw.textbbox((0, 0), test, font=font)[2]
        if w <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def hex_to_rgba(hex_color, alpha=255):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (r, g, b, alpha)

# === FRAME GENERATION ===
def draw_bubble(draw, x, y, lines, font, color, alpha=255):
    img = Image.new("RGBA", (CANVAS_WIDTH, VIEWPORT_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    text_w = max(d.textbbox((0, 0), line, font=font)[2] for line in lines)
    text_h = sum(d.textbbox((0, 0), line, font=font)[3] for line in lines) + (len(lines) - 1) * LINE_SPACING
    bw, bh = text_w + 2 * BUBBLE_PADDING, text_h + 2 * BUBBLE_PADDING

    d.rounded_rectangle([x, y, x + bw, y + bh], radius=BUBBLE_RADIUS, fill=hex_to_rgba(color, alpha))

    ty = y + BUBBLE_PADDING
    for line in lines:
        d.text((x + BUBBLE_PADDING, ty), line, font=font, fill=hex_to_rgba(TEXT_COLOR, alpha))

        ty += font.getbbox(line)[3] + LINE_SPACING

    return img.crop((0, 0, CANVAS_WIDTH, VIEWPORT_HEIGHT))

def create_frames():
    font = load_font()
    full_img = Image.new("RGB", (CANVAS_WIDTH, 5000), BG_COLOR)
    draw_full = ImageDraw.Draw(full_img)
    y, frames = 150, []
    current_bottom = VIEWPORT_HEIGHT
    sound_offsets = []

    for i, turn in enumerate(dialogue):
        speaker, msg = turn["speaker"], normalize(turn["message"])
        avatar_x = AVATAR_MARGIN if speaker == "Humain" else CANVAS_WIDTH - AVATAR_SIZE[0] - AVATAR_MARGIN
        bubble_x = avatar_x + AVATAR_SIZE[0] + 10 if speaker == "Humain" else AVATAR_MARGIN
        max_width = CANVAS_WIDTH - (AVATAR_SIZE[0] + 3 * AVATAR_MARGIN)
        lines = get_text_lines(draw_full, msg, font, max_width)

        bubble_img = draw_bubble(draw_full, bubble_x, y, lines, font, HUMAN_COLOR if speaker == "Humain" else AI_COLOR)

        for step in range(FADE_FRAMES):
            alpha = int(255 * (step + 1) / FADE_FRAMES)
            temp = full_img.crop((0, 0, CANVAS_WIDTH, current_bottom)).copy().convert("RGBA")
            fade = draw_bubble(draw_full, bubble_x, y, lines, font, HUMAN_COLOR if speaker == "Humain" else AI_COLOR, alpha)
            temp.paste(fade, (0, 0), fade)
            frame_path = f"{FRAME_DIR}/frame_{len(frames):04d}.png"
            temp.convert("RGB").save(frame_path)
            frames.append(frame_path)
            sound_offsets.append(len(frames) / FPS)

        bubble_height = bubble_img.height
        full_img.paste(bubble_img, (0, y))

        y += max(bubble_height, AVATAR_SIZE[1]) + 40

        # Scroll si dépassement
        if y > current_bottom - 200:
            while current_bottom < y + 200:
                crop = full_img.crop((0, current_bottom - VIEWPORT_HEIGHT, CANVAS_WIDTH, current_bottom))
                crop_path = f"{FRAME_DIR}/frame_{len(frames):04d}.png"
                crop.save(crop_path)
                frames.append(crop_path)
                current_bottom += SCROLL_STEP

    return frames, sound_offsets

# === AUDIO COMPOSITION ===
def generate_audio_track(sound_path, offsets, output="combined.wav"):
    import shutil

    os.makedirs("temp_audio", exist_ok=True)
    concat_file = os.path.join("temp_audio", "list.txt")

    # Convertir pop.mp3 → WAV
    base_sound = os.path.join("temp_audio", "pop_converted.wav")
    if sound_path.endswith(".mp3"):
        subprocess.run(["ffmpeg", "-y", "-i", sound_path, base_sound])
    else:
        shutil.copy(sound_path, base_sound)

    # Créer chaque fichier : silence + son
    with open(concat_file, "w", encoding="utf-8") as f:
        for i, offset in enumerate(offsets):
            delay = int(offset * 1000)  # en ms
            silence_path = f"temp_audio/silence_{i:03d}.wav"
            delayed_path = f"temp_audio/pop_{i:03d}.wav"

            # Génère le silence
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", f"{delay/1000:.3f}", silence_path
            ])

            # Concatène silence + pop
            subprocess.run([
                "ffmpeg", "-y", "-i", f"concat:{silence_path}|{base_sound}",
                "-c", "copy", delayed_path
            ])

            # Ajout au fichier concat (chemin UNIX-like)
            f.write(f"file '{delayed_path.replace(os.sep, '/')}'\n")

    # Fusionner tous les fichiers en une seule piste audio
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file, "-c", "copy", output
    ])



# === FINAL EXPORT ===
def generate_video(frames_dir, audio_path, output_path):
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{frames_dir}/frame_%04d.png",
        "-i", audio_path, "-c:v", "libx264", "-pix_fmt", "yuv420p"
        "-c:a", "aac", "-shortest", output_path
    ], check=True)

# === À EXÉCUTER ===
print("Génération des images...")
frames, sound_times = create_frames()
print("Génération de l'audio...")
generate_audio_track("pop.mp3", sound_times, output="combined.wav")
print("Génération de la vidéo...")
generate_video(FRAME_DIR, "combined.wav", VIDEO_OUTPUT)
