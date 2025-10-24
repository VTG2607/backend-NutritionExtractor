# Nutrition Extractor (NutriExtract-inator)

## Tech Stack
* Flask
* React
* Tailwind
* Openai
* Tesseract


## Purpose
The backend for the Nutrition and Allergen Extractor miniapp, it uses openAI gpt model and tesseractOCR to scan typed/scanned PDF documents for
allergens and Nutritional value and returns that data in a readable form on the frontend

## How to install
*  Clone the Repository
git clone https://github.com/VTG2607/backend-NutritionExtractor.git
cd backend-NutritionExtractor/backend

*  Create a Virtual Environment
> ```bash```
``git clone https://github.com/VTG2607/backend-NutritionExtractor.git``
``cd backend-NutritionExtractor/backend``

Activate it:
Windows

> ``venv\Scripts\activate``


macOS/Linux

> ``source venv/bin/activate``

Install Dependencies
> ``pip install -r requirements.txt``


Ensure your requirements.txt includes:

Flask
gunicorn
pytesseract
openai
Pillow
python-dotenv

Environment Variables

Create a .env file in the backend folder:

> ``FLASK_ENV=development``
> ``OPENAI_API_KEY=your_openai_api_key``
> ``TESSERACT_CMD=/usr/bin/tesseract   # Adjust path if needed``


*  Running Locally
> ``python app.py``


By default, Flask runs on:

> ``http://localhost:5000``

## Endpoint(s)
**POST /upload**

Description:
Upload a scanned or typed PDF and extract allergens and nutritional information.

Request:
>Type: multipart/form-data
>Body: file <uploaded PDF file>


Response Example:

> ``` json 
>   {
>   "allergens": ["milk", "soy", "gluten"],
>   "nutritional_values": {
>     "Calories": "210 kcal",
>     "Fat": "12g",
>     "Carbohydrates": "18g",
>     "Protein": "5g"
>   }
> }
> 
> 
> Error Responses:
> 
> { "error": "No file uploaded" }
> 
> { "error": "Invalid file type" }




## Deployment

The app was deployed using Heroku


## Functions

### Function: ExtractTextPdf(pdf)
>``` python
>def ExtractTextPdf(pdf):
>    text = ''
>    with pymupdf.open(stream=pdf, filetype="pdf") as doc:
>        for page in doc:
>            page_text = page.get_text("text")
>            if page_text.strip():  # if there is text
>                text += page_text
>            else:
>                pix = page.get_pixmap()  # Converts page to image (for OCR)
>                img = Image.open(io.BytesIO(pix.tobytes("png")))
>                text += pytesseract.image_to_string(img)
>    return text 

**Description**

Extracts readable text from a given PDF file.

Uses PyMuPDF to detect embedded text and Tesseract OCR to extract text from scanned image pages.
Combines both methods to ensure all text—typed or scanned—is captured.

**Parameters**
* pdf: The pdf file read as data

**Return**
* str	The combined extracted text from all pages of the PDF.
### Function: ExtractDataAi(text)
> ``` Python
>def ExtractDataAi(text):
>    prompt =  f"""
>    Extract allergens and nutritional values from the following text. Convert all the allergens to english.
>    Alot of the data will be in tables and in formats like kj/100g, g/100g or be in the form of checked boxes,
>    mixed in with highly technical info, etc....
>    be sure to extract all of it
>
>    Output only valid JSON with this format:
>
>    {{
>      "allergens": ["list of found allergens"(if none found put "none", 
>      if it was in another language originally, put the scanned allergen's original word in "()" right next to the allergen)],
>      "nutritional_values": {{
>        "Energy": "...",
>        "Fat": "...",
>        "Carbohydrate": "...",
>        "Sugar": "...",
>        "Protein": "...",
>        "Sodium": "..."
>        (if they are not specified put "none" for all fields except Energy, which puts "not specified",
>        put the scanned language's version of the key fields next to them in "()" as part of the key field)
>      }}
>    }}
>    
>    Text:
>    {text}
>    """
>
>    response = client.chat.completions.create(
>        model="gpt-4o-mini",
>        messages=[{"role": "user", "content": prompt}],
>        response_format={"type": "json_object"}
>    )
>
>    return response.choices[0].message.content ```

**Description**

Uses the OpenAI API to analyze extracted text and identify both allergens and nutritional values.
The AI is instructed to handle mixed-language and table-based data and to output structured JSON.

**Parameters**
* text : 	the extracted text that will be analyzed for the needed nutritional and allergen data

**Returns**
* str: 	JSON-formatted string containing allergens and nutritional data.


**Route: /extract**
>```python
>@app.route('/extract', methods=["POST"])
>def extract():
>    if "file" not in request.files:
>        return jsonify({"error": "No file uploaded"}), 400
>
>    file = request.files["file"]
>    pdf = file.read()
>    text = ExtractTextPdf(pdf)
>
>    if not text.strip():
>        return jsonify({"error": "Could not extract text"}), 400
>
>    ai_result = ExtractDataAi(text)
>    return ai_result

**Description**

Main Flask endpoint that handles PDF uploads from the frontend.
Performs text extraction and sends the results to the AI model for data analysis.

Request

Method: POST

Form Field: file — a PDF file uploaded from the client side.

Workflow

Checks if a file is present in the request.

Reads the file content as bytes.

Extracts all text using ExtractTextPdf().

Passes the extracted text to ExtractDataAi() for AI analysis.

Returns the AI-generated JSON response to the frontend.

**Responses**
Status Code	Description
200	Successfully extracted and analyzed data.
400	File missing or no text could be extracted.
Flask App Setup
>
>if __name__ == '__main__':
>   port = int(os.environ.get("PORT", 5000))
>   debug = os.environ.get("FLASK_DEBUG", "False") == "True"
>   app.run(host="0.0.0.0", port=port, debug=debug)

**Description**

Bootstraps the Flask server, using environment variables for configuration.

**Environment Variables**
Variables
1. PORT: Port to run the server on (default: 5000)
2. FLASK_DEBUG:	Enables Flask debug mode (default:	False)
3. Supporting Setup
CORS Configuration
CORS(app, origins=["https://frontend.com"])


Allows requests only from the specified frontend domain to prevent unauthorized cross-origin access.

OpenAI Client Initialization
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


Loads your OpenAI API key from the environment and initializes the client for GPT-based analysis.
