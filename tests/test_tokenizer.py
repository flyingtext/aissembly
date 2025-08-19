from aissembly_dsl.tokenizer import tokenize


def test_indent_and_dedent():
    src = 'if x:\n    let y = 1\n'
    kinds = [t.kind for t in tokenize(src)]
    assert 'INDENT' in kinds
    assert 'DEDENT' in kinds


def test_string_and_comment():
    src = "let s = 'hi' # comment"
    tokens = tokenize(src)
    string_tokens = [t for t in tokens if t.kind == 'STRING']
    assert string_tokens and string_tokens[0].value == "'hi'"
