"""
A cross-platform Truth Table Generator written in Python.
"""
import sys
import toga
from toga import style
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from inspect import signature

class Infix(object):
    def __init__(self, func):
        self.func = func
    def __or__(self, other):
        return self.func(other)
    def __ror__(self, other):
        return Infix(lambda x: self.func(other, x))
    def __call__(self, v1, v2):
        return self.func(v1, v2)

valid_symbols = ['→','↔','∨','∧','⊕','¬','(',')']

#         ~   ¬     ^   ⊕     &    ∧     |    ∨
t_dict = {38: 8743, 94: 8853, 124: 8744, 126: 172} # Dict for str.translate()
prettify = lambda s: " ".join(s.translate(t_dict).replace('<->','↔').replace('->','→').replace(" ",""))

cond = Infix(lambda a,b: ~a | b) # Conditional
bicond = Infix(lambda a,b: ~(a ^ b)) # Biconditional
fix_inline = lambda s: s.replace('<->','|bicond|').replace('->','|cond|')

flatten = lambda l: sum(map(flatten,l),[]) if isinstance(l,list) else [l] # Flattens lists
get_arity = lambda f: len(signature(f).parameters) # Returns Arity of a Function
get_bits = lambda n: [*map(lambda x:[*map(int,bin(x)[2:].zfill(n))],range(2**n))] # Get Bits
get_string_bits = lambda n: [*map(lambda x:[*map(str,bin(x)[2:].zfill(n))],range(2**n))] # Get String Bits
gbfa = lambda f: get_bits(get_arity(f)) # Get Bits from Arity
gsbfa = lambda f: get_string_bits(get_arity(f)) # Get String Bits from Arity
output = lambda f: [*map(f,*zip(*gbfa(f)))] # Output of Boolean Function
make_tt = lambda f: [*map(flatten,[*map(list,zip(gsbfa(f),output(f)))])] # Make Truth Table
gv = lambda s: sorted([*{*filter(str.isalpha,s)}]) # Gets Variables from String
gvf = lambda s: ','.join(gv(s)) # Get Vars (formatted)
make_truth_table = lambda s: make_tt(eval(f"lambda {gvf(s)}:['0','1'][{fix_inline(s)}]")) # Make Truth Table from String

get_headings = lambda s: [*gv(s),prettify(s)]

make_tt_html = lambda s: """<!DOCTYPE html>
<html>
<style>
th, td {
  border:1px solid black;
  padding:1ex;
}
table {
  border-collapse: collapse;
}
code {
  font-family: Consolas,"courier new";
  background-color: #eee;
  border: 1px solid #999;
  padding: 5px;
}
</style>
<body>

""" + f"""<h2>Truth Table for <code>{prettify(s)}</code></h2>

<table>
  <tr>
{chr(10).join([*map(lambda t: f"    <th>{t}</th>",get_headings(s))])}
  </tr>
{chr(10).join([*map(lambda r: f"  <tr>{chr(10)}{chr(10).join([*map(lambda c: f'    <td>{c}</td>',r)])}{chr(10)}  </tr>",make_truth_table(s))])}
</table>

</body>
</html>
"""

md_line = lambda l: f"|{'|'.join(map(str,l))}|" # Markdown Line
md_header = lambda s: f"|{'|'.join(gv(s))}|{prettify(s)}|\n|{'|'.join('-'*len(gv(s)))}|:-:|\n" # Markdown Header
md_table = lambda s: md_header(s)+'\n'.join(map(md_line,make_truth_table(s))) # Markdown Truth Table
make_tt_markdown = lambda s: f"""# Truth Table for `{prettify(s)}`
{md_table(s)}
"""

lt_prettify = lambda s: prettify(s).replace(
    '→','\\rightarrow').replace(
    '↔','\\leftrightarrow').replace(
    '∨','\\lor').replace(
    '∧', '\\land').replace(
    '⊕', '\\oplus').replace(
    '¬', '\\neg')
lt_line = lambda l: ' & '.join(map(str,l))+'\\\\'
lt_header = lambda s: lt_line(gv(s)+[lt_prettify(s)])
lt_table = lambda s: '\n'.join(map(lt_line,make_truth_table(s)))
make_tt_latex = lambda s: "\\documentclass[a4paper]{article}\n\\begin{document}" + \
    "\n\\title{Truth Table for $" + lt_prettify(s) + "$}\n\\author{Kyle Mueller}" + \
    "\n\\maketitle\n\\begin{displaymath}" + \
    "\n\\begin{array}{|" + ' '.join('c'*len(gv(s))) + "|c|}\n" + lt_header(s) + \
    "\n\\hline\n" + lt_table(s) + \
    "\n\\end{array}\n\\end{displaymath}\n\\end{document}"

org_line = lambda l: f"|{'|'.join(map(str,l))}|"
org_header = lambda s: f"|{'|'.join(gv(s)+[prettify(s)])}|\n|{'+'.join('-'*(len(gv(s))+1))}|\n"
org_table = lambda s: org_header(s) + '\n'.join(map(org_line,make_truth_table(s)))
make_tt_org = lambda s: f"* Truth Table for ~{prettify(s)}~\n{org_table(s)}"

