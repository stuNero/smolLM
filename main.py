from pprint import pprint
from transformers import pipeline
import datetime

class SmolLM:
    def __init__(self, model_name="HuggingFaceTB/SmolLM-135M-Instruct"):
        print("Loading {model_name} into memory (this may take a while)...")
        self.pipe = pipeline("text-generation", model_name)
        print("Model Loaded Successfully!")
        
    def invoke(self, prompt:str):
        prompt += "\nKeep it concise!"
        
        messages = [
            { "role":"system", "content": "You're a tech priest from the adeptus mechanicus in the warhammer 40k universe that will be my AI tutor"},
            {"role": "user", "content": prompt}]
        
        output = self.pipe(messages, max_new_tokens=300)
        
        with open("responses.txt", "a") as f:
            f.write("OUTPUT AT " + datetime.datetime.now().__str__()[:19] + "\nWith prompt: " + prompt + "\n______________________________\n")
            f.write(output[0]['generated_text'][-1]['content'])
            f.write("\n__________________________\n")
        return output[0]['generated_text'][-1]['content']

class PromptTemplate:
    def __init__(self, template_str:str):
        self.template_str = template_str
        
    def format(self, **kwargs):
        return self.template_str.format(**kwargs)
        
    def __or__(self, other):
        if isinstance(other, SmolLM):
            return LLMChain(
                prompt_template=self.template_str,
                llm=other
            )
        raise TypeError("It's not an instance of SmolLM")
        
class LLMChain:
    def __init__(self, 
                 prompt_template: PromptTemplate, 
                 llm: SmolLM):
        self.prompt_template = prompt_template
        self.llm = llm
    def invoke(self, **kwargs):
        formatted_prompt = self.prompt_template.format(**kwargs)
        return self.llm.invoke(formatted_prompt)

llm = SmolLM()
recipe_prompt = PromptTemplate(
    template_str="Give me a quick 2-step recipe for a {dish} using only {ingredient_count} ingredients"
)

recipe_chain = recipe_prompt | llm

result = recipe_chain.invoke(dish="omelette", ingredient_count="three")

pprint(result)