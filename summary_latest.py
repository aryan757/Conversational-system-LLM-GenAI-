from transformers import BartForConditionalGeneration, AutoTokenizer
from flask import Flask, request, jsonify

app = Flask(__name__)  # Correct usage of __name__

model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

def summarize(text):
    inputs = tokenizer([text], max_length=1024, return_tensors="pt")
    input_length = inputs["input_ids"].shape[1]
    output_length = int(0.7 * input_length)
    summary_ids = model.generate(inputs["input_ids"], num_beams=4, min_length=30, max_length=output_length)
    summary = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    return summary

@app.route("/summarize", methods=["POST"])
def summarize_api():
    data = request.get_json()  # Get JSON data from request body
    text = data.get("text")  # Use .get() to avoid KeyError if "text" is not provided
    if not text:
        return jsonify({"error": "No text provided for summarization"}), 400
    summary = summarize(text)
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)  # Run the server with debug mode enabled