save_bx = lambda s: s

valid_s = lambda s: s.isalpha() or s in valid_symbols
valid_bx = lambda s: all(map(valid_s,prettify(s).split()))

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

            self.commands.add(export_html, export_markdown, export_latex, export_org, input_syntax, save_, import_)

        self.main_box = toga.Box(style=Pack(direction=COLUMN))

        default_expression = "p -> q"

        input_label = toga.Label(
            'Enter a Boolean Expression: ',
            style=Pack(padding=(0, 5))
        )
        self.be_input = toga.TextInput(style=Pack(flex=1), placeholder=default_expression)

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
        if not hasattr(sys, 'getandroidapilevel'):
            self.main_window.info_dialog(
                title="Input Syntax",
                message="""Please use the symbols from "Input Syntax" below when entering a boolean expression into the input box.

Write boolean expressions in infix notation, as if you were writing Python code (e.g. "p & q | r").

Please limit all boolean variables to single letters of the english alphabet (i.e. p, q, r, s, etc.).

TO SEE THIS WINDOW AGAIN, go to "Help -> Input Syntax" or use "CTRL+SHIFT+i"

    |   Input Syntax     |   Logic Symbols  |   Name
    |----------------------|----------------------|--------------------
    |   ~                        |   ¬, ˜, !                 |   not
    |   &                        |   ∧, ·, &               |   and
    |   |                          |   ∨, +, ∥               |   or
    |   ^                        |   ⊕, ⊻, ≢              |   xor, not equivalence
    |   ->                       |   →, ⇒, ⊃              |   conditional
    |   <->                    |   ↔, ⇔, ≡              |   biconditional, equivalence""")
        else:
            self.main_window.info_dialog(
                title="Input Syntax",
                message="""Please use the symbols from "Syntax" below when entering a boolean expression into the input box.

Write boolean expressions in infix notation, as if you were writing Python code (e.g. "p & q | r").

Please limit all boolean variables to single letters of the english alphabet (i.e. p, q, r, s, etc.).

|  Syntax  |  Logic      |  Name
|--------------|---------------|-----------------
|  ~            |  ¬, ˜, !       |  not
|  &            |  ∧, ·, &      |  and
|  |              |  ∨, +, ∥      |  or
|  ^             |  ⊕, ⊻, ≢     |  xor
|  -              |  →, ⇒, ⊃ |  conditional
|  <->          |  ↔, ⇔, ≡ |  biconditional""")

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

        print(boolean_expression)

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

    def GetFilename(self, title, file_types):
        return self.main_window.save_file_dialog(
            title=title, 
            suggested_filename="truth_table",
            file_types=file_types)

    def SaveFile(self, title, file_types, export_function):
        filename = self.GetFilename(title, file_types)

        boolean_expression = self.be_input.value or 'p -> q'
        
        with open(filename, "w", encoding='utf-8') as f:
            f.writelines(export_function(boolean_expression))

    def ImportBooleanExpression(self, widget):
        filename = self.main_window.open_file_dialog(
            title="Import",
            file_types=["txt"])
        
        boolean_expression = ""

        with open(filename, "r", encoding='utf-8') as f:
            boolean_expression = f.readline() or 'p -> q'

        self.be_input.value = boolean_expression
        self.make_tt(widget=None, override=boolean_expression)

    def SaveBooleanExpression(self, widget):
        self.SaveFile("Save", ["txt"], save_bx)

    def ExportHTML(self, widget):
        self.SaveFile("Export as HTML", ["html", "txt"], make_tt_html)

    def ExportMarkdown(self, widget):
        self.SaveFile("Export as Markdown", ["md", "txt"], make_tt_markdown)

    def ExportLaTeX(self, widget):
        self.SaveFile("Export as LaTeX", ["tex", "txt"], make_tt_latex)

    def ExportORG(self, widget):
        self.SaveFile("Export as ORG", ["org", "txt"], make_tt_org)

    def ShowInputSyntax(self, widget):
        return self.main_window.info_dialog(
            title="Input Syntax",
            message="""Please use the symbols from "Input Syntax" below when entering a boolean expression into the input box.

Write boolean expressions in infix notation, as if you were writing Python code (e.g. "p & q | r").

Please limit all boolean variables to single letters of the english alphabet (i.e. p, q, r, s, etc.).

    |   Input Syntax     |   Logic Symbols  |   Name
    |----------------------|----------------------|--------------------
    |   ~                        |   ¬, ˜, !                 |   not
    |   &                        |   ∧, ·, &               |   and
    |   |                          |   ∨, +, ∥               |   or
    |   ^                        |   ⊕, ⊻, ≢              |   xor, not equivalence
    |   ->                       |   →, ⇒, ⊃              |   conditional
    |   <->                    |   ↔, ⇔, ≡              |   biconditional, equivalence""")

def main():
    return TruthTableGenerator() 
