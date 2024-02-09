
from openai import OpenAI
client = OpenAI()

def extract_ocr(user_prompt, urls):
    """
    Extracts text from a series of images using OpenAI's GPT-4 Vision API.

    This function sends a request to OpenAI's GPT-4 Vision API to perform Optical Character Recognition (OCR) on 
    images provided via URLs. It constructs a message payload containing the user's text prompt and the image URLs. 
    The function then sends this payload to the GPT-4 Vision API model and retrieves the extracted text from the 
    response. It's designed to handle multiple images and extract text from each of them.

    The function relies on the OpenAI client initialized at the beginning of the script for API interaction.

    Args:
        user_prompt (str): The text prompt to be sent to the API along with the image URLs. This prompt can provide 
                           context or instructions for the text extraction.
        urls (list[str]): A list of URLs pointing to the images from which text is to be extracted.

    Returns:
        str: The extracted text from the images as returned by the OpenAI GPT-4 Vision API.
    """
    
    image_url_messages = [
        {
            "type": "image_url",
            "image_url": {
                "url": url,
            },
        }
        for url in urls
    ]

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt,
                    }
                ] + image_url_messages
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content

