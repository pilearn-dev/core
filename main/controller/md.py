# coding: utf-8
from flaskext.markdown import Extension, Markdown
from markdown.preprocessors import Preprocessor
from markdown.postprocessors import Postprocessor
import re

from model import tags as mtags

class MDExtPreProcessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            m = re.findall(ur"\[\#([a-zA-Z:0-9äöüß-]{2,20})\]", line)
            for i in m:
                if i in mtags.moderator_only:
                    line = line.replace("[#"+i+"]", "<span class='tag moderator-tag'>"+i+"</span>")
                else:
                    line = line.replace("[#"+i+"]", "<span class='tag'>"+i+"</span>")
            m = re.findall(ur"\[\[([a-zA-ZÄÖÜäöü -]+?)\|([a-z]+?)\]\]", line)
            for i in m:
                line = line.replace("[["+("|".join(i))+"]]", "<a href='/t/"+i[1]+"' class='topic'>"+i[0]+"</a>")
            m = re.findall(r"\{\! application \"(.+?)\" ([a-zA-Z0-9]+?) \"(.+?)\" \!\}", line)
            for i in m:
                label, id_, url = i
                types = {
                    "election": u"π-learn wahl",
                    "::404::": u"unbekannte app"
                }
                if id_ not in types.keys():
                    id_ = "::404::"
                line = line.replace("{! application \""+label+"\" "+id_+" \""+url+"\" !}", '<a href="'+url+'" data-type="'+types[id_]+'" class="app-btn">'+label+'</a>')
            new_lines.append(line)
        return new_lines

class MDExtPostProcessor(Postprocessor):
    def run(self, lines):
        markable_count = 0
        lines = lines.split("\n")
        new_lines = []
        in_table = 0
        for line in lines:
            if in_table!=0 and line.strip() == "":
                continue
            if in_table == 1:
                if line.startswith("<p>"):
                    line = line[3:]
                line = "<tr><th>" + ("</th><th>".join([i.strip() for i in line.split("|")])) + "</th></tr>"
                in_table+=1
            elif in_table == 2:
                in_table = 3
                if not re.match("^(\-+\|)+\--+$", line):
                    line = "<tr><td>" + ("</td><td>".join([i.strip() for i in line.split("|")])) + "</td></tr>"
                else:
                    continue
            elif in_table == 3 and line not in ["<!-- %endtable% -->", "<!-- %endtable% --></p>"]:
                line = "<tr><td>" + ("</td><td>".join([i.strip() for i in line.split("|")])) + "</td></tr>"
            elif in_table == 0 and line in ["<!-- %table% -->", "<p><!-- %table% -->"]:
                in_table = 1
                line = "<table>"
            elif in_table != 0 and line in ["<!-- %endtable% -->", "<!-- %endtable% --></p>"]:
                in_table = 0
                line = "</table>"
            m = re.match(r"^\<\!\-\-\ %markable:([a-zA-Z0-0_-]+?)\% \-\-\>$", line)
            if m:
                line = "<div class='is-markable' id='"+m.group(1)+"'>"
                markable_count += 1
            m = re.match(r"^\<\!\-\- \%endmarkable\% \-\-\>$", line)
            if m:
                if markable_count > 0:
                    line = "</div>"
                    markable_count -= 1
            new_lines.append(line)
        new_lines[-1]+= "</div>"*markable_count
        new_lines = "\n".join(new_lines)
        return new_lines

def md_apply(app):
    md = Markdown(app, extensions=["iconfonts(prefix=fa-, base=fa)", "markdownnofollow"])
    moderator_tags = mtags.moderator_only
    banned_tags = mtags.banned

    @md.extend()
    class ExtensionPreRegisterer(Extension):
        def extendMarkdown(self, md, md_globals):
            md.preprocessors.add('pipreproc',
                                MDExtPreProcessor(md),
                                '_begin')
            md.registerExtension(self)

    md.register_extension(ExtensionPreRegisterer)

    @md.extend()
    class ExtensionPostRegisterer(Extension):
        def extendMarkdown(self, md, md_globals):
            md.postprocessors.add('pipostproc',
                                MDExtPostProcessor(md),
                                '_end')
            md.registerExtension(self)

    md.register_extension(ExtensionPostRegisterer)
