from django.conf import settings 
import openai

with open(f"{settings.BASE_DIR}/ai/genTextBase.txt", 'r', encoding='utf-8') as file:
    base_text = ''.join(file.readlines())

    api_key = settings.OPENAI_API_KEY
    openai.api_key=api_key
    
def get_prompt(content):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{base_text} {content.strip()}"},]
    )
    generated_text = completion["choices"][0]["message"]["content"]
    output_text=generated_text.split('\n')
    prompts = [v for v in output_text if v]
    return prompts


# model_path='Eunju2834/LoRA_oilcanvas_style' #FineTuning Model Path
# pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")#, torch_dtype=torch.float16
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# pipe.unet.load_attn_procs(model_path)
# pipe.to(device)
# print(device)

# neg_prompt='''FastNegativeV2,(bad-artist:1.0), (loli:1.2),
#     (worst quality, low quality:1.4), (bad_prompt_version2:0.8),
#     bad-hands-5,lowres, bad anatomy, bad hands, ((text)), (watermark),
#     error, missing fingers, extra digit, fewer digits, cropped,
#     worst quality, low quality, normal quality, ((username)), blurry,
#     (extra limbs), bad-artist-anime, badhandv4, EasyNegative,
#     ng_deepnegative_v1_75t, verybadimagenegative_v1.3, BadDream,
#     (three hands:1.1),(three legs:1.1),(more than two hands:1.4),
#     (more than two legs,:1.2),badhandv4,EasyNegative,ng_deepnegative_v1_75t,verybadimagenegative_v1.3,(worst quality, low quality:1.4),text,words,logo,watermark,
#     '''


# def get_image(prompt):
#     image = pipe(prompt, negative_prompt=neg_prompt,num_inference_steps=30, guidance_scale=7.5).images[0]
#     return image


# prompt = '''(masterpiece, best quality, ultra detailed), Oil Painting, Impressionism, oil painting with brush strokes, bichu,
# Park stroll, joyful atmosphere, laughter-filled time, playful dogs, vibrant park scene,
# cheerful interactions, happy pet owners, heartwarming moments, vibrant community vibes'''

# result = get_image(prompt)