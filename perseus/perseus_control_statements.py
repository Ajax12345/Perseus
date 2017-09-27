import re
import collections
class InvalidControlStatementHeader(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
class UnbalancedStringToken(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class VariableNotDeclared(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class If_Statement:
    __slots__ = ["contents", "operators", "data_tree", "line_number"]
    def __init__(self, contents):
        self.contents = contents[0][len("if "):] #will have to change to perticular conditinal expression
        #TODO: parse if statement header only, then find lines of code
        #TODO: implement parsing and running of block statements
        #TODO: implement elif and else statements
        #IDEA: I think that for "for" loops, a separate runtime environment needs to be created
        """
        control tokens: |, <, >, /, \
        """
        """
        boolean control: and:&, or:U
        """
        self.operators = {">":lambda x, y:x > y, "<":lambda x, y:x < y, "|":lambda x, y:x == y, "/":lambda x, y:x >= y, "\\":lambda x, y:x <= y, None:lambda x: x}

        self.data_tree = {"Integer":{"val":456, "asd4s":600, "val3":100, "v":100}, "Boolean":{"val8":True, "val9":True}, "Double":{}, "String":{}}
        self.line_number = 1
        #IDEA: have a "decrement" command and "increment" command

    def get_code_sections(self):
        code_blocks = re.findall("\[(.*?)\]", self.contents)

        return [b for b in [i+";" for i in re.split(';\s*', code_blocks[0])] if b != ";"]

    def split_at_conditionals(self):
        return re.split("&|U", self.contents[:self.contents.index("[")]), "&" in self.contents[:self.contents.index("[")], "U" in self.contents[:self.contents.index("[")]
    def caste_to_types(self, l):
        if not l.startswith('"') and l.endswith('"') or l.startswith('"') and not l.endswith('"'):
            raise UnbalancedStringToken("Line {}:string variable must contain quotes on each end".format(self.line_number))
        elif l.startswith('"') and l.endswith('"'):
            return l[1:-1]

        elif re.search('^\d+\.\d+$', l) is not None:
            return float(l)

        elif re.search('^\d+$', l) is not None:
            return int(l)



        else:
            if l.startswith("!"):
                if l[1:] not in self.data_tree["Boolean"]:
                    raise VariableNotDeclared("Line {}: variable '{}' not declared".format(self.line_number, l))
                return not self.data_tree["Boolean"][l[1:]]

            types = [i for i in ["Double", "Integer", "String", "Boolean"] if l in self.data_tree[i]]
            if not types:
                raise VariableNotDeclared("Line {}: variable '{}' not declared".format(self.line_number, l))
            return self.data_tree[types[0]][l]
    def analyze_conditions(self):
        parts, and1, or1 = self.split_at_conditionals()
        #print [self.parse_if_statement(i+";", False, '', '') for i in parts]
        #print "new_variables", new_variables
        #new_variables = [(self.caste_to_types(a), self.caste_to_types(b), c) for a, b, c in [self.parse_if_statement(i+";", False, '', '') for i in parts]]
        #print "new_variables", new_variables
        new_variables = [(self.caste_to_types(a), self.caste_to_types(b), operator_type) if operator_type is not None else (self.caste_to_types([c for c in [a, b] if c][0]), None) for a, b, operator_type in [self.parse_if_statement(i+";", False, '', '') for i in parts]]

        print new_variables
        truth_values = [self.operators[i[-1]](*i[:-1]) for i in new_variables]
        if len(truth_values) == 1:
            return truth_values[0], self.get_code_sections()

        elif len(truth_values) == 2:
            if '&' in self.contents[:self.contents.index("[")]:
                return truth_values[0] and truth_values[1], self.get_code_sections()
            elif 'U' in self.contents[:self.contents.index("[")]:
                return truth_values[0] or truth_values[1], self.get_code_sections()
            else:
                raise InvalidControlStatementHeader("Line {}: requires one or two control statements, but {} found".format(self.line_number, len(truth_values)))

    def parse_if_statement(self, line, seen_control, val1, val2, operator_type=None):

        if line[0] == ";":


            return [val1, val2, operator_type]



        else:
            if not seen_control:
                if line[0] not in ['|', "\\", '/', '<', '>']: #NOTE: escaping backslash works fine
                    if line[1] == ":":
                        raise InvalidControlStatementHeader("must have valid control key")
                    if line[0] == " ":
                        return self.parse_if_statement(line[1:], False, val1, val2)
                    else:
                        val1 += line[0]

                        return self.parse_if_statement(line[1:], False, val1, val2)
                else:
                    if not line[1].isdigit() and not line[1].isalpha() and line[1] != " ":
                        raise InvalidControlStatementHeader("must have complete control statement")
                    return self.parse_if_statement(line[1:], True, val1, val2, line[0])
            else:
                if line[0] == " ":
                    return self.parse_if_statement(line[1:], True, val1, val2, operator_type)
                else:
                    val2 += line[0]
                    return self.parse_if_statement(line[1:], True, val1, val2, operator_type)

s = If_Statement([i.strip('\n') for i in open('sample_file.txt')])
boolean, code = s.analyze_conditions()
print (boolean, code)
