import io
import os
import zipfile
import tempfile
import shutil

from typing import Optional
from lxml.etree import parse
from oocana import Context
from shared.epub import translate_html, Translate, EpubContent


def translate_epub_file(
    context: Context,
    translate: Translate,
    file_path: str,
    book_title: Optional[str]) -> bytes:

  unzip_path = tempfile.mkdtemp()
  try:
    with zipfile.ZipFile(file_path, "r") as zip_ref:
      for member in zip_ref.namelist():
        target_path = os.path.join(unzip_path, member)
        if member.endswith("/"):
          os.makedirs(target_path, exist_ok=True)
        else:
          target_dir_path = os.path.dirname(target_path)
          os.makedirs(target_dir_path, exist_ok=True)
          with zip_ref.open(member) as source, open(target_path, "wb") as file:
            file.write(source.read())

    _translate_folder(
      context=context,
      translate=translate,
      path=unzip_path,
      book_title=book_title,
    )
    in_memory_zip = io.BytesIO()

    with zipfile.ZipFile(in_memory_zip, "w") as zip_file:
      for root, _, files in os.walk(unzip_path):
        for file in files:
          file_path = os.path.join(root, file)
          relative_path = os.path.relpath(file_path, unzip_path)
          zip_file.write(file_path, arcname=relative_path)

    in_memory_zip.seek(0)
    zip_data = in_memory_zip.read()

    return zip_data

  finally:
    shutil.rmtree(unzip_path)

def _translate_folder(
  context: Context,
  translate: Translate,
  path: str,
  book_title: Optional[str],
):
  epub_content = EpubContent(path)

  if book_title is None:
    book_title = epub_content.title
    if not book_title is None:
      book_title = _link_translated(book_title, translate([book_title], lambda _: None)[0])

  if not book_title is None:
    epub_content.title = book_title

  authors = epub_content.authors
  to_authors = translate(authors, lambda _: None)

  for i, author in enumerate(authors):
    authors[i] = _link_translated(author, to_authors[i])

  epub_content.authors = authors
  epub_content.save()

  _transalte_ncx(epub_content, translate)
  _translate_spines(context, epub_content, translate)

def _transalte_ncx(epub_content: EpubContent, translate: Translate):
  ncx_path = epub_content.ncx_path

  if ncx_path is not None:
    tree = parse(ncx_path)
    root = tree.getroot()
    namespaces={ "ns": root.nsmap.get(None) }
    text_doms = []
    text_list = []

    for text_dom in root.xpath("//ns:text", namespaces=namespaces):
      text_doms.append(text_dom)
      text_list.append(text_dom.text)

    for index, text in enumerate(translate(text_list, lambda _: None)):
      text_dom = text_doms[index]
      text_dom.text = _link_translated(text_dom.text, text)

    tree.write(ncx_path, pretty_print=True)

def _translate_spines(context: Context, epub_content: EpubContent, translate: Translate):
  spines = epub_content.spines
  for index, spine in enumerate(spines):
    if spine.media_type == "application/xhtml+xml":
      file_path = spine.path
      with open(file_path, "r", encoding="utf-8") as file:
        content = translate_html(
          translate=translate,
          file_content=file.read(),
          report_progress=lambda p, i=index: context.report_progress(
            progress=100.0 * (float(i) + p) / float(len(spines)),
          ),
        )
      with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    context.report_progress(
      progress=100.0 * float(index + 1) / float(len(spines)),
    )

def _link_translated(origin: str, target: str) -> str:
  if origin == target:
    return origin
  else:
    return f"{origin} - {target}"