# Ghidra Control Flow Deflattening Script with Symbol Resolution
SWITCH_TABLE_ADDR = 0x402308
CODE_SECTION_START = 0x401000
CODE_SECTION_END = 0x402000
FUNCTION_END_ADDR = 0x40195d
DISPATCHER_JMP = "JMP 0x00401958"
STATE_VAR_PATTERN = "MOV qword ptr [RBP + -0x10]"
EXIT_CASE = 5
START_CASE = 0xb

import datetime

output_lines = []

def write_output(text):
    print(text)
    output_lines.append(text)

def resolve_address(addr_value):
    """Resolve address to function name, string, or symbol"""
    try:
        addr = toAddr(addr_value)

        func = getFunctionAt(addr)
        if func is not None:
            return func.getName()

        symbol = getSymbolAt(addr)
        if symbol is not None:
            return symbol.getName()

        data = getDataAt(addr)
        if data is not None and data.hasStringValue():
            string_val = str(data.getValue())
            return '"{}"'.format(string_val[:27] + "..." if len(string_val) > 30 else string_val)

        string_data = getString(addr)
        if string_data is not None:
            string_str = str(string_data)
            return '"{}"'.format(string_str[:27] + "..." if len(string_str) > 30 else string_str)

        return None
    except:
        return None

def enhance_instruction(inst):
    """Enhance instruction with resolved symbols"""
    inst_str = str(inst)

    for i in range(inst.getNumOperands()):
        try:
            operand = inst.getOpObjects(i)[0]
            if hasattr(operand, 'getOffset'):
                addr_val = operand.getOffset()
                resolved = resolve_address(addr_val)
                if resolved is not None:
                    hex_addr = "0x{:x}".format(addr_val)
                    if hex_addr in inst_str:
                        inst_str = inst_str.replace(hex_addr, "{} ; {}".format(hex_addr, resolved))
        except:
            continue

    return inst_str

# Header
write_output("; Control Flow Deobfuscation Analysis")
write_output("; Date: {} | Binary: a.out".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
write_output(";" + "=" * 70)

# Extract case addresses
case_addresses = []
current_addr = toAddr(SWITCH_TABLE_ADDR)

while True:
    addr_bytes = getBytes(current_addr, 8)
    addr_value = sum((addr_bytes[i] & 0xFF) << (i * 8) for i in range(8))

    case_addr = toAddr(addr_value)
    if case_addr.getOffset() < CODE_SECTION_START or case_addr.getOffset() > CODE_SECTION_END:
        break

    case_addresses.append(case_addr)
    current_addr = current_addr.add(8)

sorted_addresses = sorted(set([addr.getOffset() for addr in case_addresses]))

def process_case(case_num, indent_level=0, from_case=None):
    case_addr = case_addresses[case_num]
    case_start = case_addr.getOffset()
    indent = "  " * indent_level

    if from_case is not None:
        write_output("{}        v".format(indent))

    write_output("{}    +==== CASE {} (0x{:x}) ====+".format(indent, case_num, case_start))

    case_end = FUNCTION_END_ADDR
    for addr_val in sorted_addresses:
        if addr_val > case_start:
            case_end = addr_val
            break

    current_addr = case_addr
    next_cases = []
    has_conditional = False

    while current_addr.getOffset() < case_end:
        inst = getInstructionAt(current_addr)
        if inst is None:
            break

        if DISPATCHER_JMP in str(inst):
            current_addr = inst.getMaxAddress().add(1)
            continue

        inst_str = enhance_instruction(inst)
        addr_hex = "0x{:x}".format(current_addr.getOffset())
        flow_indicator = ""

        if inst.getMnemonicString() in ["JG", "JL", "JE", "JNE", "JA", "JB", "JGE", "JLE"]:
            has_conditional = True
            flow_indicator = " [BRANCH]"
        elif inst.getMnemonicString() == "CALL":
            try:
                target = inst.getOpObjects(0)[0]
                if hasattr(target, 'getOffset'):
                    func_name = resolve_address(target.getOffset())
                    flow_indicator = " --> {}".format(func_name if func_name else "CALL")
            except:
                flow_indicator = " --> CALL"
        elif inst.getMnemonicString() == "JMP" and "0x0040195d" in str(inst):
            flow_indicator = " --> EXIT"

        if STATE_VAR_PATTERN in str(inst):
            parts = str(inst).split(',')
            if len(parts) > 1:
                next_case = int(parts[1].strip(), 0)
                next_cases.append(next_case)
                flow_indicator = " =====> CASE {}".format(next_case)

        write_output("{}    | {:>10} | {:<60}{}".format(indent, addr_hex, inst_str, flow_indicator))
        current_addr = inst.getMaxAddress().add(1)

    write_output("{}    +{}+".format(indent, "=" * 70))

    if len(next_cases) > 1 and has_conditional:
        write_output("{}        +======> FALSE =====> CASE {}".format(indent, next_cases[0]))
        write_output("{}        +======> TRUE  =====> CASE {}".format(indent, next_cases[1]))
    elif next_cases:
        write_output("{}        v".format(indent))

    return next_cases

visited_cases = set()
case_queue = [(START_CASE, 0, None)]

write_output("\n  ENTRY POINT\n      v")

while case_queue:
    current_case, indent_level, from_case = case_queue.pop(0)

    if current_case == EXIT_CASE:
        indent_str = "  " * indent_level
        write_output("{}    +==== EXIT CASE {} ====+".format(indent_str, EXIT_CASE))
        case_addr = case_addresses[EXIT_CASE]
        current_addr = case_addr

        for i in range(2):
            inst = getInstructionAt(current_addr)
            if inst is None:
                break
            addr_hex = "0x{:x}".format(current_addr.getOffset())
            enhanced_inst = enhance_instruction(inst)
            flow_indicator = " --> EXIT" if inst.getMnemonicString() == "JMP" else ""
            write_output("{}    | {:>10} | {:<60}{}".format(indent_str, addr_hex, enhanced_inst, flow_indicator))
            current_addr = inst.getMaxAddress().add(1)

        write_output("{}    +{}+".format(indent_str, "=" * 70))
        continue

    visited_cases.add(current_case)
    next_cases = process_case(current_case, indent_level, from_case)

    for next_case in next_cases:
        if next_case is not None:
            if next_case in visited_cases:
                # This is a true loop - show it inline
                indent_str = "  " * indent_level
                write_output("{}        v".format(indent_str))
                write_output("{}     CASE {} (LOOP BACK)".format(indent_str, next_case))
            else:
                new_indent = indent_level + (1 if len(next_cases) > 1 else 0)
                case_queue.append((next_case, new_indent, current_case))

# Save file
output_file = "control_flow_analysis.txt"
try:
    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines))
    print("File saved: {}".format(output_file))
except:
    print("Failed to save file")
