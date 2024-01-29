import sys, re, ast

def interpretData(point):
    if point == "True": return True
    if point == "False": return False
    if point == "None": return None
    if re.match(r'^"(?:\"|[^"])*"$', point): return point[1:-1]
    if re.match(r"^'(?:\'|[^'])*'$", point): return point[1:-1]
    if re.match(r"^0x[\da-f_]+$", point.casefold()):
        return int(re.match(r"^0x([\da-f_]+)$", point.casefold()).groups()[0].replace('_', ''), 16)
    if re.match(r"^[\d_]+(?:\.[\d_]+)?e[\d_]+$", point.casefold()):
        match = re.match(r"^([\d_]+(?:\.[\d_]+)?)e([\d_]+)$", point.casefold()).groups()
        return float(match[0].replace('_', '')) * 10 ** float(match[1].replace('_', ''))
    if re.match(r"^e*[\d_]+(?:\.[\d_]+)?(e([\d_]+))?$", point.casefold()):
        match = re.match(r"^(e*)([\d_]+(?:\.[\d_]+)?)(?:e([\d_]+))?$", point.casefold())
        out = float(match.groups()[1])
        if match.groups()[2]: out *= 10 ** float(match.groups()[2])
        for i in range(len(match.groups()[0])): out = 10 ** out
        return out
    if re.match(r"^0o[0-7_]+$", point.casefold()):
        return int(re.match(r"^0o([0-7_]+)$", point.casefold()).groups()[0].replace('_', ''), 8)
    if re.match(r"^0b[01_]+$", point.casefold()):
        return int(re.match(r"^0b([01_]+)$", point.casefold()).groups()[0].replace('_', ''), 2)
    raise ValueError("Invalid data point")

def intSafe(string):
    try: return int(string)
    except ValueError:
        if re.match(r'^"(?:\"|[^"])*"$', string):
            return string[1:-1]
        if re.match(r"^'(?:\'|[^'])*'$", string):
            return string[1:-1]
        return string

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
        if re.match("^" + indent + "*", curr):
            lineIndent = int(len(re.match("^" + indent + "*", curr).group())/len(indent))
        else: lineIndent = 0
        if re.match("^" + indent + "*", prev):
            prevLineIndent = int(len(re.match("^" + indent + "*", prev).group())/len(indent))
        else: prevLineIndent = 0
        if red:
            obj = re.match("^"+indent*lineIndent+r"([^#]+?)[ \t]*:(?:[ \t]*#.*)?$", curr).groups()
            red = False
        else:
            obj = re.match("^"+indent*lineIndent+r"([^#]+?)[ \t]*:[ \t]*([^ \t#][^#]*?)(?:[ \t]*#.*)?$", curr).groups()
            while len(queue) <= lineIndent: queue += [{}]
            queue[-1][intSafe(obj[0])] = interpretData(obj[1])
        if lineIndent == prevLineIndent + 1:
            red = True
            qObj = re.match("^"+indent*prevLineIndent+"(?:"+indent+r")?([^#]+?)[ \t]*:(?:[ \t]*#.*)?$", prev).groups()
            queue[prevLineIndent][intSafe(qObj[0])] = queue[-1]
            queue = queue[0:prevLineIndent+1]
        elif lineIndent > prevLineIndent:
            raise IndentationError("Invalid indentation step")
    if re.match(r"^([^#]+?)[ \t]*:[ \t]*([^ \t#][^#]*?)(?:[ \t]*#.*)?$", code[0]):
        fObj = re.match(r"^([^#]+?)[ \t]*:[ \t]*([^ \t#][^#]*?)(?:[ \t]*#.*)?$", code[0]).groups()
        queue[0][intSafe(fObj[0])] = interpretData(fObj[1])
    if len(queue) != 1: raise SyntaxError("What?")
    return queue[0]

def buildpylon(obj, *, ind="\t"):
    return obj

if __name__ == '__main__':
    if sys.argv[1] == '-i':
        with open(sys.argv[2]) as file:
            print(parsePylon(file.read()))
    elif sys.argv[1] == '-c':
        built = buildpylon(ast.literal_eval(sys.argv[3]))
        # with open(sys.argv[2], 'w') as file:
            # file.write(built)
        print(built)
