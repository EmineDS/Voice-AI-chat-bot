import google.generativeai as genai
import os
import speech_recognition as sr
from gtts import gTTS
import pygame
import time

# Google Generative AI API anahtarınızı buraya ekleyin
api_key = "********************************************"
genai.configure(api_key=api_key)

# Ses tanıyıcı nesne oluştur
recognizer = sr.Recognizer()


def generate_response(text):
    """Generative AI ile yanıt üretir."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(text)
    if response and response.parts:
        return response.parts[0].text
    return "Yanıt alınamadı."


def text_to_speech(text):
    """Metni sese dönüştürür ve bir MP3 dosyası olarak kaydeder."""
    tts = gTTS(text=text, lang='tr')
    filename = "response.mp3"
    tts.save(filename)
    return filename


def play_audio(filename):
    """Ses dosyasını oynatır ve oynatma tamamlandığında döner."""
    if not os.path.exists(filename):
        print(f"Ses dosyası bulunamadı: {filename}")
        return

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Ses çalmayı bitene kadar bekle
        pygame.time.Clock().tick(10)
    pygame.mixer.music.stop()  # Oynatmayı durdur
    pygame.mixer.quit()  # Pygame'i kapat


def main():
    """Sürekli çalışan sesli asistan."""
    print("Dinlemeye başladım. Lütfen bir şeyler söyleyin.")
    while True:
        try:
            with sr.Microphone() as source:
                # Ortam gürültüsünü ayarla
                recognizer.adjust_for_ambient_noise(source, duration=1)

                # Ses algılanana kadar bekle
                print("Dinleniyor...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                # Sesin olup olmadığını kontrol et
                if audio:
                    try:
                        text = recognizer.recognize_google(audio, language="tr-TR")
                        print("Duyulan ses: " + text)

                        # Yanıt üret
                        response_text = generate_response(text)
                        print("Generative AI Yanıtı: " + response_text)

                        # Yanıtı sesli olarak geri ver
                        audio_file = text_to_speech(response_text)
                        if os.path.exists(audio_file):
                            print("Ses dosyası başarıyla oluşturuldu ve kaydedildi.")
                            play_audio(audio_file)
                            # Ses dosyasının tamamen kapatıldığından emin olmak için bekleyin
                            time.sleep(2)
                            try:
                                os.remove(audio_file)
                                print("Ses dosyası başarıyla silindi.")
                            except Exception as e:
                                print(f"Ses dosyası silinirken bir hata oluştu: {e}")
                        else:
                            print("Ses dosyası oluşturulamadı.")
                    except sr.UnknownValueError:
                        print("Ses anlaşılamadı.")
                    except sr.RequestError as e:
                        print(f"Servise bağlanılamadı: {e}")
                else:
                    print("Ses algılanamadı.")

        except Exception as e:
            print(f"Bir hata oluştu: {e}")


if __name__ == "__main__":
    main()
