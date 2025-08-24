from diffusers import StableDiffusionPipeline
import torch

model_id = "path/to/your/model"  # or huggingface model repo id
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

prompt = "pixel art dungeon corridor, 16-bit style"
image = pipe(prompt, height=512, width=512).images[0]

image.save("dungeon_corridor.png")
