"""
A cross-platform Truth Table Generator written in Python.
"""

import sys
from inspect import signature
import toga
from toga import style
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


# Truth Table Logic

class Infix(object):
    def __init__(self, func):
        self.func = func
    def __or__(self, other):
        return self.func(other)
    def __ror__(self, other):
        return Infix(lambda x: self.func(other, x))
    def __call__(self, v1, v2):
        return self.func(v1, v2)

# Valid symbols that are not alphabetical characters
valid_symbols = ['→','↔','∨','∧','⊕','¬','(',')']

#         ~   ¬     ^   ⊕     &    ∧     |    ∨
t_dict = {38: 8743, 94: 8853, 124: 8744, 126: 172} # Dict for str.translate()

# Prettifies and input string by using more visually appealing symbols and equalizing spacing
def prettify(s): 
    return " ".join(s.translate(t_dict)
                     .replace('<->','↔')
                     .replace('->','→')
                     .replace(" ",""))

conditional = Infix(lambda a,b: ~a | b)
biconditional = Infix(lambda a,b: ~(a ^ b))

# Makes `->` and `<->` inline functions
def fix_inline(s):
    return s.replace(
        '<->','|biconditional|').replace(
        '->','|conditional|')

# Flattens lists
flatten = lambda l: sum(map(flatten,l),[]) if isinstance(l,list) else [l]

# Takes a function as an input and returns the arity of the function
def get_arity(f): 
    return len(signature(f).parameters)

# Gets the input columns for the truth table as strings
def get_bits(n): 
    return [*map(lambda x:[*map(int,bin(x)[2:].zfill(n))],range(2**n))]


# Gets the input columns for the truth table as strings
def get_bits_s(n): 
    return [*map(lambda x:[*map(str,bin(x)[2:].zfill(n))],range(2**n))]

# Given an input function, use the arity to get the input columns for the truth table
def get_bits_f(f): 
    return get_bits(get_arity(f))

# Given an input function, use the arity to get the input columns for the truth table
def get_bits_f_s(f): 
    return get_bits_s(get_arity(f))

# Gets the output column of the truth table
def output(f): 
    return [*map(f,*zip(*get_bits_f(f)))]

# Combines the input columns of the truth table with the output column
def make_tt(f): 
    return [*map(flatten,[*map(list,zip(get_bits_f_s(f),output(f)))])]

# Gets the input variables for the boolean expression
def get_vars(s):
    return sorted([*{*filter(str.isalpha,s)}])

# Gets the parameters to be used in the generated function
def get_parameters(s):
    return ','.join(get_vars(s))

# Takes in a boolean expression as a string, converts it into a function, and makes the truth table
def make_truth_table(s):
    return make_tt(eval(f"lambda {get_parameters(s)}:['0','1'][{fix_inline(s)}]"))

# Gets the headings to display the truth table
def get_headings(s): 
    return [*get_vars(s),prettify(s)]


# HTML Function

# Generates the truth table string to be saved in an HTML file
def make_tt_html(s):
    return f"""<!DOCTYPE html>
<html>
<style>
th, td {chr(123)}
  border:1px solid black;
  padding:1ex;
{chr(125)}
table {chr(123)}
  border-collapse: collapse;
{chr(125)}
code {chr(123)}
  font-family: Consolas,"courier new";
  background-color: #eee;
  border: 1px solid #999;
  padding: 5px;
{chr(125)}
</style>
<body>

<h2>Truth Table for <code>{prettify(s)}</code></h2>

<table>
  <tr>
{chr(10).join([*map(lambda t: f"    <th>{t}</th>",get_headings(s))])}
  </tr>
{chr(10).join([*map(lambda r: f"  <tr>{chr(10)}{chr(10).join([*map(lambda c: f'    <td>{c}</td>',r)])}{chr(10)}  </tr>",make_truth_table(s))])}
</table>

</body>
</html>
"""


# Markdown Functions

# Generates a Markdown-formatted line
def md_line(l): 
    return f"|{'|'.join(map(str,l))}|"

