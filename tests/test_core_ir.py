from aissembly_dsl.core_ir import cond, loop_for, loop_while, ctrl


def test_cond_laziness():
    executed = []

    def then():
        executed.append('then')
        return 1

    def els():
        executed.append('else')
        return 2

    result = cond(lambda: True, then, els)
    assert result == 1
    assert executed == ['then']


def test_loop_for_sum():
    total = loop_for(range(1, 6), lambda i, acc: acc + i, 0)
    assert total == 15


def test_loop_while_limit():
    def test():
        return True

    def body(acc):
        return acc + 1

    try:
        loop_while(test, body, 0, max_iter=5)
    except Exception as e:
        assert e.kind == 'LimitExceeded'
