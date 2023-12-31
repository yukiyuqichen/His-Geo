import json
from retrying import retry
from .utils.extraction.chatgpt_extractor import extract_data as chatgpt_extract_data


def print_retry_details(exception):
    print(f"Error happened: {exception}")
    print("Retrying...")
    return True

class Extractor:
    def __init__(self, prompt, output_dir, output_name="extracted_results", model="chatgpt", model_version="gpt-3.5-turbo", api_key=""):
        self.prompt = prompt
        self.output_dir = output_dir
        self.output_name = output_name
        self.model = model
        self.model_version = model_version
        self.api_key = api_key

    @retry(retry_on_exception=print_retry_details)
    def extract_one_text(self, text):
        if self.model == "chatgpt":
            result = chatgpt_extract_data(self.model_version, self.api_key, self.prompt, text)
            return result

    def extract_texts(self, texts, encoding="utf-8-sig"):
        output_path = self.output_dir + self.output_name + "_" + self.model + "_" + self.model_version + ".json"
        results = {}
        for i, text in enumerate(texts):
            results[i] = self.extract_one_text(text)
            print("Extracting text " + str(i) + " to " + output_path)
            with open(output_path, "w", encoding=encoding) as f:
                json.dump(results, f, ensure_ascii=False)
        return results


