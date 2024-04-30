from django.conf import settings 
import openai

with open(f"{settings.BASE_DIR}/ai/genTextBase.txt", 'r', encoding='utf-8') as file:
    base_text = ''.join(file.readlines())

    api_key = settings.OPENAI_API_KEY
    openai.api_key=api_key
    
def get_prompt(content):
    """
    일기 내용을 입력받아 프롬프트 생성
    """
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{base_text} {content.strip()}"},]
    )
    generated_text = completion["choices"][0]["message"]["content"]
    output_text=generated_text.split('\n')
    prompts = [v for v in output_text if v]
    prompts = "(masterpiece,detailed), (Oil Painting:1.3), (Impressionism:1.3) ,(oil painting with brush strokes:1.2), (looking away:1.1)"+ ", ".join(prompts)
    return prompts