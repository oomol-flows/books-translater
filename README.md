# books translater

Translate the epub book using LLM. The translated book will retain the original text and list the translated text side by side with the original text.

## Field Description

- `file`: the epub file to be translated.
- `title`: the title of the book to be translated (original language)
- `max_translating_group`: the maximum amount of translation text submitted each time. Books will be submitted in chunks during translation, and this value will limit the maximum length of each chunk.
- `max_translating_group_unit`: the unit of the `max_translating_group_unit`.
- `source`: the language of the book to be translated.
- `target`: the target language you want to translate it into.
- `llm_api`: the LLM API format used for translation.
- `model`: the model used for translation
- `url`: the URL of the LLM
- `api_key`: the Key of the LLM
- `temperature`: the temperature of the LLM, which is a parameter used to control the randomness of the generated text. In simple terms, the lower the temperature value, the more certain and conservative the text generated by the model. The higher the temperature value, the more random and diverse the text generated by the model.
- `timeout`: the request timeout, in seconds.
- `binary`: the translated target epub file content.