import sys

# brainfuck to coin compiler
# by las-r

# jump helper
def jmp(target):
    if target <= 255:
        return [0x80, target]
    if target <= 510:
        return [0x83, target - 255]
    print("error: program too large, jump target beyond 510")
    sys.exit(1)

# open file
if len(sys.argv) < 2:
    print("usage: python coin_bf.py <file.bf>")
    sys.exit(1)
fname = sys.argv[1]
with open(fname) as f:
    code = f.read()
    
# set up compiler values
i = 0
data = bytearray([0x01, 0x01, 0x03, 0xff, 0x05, 0x04])
stack = []

# compile
while i < len(code):
    char = code[i]
    match char:
        case ">": data.extend([0x66, 0x61, 0xb0, 0x00, 0x65, 0x51, 0xc0, 0x56])
        case "<": data.extend([0x75, 0x51, 0x76, 0x61, 0xb0, 0x00, 0x65, 0x51, 0xc0, 0x56])
        case "+": data.extend([0xef, 0x00, 0x6f, 0xf1, 0xdf, 0x00])
        case "-": data.extend([0xef, 0x00, 0x7f, 0xf1, 0xdf, 0x00])
        case ".": data.extend([0x90, 0x00])
        case "[":
            start = len(data)
            data.extend([0xef, 0x00, 0xaf, 0x00])
            data.extend(jmp(start + 8))
            data.extend([0x00, 0x00])
            stack.append(start)
        case "]":
            if not stack:
                print("error: unmatched ]")
                sys.exit(1)
            start = stack.pop()
            data.extend([0xef, 0x00, 0xaf, 0x00])
            data.extend(jmp(start + 8))
            data[start + 6:start + 8] = bytes(jmp(len(data)))
    i += 1

# finish up
if stack:
    print("error: unmatched [")
    sys.exit(1)
data.extend([0xf0, 0x00])
if len(data) > 0x400:
    print("error: program overlaps the tape at 0x400")
    sys.exit(1)
    
# write
cfname = fname.split(".")[0] + ".bin"
with open(cfname, "wb") as cf:
    cf.write(data)