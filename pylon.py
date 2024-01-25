import sys, re

def interpretData(point):
    if point == "True": return True
    if point == "False": return False
    if point == "None": return None
    if re.match(r'^"((?:\"|[^"])*)"$', point): return re.match(r'^"((?:\"|[^"])*)"$', point).groups()[0]
    if re.match(r"^0x[0-9a-f_]+$", point.casefold()): return int(re.match(r"^0x([0-9a-f_]+)$", point.casefold()).groups()[0].replace('_', ''), 16)
    if re.match(r"^([0-9_]+(?:\.[0-9_]+)?)e([0-9_]+(?:\.[0-9_]+)?)$", point.casefold()):
        match = re.match(r"^([0-9_]+(?:\.[0-9_]+)?)e([0-9_]+(?:\.[0-9_]+)?)$", point.casefold()).groups()
        return float(match[0].replace('_', '')) * 10 ** float(match[1].replace('_', ''))
    if re.match(r"^[0-9_]+(?:\.[0-9_]+)?$", point.casefold()): return float(re.match(r"^[0-9_]+(?:\.[0-9_]+)?$", point.casefold()).group().replace('_', ''))
    if re.match(r"^0o[0-7_]+$", point.casefold()): return int(re.match(r"^0o([0-7_]+)$", point.casefold()).groups()[0].replace('_', ''), 8)
    if re.match(r"^0b[01_]+$", point.casefold()): return int(re.match(r"^0b([01_]+)$", point.casefold()).groups()[0].replace('_', ''), 2)

def detectIndent(code):
    for i in code:
        match = re.match(r"^ +|^\t+", i, re.MULTILINE)
        if match: return match.group()
    return None

def parsePylon(code):
    code = [ln for ln in code.split('\n') if re.match("^[ \t]*(#|$)", ln) is None]
    if code == []: return {}
    indent = detectIndent(code)
    queue = [{}]
    red = False
    for i in range(len(code)-1, 0, -1):
        curr = code[i]
        prev = code[i-1]
        if re.match("^" + indent + "*", curr): lineIndent = int(len(re.match("^" + indent + "*", curr).group())/len(indent))
        else: lineIndent = 0
        if re.match("^" + indent + "*", prev): prevLineIndent = int(len(re.match("^" + indent + "*", prev).group())/len(indent))
        else: prevLineIndent = 0
        if red:
            obj = re.match("^"+indent*lineIndent+r"([^#]+?)[ \t]*:(?:[ \t]*#.*)?$", curr).groups()
            red = False
        else:
            obj = re.match("^"+indent*lineIndent+r"([^#]+?)[ \t]*:[ \t]*([^ \t#][^#]*?)(?:[ \t]*#.*)?$", curr).groups()
            while len(queue) <= lineIndent: queue += [{}]
            queue[-1][obj[0]] = interpretData(obj[1])
        if lineIndent == prevLineIndent + 1:
            red = True
            qObj = re.match("^"+indent*prevLineIndent+"(?:"+indent+r")?([^#]+?)[ \t]*:(?:[ \t]*#.*)?$", prev).groups()
            queue[prevLineIndent][qObj[0]] = queue[-1]
            queue = queue[0:prevLineIndent+1]
        elif lineIndent > prevLineIndent:
            raise IndentationError("Invalid indentation step")
    if re.match(r"^([^#]+?)[ \t]*:[ \t]*([^ \t#][^#]*?)(?:[ \t]*#.*)?$", code[0]):
        fObj = re.match(r"^([^#]+?)[ \t]*:[ \t]*([^ \t#][^#]*?)(?:[ \t]*#.*)?$", code[0]).groups()
        queue[0][fObj[0]] = interpretData(fObj[1])
    if len(queue) != 1: raise SyntaxError("What?")
    return queue[0]

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as file: code = file.read()
    print(parsePylon(code))