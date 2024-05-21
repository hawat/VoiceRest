from playsound import playsound, PlaysoundException
import requests






def send_text_and_get_wav(text, filename, api_url="http://192.168.4.29:8000/voice/"):
    """Sends text to a text-to-speech API and downloads the generated WAV file.

    Args:
        text: The text to convert to speech.
        filename: The desired filename for the downloaded WAV file.
        api_url: The base URL of the text-to-speech API (optional, default provided).
    """

    data = {
        "text": text,
        "filename": filename,
        "lang": "pl"
    }

    try:
        response = requests.post(api_url, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)

        # Handle the response content (WAV file)
        with open(filename, "wb") as f:
            f.write(response.content)

        print(f"Audio file '{filename}' downloaded successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


# Example usage
text_to_convert = "Kocham CIę moja Agnieszko!"
filename_to_save = "audio.wav"
send_text_and_get_wav(text_to_convert, filename_to_save)
try:
    playsound(filename_to_save)
except PlaysoundException as e:
    print("Error playing sound:", e)