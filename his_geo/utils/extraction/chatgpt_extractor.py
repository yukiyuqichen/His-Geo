from openai import OpenAI


def extract_data(model_version, api_key, prompt, text):
    client = OpenAI(
        api_key = api_key
    )
    response = client.chat.completions.create(
    model = model_version,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt + text}
    ],
    temperature=0,
    )
    result = response.choices[0].message.content
    result = result.replace('"', '').replace(' ', '')
    
    return result