#extension of perseus language
from collections import defaultdict
import re
class SyntaxError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class InvalidSyntaxError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
class InvalidDeclaration(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class VariableNotDeclared(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class InvalidOperation(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class InvalidLineTermination(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class UnassignableTypes(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class InvalidOutputStatement(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class IndexOutOfBoundsError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

errors = []

class ListData:
    #TODO: modify assignment statements to be able to store function returns, list indices, etc.
    __slots__ = ["line", "final_list", "seen_assignment", "forbidden", "line_number", "seen_first_bracket", "variable_name", "current_variable", "index", "seen_last_bracket"]
    def __init__(self, line, line_number, **args):
        self.line = line
        self.final_list = []
        self.seen_assignment = False
        self.line_number = line_number
        self.seen_first_bracket = False
        self.forbidden = ["+", "-", "/", "*", "%"]
        self.variable_name = ''
        self.flag = args.get("flag", False)
        self.current_variable = ''
        self.new_final_line = []
        if args.get("flag", False):
            self.new_final_line = self.initialize_list(self.line)

        self.index = ''
        self.seen_last_bracket = False
        if args.get("flag", False):
            print "new_final_line", self.new_final_line


    def initialize_list(self, line):
        print "line", line
        if line[0] == ";":
            return self.final_list

        else:
            if not self.seen_assignment:
                if line[0] == " ":
                    if line[1].isdigit() or line[1].isalpha():
                        raise InvalidSyntaxError("Line {}: cannot have spaces in variable assignment".format(self.line_number))

                    else:
                        return self.initialize_list(line[1:])

                elif line[0] in self.forbidden:
                    raise InvalidSyntaxError("Line {}: forbidden character '{}' in List object assignment".format(self.line_number, line[0]))


                elif line[0] == "=":
                    self.seen_assignment = True
                    return self.initialize_list(line[1:])

                elif line[0].isdigit() or line[0].isalpha():
                    self.variable_name += line[0]
                    return self.initialize_list(line[1:])

            else:
                if line[0] == " ":
                    return self.initialize_list(line[1:])

                elif line[0] == "[":
                    self.seen_first_bracket = True
                    return self.initialize_list(line[1:])
                elif line[0] == "{":
                    raise InvalidSyntaxError("Line {}: invalid list declaration".format(self.line_number))

                elif line[0] == "]":
                    if not self.seen_first_bracket:
                        raise InvalidSyntaxError("Line {}: must have corresponding ']' bracket".format(self.line_number))

                    else:
                        if line[1] != ";":
                            raise InvalidSyntaxError("Line {}:must include closing ';'".format(self.line_number))
                        self.final_list.append(self.current_variable)
                        return self.initialize_list(line[1:])

                elif line[0].isdigit() or line[0].isalpha() or line[0] == ".":
                    self.current_variable += line[0]
                    return self.initialize_list(line[1:])
                elif line[0] == '"':
                    self.current_variable += line[0]
                    return self.initialize_list(line[1:])

                elif line[0] == ",":
                    self.final_list.append(self.current_variable)

                    self.current_variable = ''
                    return self.initialize_list(line[1:])

    def __iter__(self):
        if self.flag:
            return self.new_final_line.__iter__()


class AssignValue(ListData):
    __slots__ = ["final_data"]
    def __init__(self, line, line_number):
        ListData.__init__(self, line, line_number, flag = False)

        self.final_data = self.get_assigment_data(line)

    def get_assigment_data(self, line):

        if line[0] == ";":
            return [self.variable_name, self.current_variable, self.index]
        else:
            if not self.seen_assignment:
                if not self.seen_first_bracket:
                    if line[0].isalpha() or line[0].isdigit():
                        self.variable_name += line[0]
                        return self.get_assigment_data(line[1:])

                    elif line[0] == "[":
                        self.seen_first_bracket = True
                        return self.get_assigment_data(line[1:])

                    else:
                        raise InvalidSyntaxError("Line {}: unauthorized character".format(self.line_number))

                elif self.seen_first_bracket and not self.seen_last_bracket:
                    if line[0].isdigit():
                        self.index += line[0]
                        return self.get_assigment_data(line[1:])

                    elif line[0] == "]":
                        self.seen_last_bracket = True
                        return self.get_assigment_data(line[1:])

                    else:
                        raise InvalidSyntaxError("Line {}: index can only contain integer values".format(self.line_number))

                elif self.seen_last_bracket and self.seen_first_bracket:
                    if line[0] == " ":
                        return self.get_assigment_data(line[1:])

                    elif line[0] == ">":
                        self.seen_assignment = True
                        return self.get_assigment_data(line[1:])

                    else:
                        raise InvalidSyntaxError("Line {}:invalid access statement".format(self.line_number))

            else:

                if line[0] == " ":
                    return self.get_assigment_data(line[1:])

                elif line[0].isdigit() or line[0].isalpha():
                    self.current_variable += line[0]
                    return self.get_assigment_data(line[1:])

                else:
                    raise InvalidSyntaxError("Line {}: invalid access declaration".format(self.line_number))





    def variable_value(self):
        pass

    def __getattr__(self, name):
        if name == "index":
            return self.index

        elif name == "variable":
            return self.current_variable

        elif name == "list":
            return self.variable_name




class Parser:
    """
    types: string, int, double, boolean, list
    """
    #TODO: find syntax errors: intval2=34; should be int val2 = 456;
    #TODO: add all errors to error queue, raise one error, and list issues
    #IDEA: separate file for Perseus errors?
    #IDEA: classes for each keyword (token)?
    #TODO: every method should have a final else statement that throws an error
    #TODO: create 'increment' and 'decrement' keywords
    #TODO: modify assignment statements to be able to store function returns, list indices, etc.
    #TODO: support negative indicing?

    __slots__ = ["file", "data_tree", "last_variable", "line_number", "operation_names", "print_queue"]
    def __init__(self, the_file):
        self.file = the_file
        self.data_tree = defaultdict(dict)
        self.last_variable = None
        self.line_number = 1
        self.operation_names = {"+":["addition", lambda x, y:x+y], "*":["multplication", lambda x, y:x*y], "-":["subtraction", lambda x, y:x-y], "%":["modulo", lambda x, y:x%2], "/":["division", lambda x, y:x/y]}
        self.print_queue = []
        print self.parse_stream(self.file)
        print self.data_tree
    def parse_int_declaration(self, line, need_digit, variable, value):

        if line[0] == ";":

            if not line[1:]:
                return {variable:int(value)}
            else:
                raise InvalidLineTermination("Line {}: invalid line declaration".format(self.line_number))

        else:
            if line[0].isalpha() and not need_digit:
                variable += line[0]
                return self.parse_int_declaration(line[1:], False, variable, value)

            elif line[0] == " ":#here, can peek
                new_character = line[1]


                if new_character == " ":
                    return self.parse_int_declaration(line[1:], False, variable, value)
                elif new_character == "=" and not need_digit:

                    return self.parse_int_declaration(line[1:], True, variable, value)
                else:


                    if new_character != ";" and not new_character.isdigit():

                        raise SyntaxError("Line {}: reached invalid end of assignment".format(self.line_number))

                    return self.parse_int_declaration(line[1:], True, variable, value)

            elif line[0] == "=":
                if line[1] == "=":
                    raise InvalidSyntaxError("Line {}: '==' is used for comparison, not declaration".format(self.line_number))

                return self.parse_int_declaration(line[1:], True, variable, value)

            elif line[0].isdigit() and not need_digit:
                next_character = line[1]
                variable += line[0]
                return self.parse_int_declaration(line[1:], False, variable, value)

            else:
                if line[0].isdigit():

                    #next_character = line[1] if not line[1:] else line[1:]
                    next_character = None
                    if len(line[1:]) > 0:
                        next_character = line[1]
                    else:
                        next_character = ''

                    value += line[0]
                    if next_character.isdigit():

                        return self.parse_int_declaration(line[1:], True, variable, value)

                    elif re.findall("$", line[1:]) and line[1:] != ";":
                        raise InvalidSyntaxError("Line {}: forgot to include ';' and end of variable".format(self.line_number))
                    else:
                        return self.parse_int_declaration(line[1:], True, variable, value)
                else:
                    raise SyntaxError("Line {}: declared {} of type integer, but found value of not pure string".format(self.line_number, variable))


    def auto_parser(self, line, variable):

        if line[0] == ";":
            return variable

        else:
            if line[0].isdigit() or line[0].isalpha():
                variable += line[0]
                return self.auto_parser(line[1:], variable)
            else:
                raise InvalidSyntaxError("Line {}: invalid line declaration".format(self.line_number))


    def parse_double_declaration(self, line, need_digit, variable, value):

        if line[0] == ";":
            return {variable:float(value)}

        else:
            if line[0].isalpha() and not need_digit:
                variable += line[0]

                return self.parse_double_declaration(line[1:], False, variable, value)

            elif line[0] == " ":#here, can peek
                new_character = line[1]


                if new_character == " ":
                    return self.parse_double_declaration(line[1:], False, variable, value)
                elif new_character == "=" and not need_digit:

                    return self.parse_double_declaration(line[1:], True, variable, value)
                else:


                    if new_character != ";" and not new_character.isdigit():

                        raise SyntaxError("Line {}: reached invalid end of assignment".format(self.line_number))

                    return self.parse_double_declaration(line[1:], True, variable, value)

            elif line[0] == "=":
                if line[1] == "=":
                    raise InvalidSyntaxError("Line {}: '==' is used for comparison, not declaration".format(self.line_number))

                return self.parse_double_declaration(line[1:], True, variable, value)

            elif line[0].isdigit() and not need_digit:
                next_character = line[1]
                variable += line[0]
                return self.parse_double_declaration(line[1:], False, variable, value)

            elif line[0] == ".":

                if not line[1].isdigit():
                    raise InvalidDeclaration("Line {}: cannot have trailing decimal point".format(self.line_number))
                value += line[0]
                return self.parse_double_declaration(line[1:], True, variable, value)

            else:

                if line[0].isdigit():

                    #next_character = line[1] if not line[1:] else line[1:]
                    next_character = None
                    if len(line[1:]) > 0:
                        next_character = line[1]
                    else:
                        next_character = ''

                    value += line[0]
                    if next_character.isdigit() or next_character == ".":

                        return self.parse_double_declaration(line[1:], True, variable, value)

                    elif re.findall("$", line[1:]) and line[1:] != ";":
                        raise InvalidSyntaxError("Line {}: forgot to include ';' and end of variable".format(self.line_number))
                    else:
                        return self.parse_double_declaration(line[1:], True, variable, value)
                else:
                    raise SyntaxError("Line {}: declared {} of type integer, but found value of not pure string".format(self.line_number, variable))


    def parse_string_declaration(self, line, variable, value, expecting_string, seen_alpha):

        if line[0] == ";":

            new_dict = {variable:value}

            return new_dict

        else:
            if not expecting_string:
                if line[0].isalpha():
                    variable += line[0]
                    return self.parse_string_declaration(line[1:], variable, value, False, True)

                elif line[0].isdigit():
                    if seen_alpha:
                        variable += line[0]
                        return self.parse_string_declaration(line[1:], variable, value, False, True)
                    else:
                        raise InvalidDeclaration("line {}: digits cannot preceed variable".format(self.line_number))
                elif line[0] == " ":
                    if not line[1] in [" ", "="]:
                        raise InvalidSyntaxError("Line {}: unexpected end of declaration".format(self.line_number))
                    else:
                        return self.parse_string_declaration(line[1:], variable, value, False, False)

                elif line[0] == "=":
                    return self.parse_string_declaration(line[1:], variable, value, True, False)
            else:
                if line[0] == " ":
                    value += line[0]
                    return self.parse_string_declaration(line[1:], variable, value, True, True)
                elif line[0] == '"':
                    return self.parse_string_declaration(line[1:], variable, value, True, True)
                elif line[0].isalpha() or line[0].isdigit():
                    value += line[0]
                    return self.parse_string_declaration(line[1:], variable, value, True, True)
                else:
                    raise InvalidSyntaxError("Line {}: invalid syntax".format(self.line_number))


    def parse_boolean_declaration(self, line, variable, direction):
        if line[0] == ";":
            return {variable:direction}

        else:
            if line[0].isalpha():
                variable += line[0]
                return self.parse_boolean_declaration(line[1:], variable, direction)
            elif line[0].isdigit():

                if variable[-1].isdigit() or variable[-1].isdigit() and line[1].isdigit() or line[1].isalpha() or line[1] == ";":
                    variable += line[0]
                    return self.parse_boolean_declaration(line[1:], variable, direction)
                else:
                    raise InvalidDeclaration("Line {}: invalid syntax".format(self.line_number))

    def parse_operations(self, line, variable, value, seen_operator, seen_quotes, operator_type):

        if line[0] == ";":
            return [variable, value], operator_type

        else:
            if not seen_quotes:
                if line[0].isalpha() and seen_operator:
                    value += line[0]
                    return self.parse_operations(line[1:], variable, value, True, False, operator_type)
                elif line[0].isalpha():
                    variable += line[0]
                    return self.parse_operations(line[1:], variable, value, seen_operator, seen_quotes, operator_type)

                elif line[0].isdigit() and not seen_operator:
                    variable += line[0]
                    return self.parse_operations(line[1:], variable, value, seen_operator, seen_quotes, operator_type)

                elif line[0] == " ":

                    next_character = line[1]

                    if next_character != " " and next_character not in ["+", "-", "*", "/"] and not seen_operator:
                        raise InvalidSyntaxError("Line {}: must have valid operator".format(self.line_number))

                    return self.parse_operations(line[1:], variable, value, seen_operator, seen_quotes, operator_type)

                elif line[0] in ["+", "-", "*", "/"]:

                    if line[1:]:
                        if line[1] != " " and line[1].isdigit() and line[1] != '"': #used to be: if line[1] != " " and line[1].isdigit() and line[1] != '"':
                        #if not line[1].isdigit() or line[1] != '"':
                            raise InvalidSyntaxError("Line {}: unexpected end of declaration".format(self.line_number))

                    operator_type = [i for i in ["+", "-", "*", "/", "%"] if line[0] == i][0]
                    return self.parse_operations(line[1:], variable, value, True, seen_quotes, operator_type)

                elif line[0].isdigit() and seen_operator:
                    value += line[0]
                    return self.parse_operations(line[1:], variable, value, True, seen_quotes, operator_type)
                elif line[0] == ".":
                    if variable[-1].isdigit() and line[1].isdigit():
                        value += line[0]
                        return self.parse_operations(line[1:], variable, value, True, seen_quotes, operator_type)

                    else:
                        raise InvalidDeclaration("Line {}: invalid formatting; expected a full double variable".format(self.line_number))

                elif line[0] == '"':
                    return self.parse_operations(line[1:], variable, value, True, True, operator_type)


            else:
                if line[0] != '"':
                    value += line[0]
                    return self.parse_operations(line[1:], variable, value, True, True, operator_type)
                else:
                    return self.parse_operations(line[1:], variable, value, True, True, operator_type)

    def parse_variable_storage(self, line, var1, var2, operator_type, seen_operator):

        if line[0] == ";":
            return [var1, var2], operator_type

        else:
            if not seen_operator:
                if line[0].isalpha() or line[0].isdigit():
                    var1 += line[0]
                    return self.parse_variable_storage(line[1:], var1, var2, operator_type, seen_operator)

                elif line[0] == " ":
                    if line[1].isalpha() or line[1].isdigit():
                        raise InvalidDeclaration("Line {}: cannot have more than two variables in declaration".format(self.line_number))
                    return self.parse_variable_storage(line[1:], var1, var2, operator_type, seen_operator)
                elif line[0] == operator_type:
                    return self.parse_variable_storage(line[1:], var1, var2, line[0], True)

            else:
                if line[0].isalpha() or line[0].isdigit():
                    var2 += line[0]
                    return self.parse_variable_storage(line[1:], var1, var2, operator_type, seen_operator)
                elif line[0] == " ":
                    return self.parse_variable_storage(line[1:], var1, var2, operator_type, seen_operator)

                elif not line[0].isalpha() and not line[0].isdigit():
                    raise InvalidSyntaxError("Line {}:illegal formatting of storage expression".format(self.line_number))



    def parse_output_statement(self, line, var):
        if line[0] == ";":
            return var

        else:

            if line[0].isalpha() or line[0].isdigit() or line[0] in '""':
                var += line[0]
                return self.parse_output_statement(line[1:], var)

            else:
                raise InvalidSyntaxError("Line {}:output statement cannot contain spaces or operators".format(self.line_number))



    def parse_stream(self, line):

        if not line:
            return "Finished parsing"

        else:
            if line[0].startswith("int") and re.findall("^int\s", line[0]):

                integers = self.parse_int_declaration(line[0][len("int "):], False, '', '')
                print integers
                self.data_tree["Integer"].update(integers)
            elif line[0].startswith("double") and re.findall("^double\s", line[0]):
                if not re.findall("\d\.\d", line[0]):
                    name, variable = re.split("\s*=\s*", line[0][len("double "):])

                    raise InvalidDeclaration("Line {}:declared '{}' double, found integer".format(self.line_number, name))
                values = self.parse_double_declaration(line[0][len("double "):], False, '', '')
                self.data_tree["Double"].update(values)
            elif line[0].startswith("string") and re.findall("^string\s", line[0]):

                val = self.parse_string_declaration(line[0][len("string "):], '', '', False, False)
                self.data_tree["String"].update(val)

            elif line[0].startswith("boolean") and re.findall("^boolean\s", line[0]):
                new_line = line[0][len("boolean "):]
                if new_line[0] == "!":
                    val1 = self.parse_boolean_declaration(new_line[1:], '', False)
                    self.data_tree["Boolean"].update(val1)
                else:
                    val1 = self.parse_boolean_declaration(new_line, '', True)
                    self.data_tree["Boolean"].update(val1)


            elif re.findall("^assign\s", line[0]):
                new_data = line[0][len("assign "):]
                if "=" in new_data:
                    name, val = re.split("\s*=\s*", new_data)
                    if not any(name in self.data_tree[i] for i in ["String", "Boolean", "Integer", "Double"]):
                        raise VariableNotDeclared("Line {}: variable '{}' not found in tree".format(name))

                    if val[-1] != ";":
                        raise InvalidSyntaxError("Line {}: missing ';' at end of assignment".format(self.line_number))
                    val = val[:-1]
                    if all(i.isdigit() for i in val):
                        self.data_tree["Integer"][name] = int(val)

                    elif re.search("^\d+\.\d+$", val) is not None and re.search("\d+\.\d+", val).group(0) == val:
                        self.data_tree["Double"][name] = float(val)
                    elif val.startswith('"') and val.endswith('"'):
                        self.data_tree["String"][name] = val[1:-1]



                else:
                    if not new_data.endswith(";"):
                        raise InvalidSyntaxError("Line {}: missing ';' at end of declaration".format(self.line_number))

                    if new_data.startswith("!"):


                        self.data_tree["Boolean"][new_data[:-1]] = False

                    else:
                        self.data_tree["Boolean"][new_data[:-1]] = True

            elif re.findall("^update\s", line[0]):
                final_dict, operation = self.parse_operations(line[0][len("update "):], '', '', False, False, '')
                first, second = final_dict
                print final_dict
                isint = re.search("^\d+$", second)
                isdouble = re.search("^\d+\.\d+$", second)
                isstring = re.search('^.*?$', second)



                final_type = [a for a, b in zip(["int", "double", "string"], [isint, isdouble, isstring]) if b is not None]

                types = [a for a, b in self.data_tree.items() if first in b]
                if final_type[0] == "int":
                    second = int(second)
                elif final_type[0] == "double":
                    second = float(second)

                if any(second in self.data_tree[i] for i in ["String", "Boolean", "Double", "Integer"]):
                    the_type = [i for i in ["String", "Boolean", "Double", "Integer"] if second in self.data_tree[i]][0]

                    second = self.data_tree[the_type][second]

                if not any(first in self.data_tree[i] for i in ["String", "Boolean", "Double", "Integer"]):
                    raise VariableNotDeclared("Line {}: variable not found in tree".format(self.line_number))
                if type(self.data_tree[types[0]][first]) != type(second):
                    raise InvalidOperation("Line {}: cannot perform {} by variable of type {} on variable of type {}".format(self.line_number, self.operation_names[operation][0], type(second), type(first)))

                type_of_operation = self.operation_names[operation][-1]


                self.data_tree[types[0]][first] = type_of_operation(self.data_tree[types[0]][first], second)

            elif re.findall("^store\s", line[0]):

                [firstvar, secondvar], operator = self.parse_variable_storage(line[0][len("store "):], '', '', "=", False)
                data_type1 = [i for i in ["Double", "String", "Boolean", "Integer"] if firstvar in self.data_tree[i]]
                data_type2 = [i for i in ["Double", "String", "Boolean", "Integer"] if secondvar in self.data_tree[i]]
                if not data_type1:
                    raise VariableNotDeclared("Line {}: variable '{}' not declared".format(self.line_number, firstvar))
                if not data_type2:
                    raise VariableNotDeclared("Line {}: variable '{}' not declared".format(self.line_number, secondvar))

                if data_type1[0] != data_type2[0]:

                    raise UnassignableTypes("Line {}: cannot assign variable of type '{}' to variable of type '{}'".format(self.line_number, data_type2[0], data_type1[0]))

                self.data_tree[data_type1[0]][firstvar] = self.data_tree[data_type2[0]][secondvar]

            elif re.findall("^!", line[0]):
                if line[0][-1] != ";":
                    raise InvalidSyntaxError("Line {}: missing ';'".format(self.line_number))

                if not all(i.isdigit() or i.isalpha() for i in line[0][1:-1]):
                    raise InvalidDeclaration("Line {}: invalid variable declaration".format(self.line_number))

                variable = line[0][1:-1]
                if variable not in self.data_tree["Boolean"]:
                    raise VariableNotDeclared("Line {}: variable '{}' not declared as type 'Boolean'".format(self.line_number, variable))

                self.data_tree["Boolean"][variable] = not self.data_tree["Boolean"][variable]

            elif re.findall("^output\s", line[0]):
                variable = self.parse_output_statement(line[0][len("output "):], '')
                print "variable", repr(variable)
                if not variable.startswith('"') and variable.endswith('"') or variable.startswith('"') and not variable.endswith('"'):
                    raise InvalidOutputStatement("Line {}: unbalanced quotes".format(self.line_number))

                elif variable.startswith('"') and variable.endswith('"'):
                    self.print_queue.append(variable[1:-1])
                else:
                    possibilites = [i for i in ["Double", "String", "Boolean", "Integer"] if variable in self.data_tree[i]]
                    if not possibilites:
                        raise VariableNotDeclared("Line {}: variable '{}' not found".format(self.line_number, variable))

                    self.print_queue.append(self.data_tree[possibilites[0]][variable])

            elif re.findall("^List\s", line[0]):
                the_list = ListData(line[0][len("List "):], self.line_number, flag=True)
                variable_name = the_list.variable_name
                new_list = [i for i in the_list]
                print "variable_name", variable_name, "the_list", new_list

                new_final_list = []
                for variable in new_list:
                    if variable.startswith('"') and not variable.endswith('"'):
                        raise InvalidSyntaxError("Line {}:unbalanced quotes around string declaration".format(self.line_number))

                    elif not variable.startswith('"') and variable.endswith('"'):
                        raise InvalidSyntaxError("Line {}:unbalanced quotes around string declaration".format(self.line_number))

                    elif variable.startswith('"') and variable.endswith('"'):
                        new_final_list.append(variable[1:-1])

                    elif re.search('^\d+$', variable) is not None and re.search('^\d+$', variable).group(0) == variable:
                        new_final_list.append(int(variable))

                    elif re.search('^\d+\.\d+$', variable) is not None and re.search('^\d+\.\d+$', variable).group(0) == variable:
                        new_final_list.append(float(variable))

                    elif variable in ["True", "False"]:
                        new_final_list.append((lambda x:{"True":True, "False":False}[x])(variable))


                    else:
                        if variable.isalnum() and variable not in ["True", "False"]:
                            possibilites = [i for i in ["Double", "Boolean", "String", "List"] if variable in self.data_tree[i]]
                            if not possibilites:
                                raise VariableNotDeclared("Line {}: variable '{}' not declared".format(self.line_number, variable))

                            new_final_list.append(self.data_tree[possibilites[0]][variable])

                self.data_tree["List"][variable_name] = new_final_list


            elif re.findall("^access\s", line[0]):
                access_data = AssignValue(line[0][len("access "):], self.line_number)
                index = access_data.index
                list_name = access_data.list
                variable_name = access_data.variable
                if not any(variable_name in self.data_tree[i] for i in ["Auto", "Boolean", "String", "Double", "Integer"]):
                    raise VariableNotDeclared("Line {}: variable '{}' not found".format(self.line_number, variable_name))
                if list_name not in self.data_tree["List"]:
                    raise VariableNotDeclared("Line {}: variable '{}' not found".format(self.line_number, list_name))
                if int(index) >= len(self.data_tree["List"][list_name]):
                    raise IndexOutOfBoundsError("Line {}: index of {} is greater than length of List {} (size of {})".format(self.line_number, int(index), list_name, len(self.data_tree["List"][list_name])))


            elif re.findall("^auto\s", line[0]):
                if line[0][-1] != ";":
                    raise InvalidLineTermination("Line {}: must complete statement with ';'".format(self.line_number))

                new_variable_name = self.auto_parser(line[0][len("auto "):], '')
                self.data_tree["Auto"][new_variable_name] = None





            self.line_number += 1

            return self.parse_stream(line[1:])




p = Parser([i.strip('\n') for i in open('sample_file.txt')])
