# pip install regex
import regex

def compile_func_pattern_excluding_strings(name_or_names):
    if isinstance(name_or_names, (list, tuple, set)):
        escaped = [regex.escape(n) for n in name_or_names]
        name_alt = "(?:" + "|".join(escaped) + ")"
    else:
        name_alt = regex.escape(name_or_names)

    # 1) 문자열 리터럴 전부 스킵
    #   - 삼중따옴표는 비탐욕적으로 전체 블록을 먹고 SKIP
    #   - 일반 따옴표는 이스케이프 허용
    skip_strings = r"""
        (?:
              """ + '"""' + r"""[\s\S]*?""" + '"""' + r"""     # triple double
            |  '''[\s\S]*?'''                                 # triple single
            |  "(?:[^"\\]|\\.)*"                              # double quoted
            |  '(?:[^'\\]|\\.)*'                              # single quoted
        )
        (*SKIP)(*F)
    """

    # 2) 함수 패턴 (재귀로 괄호 균형/중첩 처리, 문자열 내부 괄호 무시)
    func_pat = rf"""
        (?P<name>{name_alt})
        [ \t]*                    # 선택적 공백/탭
        \(                        # '('
        (?P<params>
            (?:
                [^()"'\n\r]+      # 일반 텍스트
              | " (?:[^"\\]|\\.)* "
              | ' (?:[^'\\]|\\.)* '
              | \(
                    (?&params)    # 재귀: 중첩 괄호
                \)
              | [\n\r]            # 여러 줄 허용
            )+                    # '(' 다음엔 내용이 반드시 존재(요구사항)
        )
        \)                        # 짝이 맞는 ')'
    """

    pattern = rf"""
        {skip_strings}            # 1) 문자열은 전부 건너뜀
        |                         # 2) 그 외 구간에서만 함수 패턴 탐색
        {func_pat}
    """
    return regex.compile(pattern, flags=regex.VERBOSE | regex.DOTALL)

def find_function_blocks_excluding_strings(text, name_or_names):
    pat = compile_func_pattern_excluding_strings(name_or_names)
    results = []
    for m in pat.finditer(text):
        # m가 skip 분기면 실패로 끝나므로 여기엔 함수 매치만 옴
        results.append((
            m.group(0),            # 전체 "NAME ( ... )"
            m.group("name"),
            m.group("params"),
            m.span()
        ))
    return results

# --------- 사용 예시 ---------
if __name__ == "__main__":
    sample = r'''
    "TARGET (should not, close) here)"   # 더블 쿼트 내부 -> 무시
    'TARGET (no ) match'                 # 싱글 쿼트 내부 -> 무시
    """TARGET(
        skipped, "even ) here"
    )"""                                 # 삼중 따옴표 내부 -> 무시

    TARGET   (
        a, b(c, d),
        "text ) inside",
        'another \') example',
        nested(call(1, 2, (3)))
    )

    OTHER(
        x, "y(z)", z
    )
    '''

    print("TARGET만:")
    for full, name, params, span in find_function_blocks_excluding_strings(sample, "TARGET"):
        print(span, name, "=>", full.splitlines()[0] + " ... )")

    print("\nTARGET/OTHER 동시:")
    hits = find_function_blocks_excluding_strings(sample, ["TARGET", "OTHER"])
    for full, name, params, span in hits:
        print(span, name, "OK")
