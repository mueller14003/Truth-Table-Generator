"""
A cross-platform Truth Table Generator written in Python.
"""
import toga
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

#         ~   ¬     ^   ⊕     &    ∧     |    ∨
t_dict = {38: 8743, 94: 8853, 124: 8744, 126: 172} # Dict for str.translate()
prettify = lambda s: " ".join(s.translate(t_dict).replace('<->','↔').replace('->','→').replace(" ",""))

cond = Infix(lambda a,b: ~a | b) # Conditional
bicond = Infix(lambda a,b: ~(a ^ b)) # Biconditional
fix_inline = lambda s: s.replace('<->','|bicond|').replace('->','|cond|')

flatten = lambda l: sum(map(flatten,l),[]) if isinstance(l,list) else [l] # Flattens lists
get_arity = lambda f: len(signature(f).parameters) # Returns Arity of a Function
get_bits = lambda n: [*map(lambda x:[*map(int,bin(x)[2:].zfill(n))],range(2**n))] # Get Bits
gbfa = lambda f: get_bits(get_arity(f)) # Get Bits from Arity
output = lambda f: [*map(f,*zip(*gbfa(f)))] # Output of Boolean Function
make_tt = lambda f: [*map(flatten,[*map(list,zip(gbfa(f),output(f)))])] # Make Truth Table
gv = lambda s: sorted([*{*filter(str.isalpha,s)}]) # Gets Variables from String
gvf = lambda s: ','.join(gv(s)) # Get Vars (formatted)
mttfs = lambda s: make_tt(eval(f"lambda {gvf(s)}:[0,1][{fix_inline(s)}]")) # Make Truth Table from String

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
{chr(10).join([*map(lambda r: f"  <tr>{chr(10)}{chr(10).join([*map(lambda c: f'    <td>{c}</td>',r)])}{chr(10)}  </tr>",mttfs(s))])}
</table>

</body>
</html>
"""

md_line = lambda l: f"|{'|'.join(map(str,l))}|" # Markdown Line
md_header = lambda s: f"|{'|'.join(gv(s))}|{prettify(s)}|\n|{'|'.join('-'*len(gv(s)))}|:-:|\n" # Markdown Header
md_table = lambda s: md_header(s)+'\n'.join(map(md_line,mttfs(s))) # Markdown Truth Table
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
lt_table = lambda s: '\n'.join(map(lt_line,mttfs(s)))
make_tt_latex = lambda s: "\\documentclass[a4paper]{article}\n\\begin{document}" + \
    "\n\\title{Truth Table for $" + lt_prettify(s) + "$}\n\\author{Kyle Mueller}" + \
    "\n\\maketitle\n\\begin{displaymath}" + \
    "\n\\begin{array}{|" + ' '.join('c'*len(gv(s))) + "|c|}\n" + lt_header(s) + \
    "\n\\hline\n" + lt_table(s) + \
    "\n\\end{array}\n\\end{displaymath}\n\\end{document}"

org_line = lambda l: f"|{'|'.join(map(str,l))}|"
org_header = lambda s: f"|{'|'.join(gv(s)+[prettify(s)])}|\n|{'+'.join('-'*(len(gv(s))+1))}|\n"
org_table = lambda s: org_header(s) + '\n'.join(map(org_line,mttfs(s)))
make_tt_org = lambda s: f"* Truth Table for ~{prettify(s)}~\n{org_table(s)}"

class TruthTableGenerator(toga.App):   
    
    def startup(self):
        help_group = toga.Group.HELP

        input_syntax = toga.Command(
            self.ShowInputSyntax,
            label="Input Syntax",
            group=help_group
        )

        file_group = toga.Group.FILE

        export_html = toga.Command(
            self.ExportHTML,
            label="Export as HTML",
            group=file_group
        )

        export_markdown = toga.Command(
            self.ExportMarkdown,
            label="Export as Markdown",
            group=file_group
        )

        export_latex = toga.Command(
            self.ExportLaTeX,
            label="Export as LaTeX",
            group=file_group
        )

        export_org = toga.Command(
            self.ExportORG,
            label="Export as ORG",
            group=file_group
        )

        self.commands.add(export_html, export_markdown, export_latex, export_org, input_syntax)

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

        truth_table = toga.Table(
            headings=get_headings(default_expression), 
            data=mttfs(default_expression), 
            style=Pack(
                flex=1,
                padding=5))

        self.main_box.add(input_box)
        self.main_box.add(button)
        self.main_box.add(truth_table)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def make_tt(self, widget):
        boolean_expression = self.be_input.value or 'p -> q'

        truth_table = toga.Table(
            headings=get_headings(boolean_expression), 
            data=mttfs(boolean_expression), 
            style=Pack(
                flex=1, 
                padding=5))
        
        self.main_box.remove(self.main_box.children[-1])
        self.main_box.add(truth_table)

    def ExportHTML(self, widget):
        boolean_expression = self.be_input.value or 'p -> q'

        filename = self.main_window.save_file_dialog(
            title="Export as HTML", 
            suggested_filename="truth_table",
            file_types=["html", "txt"])
        
        with open(filename, "w", encoding='utf-8') as f:
            f.writelines(make_tt_html(boolean_expression))

    def ExportMarkdown(self, widget):
        boolean_expression = self.be_input.value or 'p -> q'
        
        filename = self.main_window.save_file_dialog(
            title="Export as Markdown", 
            suggested_filename="truth_table",
            file_types=["md", "txt"])

        with open(filename, "w", encoding='utf-8') as f:
            f.writelines(make_tt_markdown(boolean_expression))

    def ExportLaTeX(self, widget):
        boolean_expression = self.be_input.value or 'p -> q'
        
        filename = self.main_window.save_file_dialog(
            title="Export as LaTeX", 
            suggested_filename="truth_table",
            file_types=["tex", "txt"])

        with open(filename, "w", encoding='utf-8') as f:
            f.writelines(make_tt_latex(boolean_expression))

    def ExportORG(self, widget):
        boolean_expression = self.be_input.value or 'p -> q'
        
        filename = self.main_window.save_file_dialog(
            title="Export as ORG", 
            suggested_filename="truth_table",
            file_types=["org", "txt"])

        with open(filename, "w", encoding='utf-8') as f:
            f.writelines(make_tt_org(boolean_expression))

    def ShowInputSyntax(self, widget):
        return self.main_window.info_dialog(
            title="Input Syntax",
            message="""Please use the symbols from "Input Syntax" below when entering a boolean expression into the input box.

Write boolean expressions in infix notation, as if you were writing Python code (e.g. "p & q | r").

Please limit all boolean variables to single characters of the english language (i.e. p, q, r, s, etc.).

    |   Input Syntax     |   Logic Symbol    |   Name
    |----------------------|----------------------|--------------------
    |   ~                        |   ¬                       |   not
    |   &                        |   ∧                       |   and
    |   |                          |   ∨                       |   or
    |   ^                        |   ⊕                       |   xor
    |   ->                       |   →                       |   conditional
    |   <->                    |   ↔                       |   biconditional"""
        )

def main():
    return TruthTableGenerator() 
