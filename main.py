from pprint import pprint
from transformers import pipeline
from pydantic import BaseModel, ConfigDict, SerializeAsAny
from typing import Any, Callable


import datetime

class Runnable(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def invoke(self, data: Any) -> Any:
        raise NotImplementedError("I am not implemented!")
    
    def __or__(self, other:Any)->Any:
        if isinstance(other, Runnable):
            return RunnableSequence(first=self,second=other)
        if callable(other):
            return RunnableSequence(first=self, second=RunnableLambda(func=other))
        return NotImplemented
    
    def __ror__(self, other: Any) -> Any:
        if callable(other):
            return RunnableSequence(
                first=RunnableLambda(func=other),
                second=self
                )

class RunnableLambda(Runnable):
    func: Callable[[Any], Any]
    
    def invoke(self, data:Any) -> Callable:
        return self.func(data)
    
class RunnableSequence(Runnable):
    first: Runnable
    second: Runnable
    def invoke(self, data: Any) -> Any:
        return self.second.invoke(data)

class ProcessTicket(BaseModel):
    customer_id: int
    sentiment: int
    urgency: int
    summary: str

class TicketParser(Runnable):
    name: str = "ticket_parser"
    
    def invoke(self, raw_dict: dict) -> ProcessedTicket:
        return ProcessTicket(**raw_dict)
    
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