# Generates a Markdown-formatted header
def md_header(s):
    vars_ = get_vars(s)
    return f"|{'|'.join(vars_)}|{prettify(s)}|\n|{'|'.join('-'*len(vars_))}|:-:|\n"

# Generates a Markdown-formatted table
def md_table(s):
    return md_header(s)+'\n'.join(map(md_line,make_truth_table(s)))

# Generates the truth table string to be saved in a Markdown file
def make_tt_markdown(s):
    return f"# Truth Table for `{prettify(s)}`\n{md_table(s)}"


# LaTeX Functions

# Converts prettified string to LaTeX style
def lt_prettify(s): 
    return prettify(s).replace(
        '→','\\rightarrow').replace(
        '↔','\\leftrightarrow').replace(
        '∨','\\lor').replace(
        '∧', '\\land').replace(
        '⊕', '\\oplus').replace(
        '¬', '\\neg')

# Generates a LaTeX-formatted line
def lt_line(l):
    return ' & '.join(map(str,l))+'\\\\'

# Generates a LaTeX-formatted header
def lt_header(s): 
    return lt_line(get_vars(s)+[lt_prettify(s)])

# Generates a LaTeX-formatted table
def lt_table(s):
    return '\n'.join(map(lt_line,make_truth_table(s)))

# Generates the truth table string to be saved in a LaTeX file
def make_tt_latex(s): 
    return "\\documentclass[a4paper]{article}\n\\begin{document}" + \
        "\n\\title{Truth Table for $" + lt_prettify(s) + "$}\n\\author{Kyle Mueller}" + \
        "\n\\maketitle\n\\begin{displaymath}" + \
        "\n\\begin{array}{|" + ' '.join('c'*len(get_vars(s))) + "|c|}\n" + lt_header(s) + \
        "\n\\hline\n" + lt_table(s) + \
        "\n\\end{array}\n\\end{displaymath}\n\\end{document}"


# ORG Functions

# Generates a ORG-formatted line
def org_line(l):
    return f"|{'|'.join(map(str,l))}|"

# Generates a ORG-formatted header
def org_header(s):
    vars_ = get_vars(s)
    return f"|{'|'.join(vars_+[prettify(s)])}|\n|{'+'.join('-'*(len(vars_)+1))}|\n"

# Generates a ORG-formatted table
def org_table(s):
    return org_header(s) + '\n'.join(map(org_line,make_truth_table(s)))

# Generates the truth table string to be saved in a ORG file
def make_tt_org(s):
    return f"* Truth Table for ~{prettify(s)}~\n{org_table(s)}"


# Error Checking Functions

# Checks if a character is valid
def valid_c(s):
    return s.isalpha() or s in valid_symbols

# Checks if a boolean expression is valid
def valid_bx(s):
    return all(map(valid_c,prettify(s).split())) and len(get_vars(s)) < 6


# Application Class

