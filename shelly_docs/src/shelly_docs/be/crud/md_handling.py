
from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer
from mistletoe.block_token import BlockToken, Paragraph, SetextHeading, Heading, CodeFence
from mistletoe.span_token import SpanToken, RawText, InlineCode
from mistletoe.token import Token
from mistletoe.markdown_renderer import MarkdownRenderer

def update_text(token: SpanToken, new_text: str):
    """Update the text contents of a span token and its children.
    `InlineCode` tokens are left unchanged."""
    if isinstance(token, RawText):
        token.content = new_text

def update_block(token: BlockToken, new_text: str):
    """Update the text contents of paragraphs and headings within this block,
    and recursively within its children."""
    if isinstance(token, (Paragraph, SetextHeading, Heading, CodeFence)):
        for child in token.children:
            update_text(child, new_text)

    for child in token.children:
        if isinstance(child, BlockToken):
            update_block(child, new_text)