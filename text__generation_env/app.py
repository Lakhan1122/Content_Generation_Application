from flask import Flask, request, jsonify, render_template
import openai
from PyPDF2 import PdfReader



app = Flask(__name__)

# Configure OpenAI with your API key
openai.api_key = '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'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate',methods=['GET'])
def text():
    return render_template('text_generator.html')
    
@app.route('/pdf',methods=['GET'])
def reader():
    return render_template('document_summarization.html')

@app.route('/emotions',methods=['GET'])
def anal():
    return render_template('sentiment_analysis.html')

@app.route('/generate-text', methods=['POST'])
def generate_text():
     

    try:
        data = request.get_json()
        keyword = data['keyword']

        # Create a list of messages to maintain conversation history
        messages = [{"role": "system", "content": "You are a helpful assistant."}]

        # Add the user's message with the keyword
        messages.append({"role": "user", "content": keyword})

        # Generate text with context
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
       

        generated_text = response.choices[0].message['content']
        return jsonify({"text": generated_text})

    except Exception as e:
        return jsonify({"error": str(e)})
    
   


def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

@app.route('/summarization', methods=['POST'])
def summarization():
    try:
        # Handle the uploaded files (both TXT and PDF)
        uploaded_files = request.files.getlist('files')

        if not uploaded_files or len(uploaded_files) == 0:
            return jsonify({"error": "Please upload at least one valid file."}), 400

        file_contents = []

        for file in uploaded_files:
            content = ""
            if file.mimetype == "text/plain":
                # Read the contents of a TXT file
                content = file.read().decode('utf-8')
            elif file.mimetype == "application/pdf":
                # Read the contents of a PDF file
                content = extract_text_from_pdf(file)

            file_contents.append(content)

        # Create conversation messages with system message, user request, and file contents
        summary_request = request.form.get("summaryRequest", "")
        messages = [
            {"role": "system", "content": "You are a summarization assistant."},
            {"role": "user", "content": f"Please make a summary of the content from the below files for: {summary_request}"},
            * [{"role": "user", "content": content} for content in file_contents],
        ]

        # Request a summary from the OpenAI model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            # temperature=0.9,
            # max_tokens=2000
        )

        # Return the generated summary to the client
        return jsonify({"summary": response.choices[0].message['content']})

    except Exception as e:
        print("Error in /summarization route:", str(e))
        return jsonify({"error": "An error occurred while processing the request."}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        text = data['text']

        # Use the OpenAI GPT-3.5 Turbo model to analyze sentiment and recognize emotions
        messages = [
            {"role": "system", "content": "You are an emotion recognition assistant."},
            {"role": "user", "content": f"Provide a single-word response after analyzing this text: {text}"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        # Extract sentiment and emotion analysis results
        result = response.choices[0].message['content']

        return jsonify({"result": result})

    except Exception as error:
        print('Error in /analyze route:', str(error))
        return jsonify({"error": "An error occurred while processing the request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