class TruthTableGenerator(toga.App):   
    
    def startup(self):
        if not hasattr(sys, 'getandroidapilevel'):
            help_group = toga.Group.HELP

            input_syntax = toga.Command(
                self.ShowInputSyntax,
                label="Input Syntax",
                shortcut=toga.Key.MOD_1 + toga.Key.SHIFT + 'i',
                group=help_group
            )

            file_group = toga.Group.FILE

            save_ = toga.Command(
                self.SaveBooleanExpression,
                label="Save",
                shortcut=toga.Key.MOD_1 + 's',
                group=file_group            
            )

            import_ = toga.Command(
                self.ImportBooleanExpression,
                label="Import",
                shortcut=toga.Key.MOD_1 + 'i',
                group=file_group
            )

            export_html = toga.Command(
                self.ExportHTML,
                label="Export as HTML",
                shortcut=toga.Key.MOD_1 + 'h',
                group=file_group
            )

            export_markdown = toga.Command(
                self.ExportMarkdown,
                label="Export as Markdown",
                shortcut=toga.Key.MOD_1 + 'm',
                group=file_group
            )

            export_latex = toga.Command(
                self.ExportLaTeX,
                label="Export as LaTeX",
                shortcut=toga.Key.MOD_1 + 'l',
                group=file_group
            )

            export_org = toga.Command(
                self.ExportORG,
                label="Export as ORG",
                shortcut=toga.Key.MOD_1 + 'o',
                group=file_group
            )

            update_table = toga.Command(
                self.make_tt,
                label="Update Truth Table",
                shortcut=toga.Key.MOD_1 + 'u',
                group=file_group
            )

            self.commands.add(export_html, export_markdown, export_latex, export_org, input_syntax, save_, import_, update_table)

        self.main_box = toga.Box(style=Pack(direction=COLUMN))

        default_expression = "p -> q"

        input_label = toga.Label(
            'Enter a Boolean Expression: ',
            style=Pack(padding=(0, 5))
        )

        self.be_input = toga.TextInput(style=Pack(flex=1), placeholder=default_expression, on_change=self.make_tt_auto)

        input_box = toga.Box(style=Pack(direction=ROW, padding=5))
        input_box.add(input_label)
        input_box.add(self.be_input)

        button = toga.Button(
            'Generate Truth Table',
            on_press=self.make_tt,
            style=Pack(padding=5)
        )

        self.main_box.add(input_box)
        self.main_box.add(button)

        if not hasattr(sys, 'getandroidapilevel'):
            self.truth_table = toga.Table(
                headings=get_headings(default_expression), 
                data=make_truth_table(default_expression), 
                style=Pack(
                    flex=1,
                    padding=5))

            self.main_box.add(self.truth_table)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()
        self.ShowInputSyntax()

    def show_err(self, boolean_expression):
        m_string = f"The boolean expression '{boolean_expression}' is invalid.\n\n" \
                    "Please enter a valid boolean expression and try again."
        if hasattr(sys, 'getandroidapilevel'):
            self.main_window.info_dialog(
                title="Invalid Boolean Expression",
                message=m_string)
        else:
            self.main_window.error_dialog(
                title="Invalid Boolean Expression",
                message=m_string+"\n\nPress CTRL+SHIFT+i for instructions on proper input syntax.")

    def make_tt(self, widget='', override=''):
        boolean_expression = override or self.be_input.value or 'p -> q'

        if not valid_bx(boolean_expression):
            self.show_err(boolean_expression)

        else:
            try:
                tt_headings = get_headings(boolean_expression)
                tt_data = make_truth_table(boolean_expression)

                if hasattr(sys, 'getandroidapilevel'):
                    p_string = '\n'.join([*map(' | '.join,[tt_headings]+tt_data)])

                    self.main_window.info_dialog(
                        title=f"Truth Table for {prettify(boolean_expression)}",
                        message=f"{p_string}")
                else:
                    self.main_box.remove(self.truth_table)

                    self.truth_table = toga.Table(
                        headings=tt_headings, 
                        data=tt_data, 
                        style=Pack(
                            flex=1, 
                            padding=5))
                                
                    self.main_box.add(self.truth_table)
            except:
                self.show_err(boolean_expression)

    def make_tt_auto(self, widget='', override=''):
        boolean_expression = override or self.be_input.value or 'p -> q'

        tt_headings = get_headings(boolean_expression)
        tt_data = make_truth_table(boolean_expression)

        if hasattr(sys, 'getandroidapilevel'):
            p_string = '\n'.join([*map(' | '.join,[tt_headings]+tt_data)])

            self.main_window.info_dialog(
                title=f"Truth Table for {prettify(boolean_expression)}",
                message=f"{p_string}")
        else:
            self.main_box.remove(self.truth_table)

            self.truth_table = toga.Table(
                headings=tt_headings, 
                data=tt_data, 
                style=Pack(
                    flex=1, 
                    padding=5))
                        
            self.main_box.add(self.truth_table)

    def GetFilename(self, title, file_types):
        return self.main_window.save_file_dialog(
            title=title, 
            suggested_filename="truth_table",
            file_types=file_types)

    def SaveFile(self, title, file_types, export_function):
        boolean_expression = self.be_input.value or 'p -> q'

        if not valid_bx(boolean_expression):
            self.show_err(boolean_expression)
        
        else:
            try:
                self.make_tt_auto(widget=None)

                filename = self.GetFilename(title, file_types)
            
                with open(filename, "w", encoding='utf-8') as f:
                    f.writelines(export_function(boolean_expression))
            except:
                self.show_err(boolean_expression)

    def ImportBooleanExpression(self, widget):
        filename = self.main_window.open_file_dialog(
            title="Import",
            file_types=["txt"])
        
        boolean_expression = 'p -> q'

        with open(filename, "r", encoding='utf-8') as f:
            boolean_expression = f.readline() or 'p -> q'

        if not valid_bx(boolean_expression):
            self.show_err(boolean_expression)

        else:
            self.be_input.value = boolean_expression
            self.make_tt(widget=None, override=boolean_expression)

    def SaveBooleanExpression(self, widget):
        self.SaveFile("Save", ["txt"], lambda x: x)

    def ExportHTML(self, widget):
        self.SaveFile("Export as HTML", ["html", "txt"], make_tt_html)

    def ExportMarkdown(self, widget):
        self.SaveFile("Export as Markdown", ["md", "txt"], make_tt_markdown)

    def ExportLaTeX(self, widget):
        self.SaveFile("Export as LaTeX", ["tex", "txt"], make_tt_latex)

    def ExportORG(self, widget):
        self.SaveFile("Export as ORG", ["org", "txt"], make_tt_org)

    def ShowInputSyntax(self, widget=''):
        if not hasattr(sys, 'getandroidapilevel'):
            return self.main_window.info_dialog(
                title="Input Syntax",
                message="Please use the symbols from \"Input Syntax\" below when entering a boolean expression into the input box.\n\n" \
                        "Write boolean expressions in infix notation, as if you were writing Python code (e.g. \"p & q | r\").\n\n" \
                        "Please limit all boolean variables to single letters of the english alphabet (i.e. p, q, r, s, etc.).\n\n" \
                        "Please limit all boolean expressions to 5 or fewer unique boolean variables.\n\n" \
                        "TO SEE THIS WINDOW AGAIN, go to \"Help -> Input Syntax\" or use \"CTRL+SHIFT+i\"\n\n" \
                        "|   Input Syntax     |   Logic Symbols  |   Name\n" \
                        "|----------------------|----------------------|--------------------\n" \
                        "|   ~                        |   ¬, ˜, !                 |   not\n" \
                        "|   &                        |   ∧, ·, &               |   and\n" \
                        "|   |                          |   ∨, +, ∥               |   or\n" \
                        "|   ^                        |   ⊕, ⊻, ≢              |   xor, not equivalence\n" \
                        "|   ->                       |   →, ⇒, ⊃              |   conditional\n" \
                        "|   <->                    |   ↔, ⇔, ≡              |   biconditional, equivalence")
        else:
            return self.main_window.info_dialog(
                title="Input Syntax",
                message="Please use the symbols from \"Input Syntax\" below when entering a boolean expression into the input box.\n\n" \
                        "Write boolean expressions in infix notation, as if you were writing Python code (e.g. \"p & q | r\").\n\n" \
                        "Please limit all boolean variables to single letters of the english alphabet (i.e. p, q, r, s, etc.).\n\n" \
                        "Please limit all boolean expressions to 5 or fewer unique boolean variables.\n\n" \
                        "|  Syntax  |  Logic      |  Name\n" \
                        "|--------------|---------------|-----------------\n" \
                        "|  ~            |  ¬, ˜, !       |  not\n" \
                        "|  &            |  ∧, ·, &      |  and\n" \
                        "|  |              |  ∨, +, ∥      |  or\n" \
                        "|  ^             |  ⊕, ⊻, ≢     |  xor\n" \
                        "|  -              |  →, ⇒, ⊃ |  conditional\n" \
                        "|  <->          |  ↔, ⇔, ≡ |  biconditional")

def main():
    return TruthTableGenerator()
