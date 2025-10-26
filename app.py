from flask import Flask, request, jsonify
from flask_cors import CORS
import pymupdf
import pytesseract
from PIL import Image
import io
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # initialize an instance of the OpenAI class with an api key
app = Flask(__name__)

is_debug = os.environ.get("FLASK_DEBUG", "False") == "True"

if is_debug:
    # Local development
    CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])
else:
    CORS(app, origins=["https://frontend-nutritionextract.onrender.com"])


def ExtractTextPdf(pdf):
    text = ''
    with pymupdf.open(stream=pdf, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text("text")
            if page_text.strip(): # if there is text
                text += page_text

            else:

                pix  = page.get_pixmap() #Converts page to pixmap (for OCR)
                img = Image.open(io.BytesIO(pix.tobytes("png"))) # pix.tobytes("png") turns the pixmap the raw binary data of the page,  io.BytesIO() creates a file-like object from bytes in memory.
                text += pytesseract.image_to_string(img) # tesseract turns the "image" to string

    return    text

def ExtractDataAi(text):
    prompt =  f"""
    Extract allergens and nutritional values from the following text. Convert all the allergens to english.
    Alot of the data will be in tables and in formats like kj/100g, g/100g or  be in the form of checked boxes,
    +/-(yes/no) lists, mixed in with highly technical info, etc....
    be sure to extract all of it

    Output only valid JSON with this format:

    {{
      "allergens": ["list of found allergens"(if none found put "none", 
      if it was in another language originally, put the scanned allergen's original word in "()" right next to the allergen)],
      "nutritional_values": {{
        "Energy": "...",
        "Fat": "...",
        "Carbohydrate": "...",
        "Sugar": "...",
        "Protein": "...",
        "Sodium": "..."
        (if they are not specified put "none" for all fields except Energy, which puts "not specified",
        put the scanned language's version of the key fields next to them in "()" as part of the key field)
      }}
    }}
    
  

    Text:
    {text}
    """

    # calling the OpenAI Chat Completions API, through the official Python SDK
    response = client.chat.completions.create(
        model="gpt-4o-mini", # the model of gpt used
        messages=[{"role": "user", "content": prompt}], 
        response_format={"type": "json_object"} #give response in json
    )

    return response.choices[0].message.content # grabs the response.

@app.route('/extract', methods=["POST"])
def extract():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]  # get the file from the uploaded files with the key "file"
    pdf = file.read() # read the file
    text = ExtractTextPdf(pdf) #Extract text

    if not text.strip():
        return jsonify({"error": "Could not extract text"}), 400


    ai_result = ExtractDataAi(text) # use Ai to analyze text


    return ai_result

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False") == "True"
    app.run(host="0.0.0.0", port=port, debug=debug)