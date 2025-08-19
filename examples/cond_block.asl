let x = add(7, 6)
let tag = cond(test=ge(x, 10)):
    then:
        -> "ok"
    else:
        -> "ng"
