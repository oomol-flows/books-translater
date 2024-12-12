import base64

from oocana import Context
from shared.epub import EpubHandler, CountUnit
from shared.transalter import AITranslator
from .file import translate_epub_file

def main(inputs: dict, context: Context):
  ai = inputs["ai"]
  model: str
  api_url: str

  if ai == "DeepSeek":
    model = "deepseek-chat"
    api_url = "https://api.deepseek.com/chat/completions"
  elif ai == "ChatGPT":
    model = "gpt-3.5-turbo"
    api_url = "https://aigptx.top/v1/chat/completions"
  else:
    raise Exception(f"unknown AI: {ai}")

  translater = AITranslator(
    model=model,
    api_url=api_url,
    auth_token=inputs["ai_token"],
    source_lan=_convert_to_lan_description(inputs["source"]),
    target_lan=_convert_to_lan_description(inputs["target"]),
  )
  max_translating_group_unit: CountUnit
  group_unit: str = inputs["max_translating_group_unit"]

  if group_unit == "char":
    max_translating_group_unit = CountUnit.Char
  elif group_unit == "token":
    max_translating_group_unit = CountUnit.Token
  else:
    raise Exception(f"unknown max_translating_group_unit: {group_unit}")

  epub_handler = EpubHandler(
    translate=translater.translate,
    max_paragraph_chars=inputs["max_paragraph_chars"],
    max_translating_group=inputs["max_translating_group"],
    max_translating_group_unit=max_translating_group_unit,
  )
  zip_data = translate_epub_file(
    context=context,
    handler=epub_handler,
    file_path=inputs["file"],
    book_title=inputs.get("title", None),
  )
  base64_str = base64.b64encode(zip_data).decode("utf-8")

  return { "bin": base64_str }

def _convert_to_lan_description(lan_key: str) -> str:
  if lan_key == "English":
    return "English"
  elif lan_key == "中文":
    return "Chinese"
  else:
    raise Exception(f"unknown lan: {lan_key}")