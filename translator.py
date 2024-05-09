import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

class Translator:
    def __init__(self, api_key, translate_to_lang):
        self.llm = ChatOpenAI(openai_api_key=api_key, model_name="gpt-3.5-turbo")
        self.translate_to_lang = translate_to_lang
        self.language_map = self.load_language_map()
        self.prompt_template = PromptTemplate(
            input_variables=["text", "language_name"],
            template="翻訳文に余計な装飾はしない、改行を含まず１行で表示する、というルールに従って次の文章を{language_name}に翻訳して下さい:\n\n{text}"
        )

    def load_language_map(self):
        try:
            with open('conf/language_code.json', 'r', encoding='utf-8') as f:
                language_map = json.load(f)
            return language_map
        except Exception as e:
            print(f"Error loading language map: {str(e)}")
            return {}

    def get_language_name(self, lang_code):
        return self.language_map.get(lang_code, 'none')

    def translation(self, text):
        if text == "":
            return ""

        try:
            language_name = self.get_language_name(self.translate_to_lang)
            if language_name == 'none':
                raise ValueError(f"Unsupported language code: {self.translate_to_lang}")

            prompt = self.prompt_template.format(text=text, language_name=language_name)
            response = self.llm.invoke(prompt)
            print(response.content)
            return response.content
        except Exception as e:
            print(f"Error: {str(e)}")
            return ""