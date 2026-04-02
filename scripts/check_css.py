import re
html = open('docs/api-reference-redoc.html','r',encoding='utf-8').read()
m = re.search(r"var mqttCssText = \[(.*?)\]\.join", html, re.DOTALL)
if m:
    block = m.group(1)
    items = re.findall(r"'([^']*?)'", block)
    print('CSS rules count:', len(items))
    for i, rule in enumerate(items):
        ob = rule.count('{')
        cb = rule.count('}')
        if ob != cb:
            print('UNBALANCED rule %d: o=%d c=%d => %s' % (i, ob, cb, rule[:80]))
    print('CSS check done')
else:
    print('not found')
