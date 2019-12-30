# coding: utf-8
import smtplib, re, time, json
from flask import render_template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

f = open("pidata.json", "r")
pidata = json.loads(f.read())
f.close()

def render_email_html(text_old, contents):
    text = []
    in_table = False
    table = []
    for line in text_old.split("\n"):
        line = line.strip()
        line = re.sub("~~(.+?)~~", "<strong>\\1</strong>", line)
        line = re.sub("~(.+?)~", "<em>\\1</em>", line)
        line = re.sub("\\{\\#(.+?)[ ]*\\-\\>[ ]*(.+?)\\#\\}", "<a style=\"text-decoration: none\" href=\"\\2\"><table cellspacing=\"0\" cellpadding=\"0\" border=\"0\"><tr><td align=\"center\"><table cellspacing=\"0\" cellpadding=\"10px\" style=\"border: 1px solid #447fd8; border-radius: 0.15em;\"><tr bgcolor=\"#136cf5\" style=\"box-shadow: 0 4px 0 -2px rgba(255,255,255,.25) inset\"><td style=\"width: 1px\"></td><td align=\"center\"><font color=\"#fff\">\\1</font></td><td style=\"width: 1px\"></td></tr></table></td></tr></table></a>", line)
        line = re.sub("\\{(.+?)[ ]*\\-\\>[ ]*(.+?)\\}", "<a href='\\2'>\\1</a>", line)
        if in_table:
            if line == "\\endtable":
                in_table = False
                table = "<table width=\"100%\" border=\"1\" cellspacing=\"0\" cellpadding=\"5px\"><tr><td>" + "</tr><tr><td>".join(["</td><td>".join(i) for i in table]) + "</td></tr></table>"
                text.append(table)
                table = []
            else:
                table.append(line.split("&&"))
        elif line == "\\table":
            in_table = True
        elif line == "":
            text.append("</td></tr><tr><td>")
        else:
            if line.startswith("### "):
                line = "<font size=\"4\">" + line[4:] + "</font>"
            elif line.startswith("## "):
                line = "<font size=\"5\">" + line[3:] + "</font>"
            elif line.startswith("# "):
                line = "<font size=\"6\">" + line[2:] + "</font>"
            elif re.match(r"\[\[[a-z_]+\]\]", line):
                pattern = line[2:-2]
                c = contents[pattern]

                if len(c) == 0:
                    continue

                def _p(x):
                    return '<table width="100%"><tr><td cellpadding="10px">' + "\n".join(x) + "\n<table width=\"100%\"><tr><td height=\"0.5px\" bgcolor=\"#ddd\"></td></tr></table></td></tr></table>"

                def _i(x):
                    return "<table width=\"100%\"><tr><td height=\"0.5px\" bgcolor=\"#ddd\"></td></tr><tr><td cellpadding=\"20px\"><table><tr><td><font size=\"4\"><a href=\""+x["link"]+"\">" + x["title"] + "</a></font></td></tr><tr><td><font size=\"1\" color=\"#aaaaaa\">" + x["date"] + "</font>&nbsp;&nbsp;" + _t(x["tags"]) + "</td></tr><tr><td>" + x["excerpt"] + "</td></tr></table></td></tr></table>"

                def _t(x):
                    k = ""
                    for i in x:
                        if i.startswith(":"):
                            k += "<td bgcolor=\"#f9ecee\"><font size=\"1.5\" color=\"#c91d2e\">"+i[1:]+"</font></td>"
                        else:
                            k += "<td bgcolor=\"#E1ECF4\"><font size=\"1.5\" color=\"#39239d\">"+i+"</font></td>"
                    return "<table style=\"display: inline;\" cellpadding=\"5px\"><tr cellspacing=\"7.5px\">"+k+"</tr></table>"

                line = _p(list(map(_i, c)))
            text.append(line)

    text = "\n\n".join(text)
    return text




def send_textbased_email(to, subject, text, contents=None):
    senderaddr = 'nicht-antworten' + pidata["mail_configuration"]["addr_base"]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = senderaddr
    msg['To'] = to

    part1 = MIMEText(text, 'plain', 'utf-8')


    html = render_email_html(text, contents)
    html = render_template("mail.html", body=html)
    part2 = MIMEText(html, 'html', 'utf-8')

    msg.attach(part1)
    msg.attach(part2)


    if pidata["mail_service"] == "smtp":

        server = smtplib.SMTP(pidata["mail_configuration"]["smtp_srv"], pidata["mail_configuration"]["smtp_port"])
        server.ehlo()
        server.starttls()
        server.ehlo()
        print((pidata["mail_configuration"]["password"]))
        server.login(pidata["mail_configuration"]["user"],bytearray(pidata["mail_configuration"]["password"], 'utf-8'))
        server.sendmail(senderaddr, to, msg.as_string())
        server.quit()

    elif pidata["mail_service"] == "fileoutput":

        f = open("mailoutput/" + str(int(time.time())) + ".eml", "w")
        f.write(msg.as_string())
        f.close()
