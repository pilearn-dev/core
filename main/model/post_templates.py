# coding: utf-8

TEMPLATES = {
    "ban.rule-violation": u"""
Du hast mehrfach gegen unsere Nutzungsbedingungen verstoßen.

Wir haben versucht, diese so einfach wie m&ouml;glich zu formulieren. Wir haben dich auch schon mehrfach darauf hingewiesen, dass du, solltest du dir trotzdem unsicher sein, im [globalen Forum](/f/0) oder im [Helpdesk](/helpdesk) fragen kannst.
    """,
    "ban.sockpuppets": u"""
Wir haben starke Hinweise darauf, dass dieses Konto Teil einer Gruppe von Konten ist, die alle der selben Personengruppe geh&ouml;ren. Das ist nur dann erlaubt, solange diese Konten sich gegenseitig keine Vorteile geben oder gezielt gegen andere Benutzer eingesetzt werden.

**Diese Bedingungen wurden von dir nicht erf&uuml;llt.**
    """,
    "ban.spam": u"""
Auf &pi;-Learn d&uuml;rfen Produkte nur [unter bestimmten Bedingungen](/help/content-policy) beworben werden:

> - Erlaubt ist jede Werbung, die offiziell vom &pi;-Learn-Team autorisiert und eingef&uuml;gt wurde.
> - Erlaubt ist ist zur&uuml;ckhaltende Werbung in Form von Links in Beitr&auml;gen, die die folgenden Bedingungen erf&uuml;llt:
> 	- Die Werbung passt thematisch zum zugeh&ouml;rigen Beitrag und erg&auml;nzt diesen.
> 	- Der zugeh&ouml;rige Beitrag w&uuml;rde auch ohne die Werbung noch sinnvoll sein.
> 	- Du nennst explizit im Beitrag alle Beziehungen von dir zum Werbeprodukt, die ein Werbeinteresse f&ouml;rdern k&ouml;nnten.
> 	- Die Werbung ist als solche zu erkennen und nicht im Beitrag versteckt.

**Diese Bedingungen wurden von dir mehrfach nicht erf&uuml;llt.**
    """,
    "ban.offensive": u"""
Auf &pi;-Learn d&uuml;rfen keine [beleidigenden Inhalte](/help/legal/coc) ver&ouml;ffentlicht werden. Du hast dies aber mehrfach getan und wurdest deshalb auch bereits von uns verwarnt.
    """,
    "ban.conflicts": u"""
In letzter Zeit kam es h&auml;ufiger vor, dass du &uuml;berreagiert hast und dadurch Konflikte ausgel&ouml;st oder verschlimmert hast.
Wir haben dich bereits mehrfach kontaktiert, mit der Bitte, Konflikte in Zukunft zu vermeiden. Auch wenn jeder manchmal w&uuml;tend ist, war dein Verh&auml;ltnis grenzwertig und hat unseren [Code of Conduct](/help/legal/coc) verletzt.

Wir gehen davon aus, dass dies nicht absichtlich geschehen ist. Doch da du im Moment eine Last f&uuml;r die Community darstellst, m&uuml;ssen wir dich, auch zu deinem eigenen Schutz, sperren.

Wenn du der Meinung bist, dass andere Nutzer dich provozieren, versuche diesen aus dem Weg zu gehen. Sollte dies nicht m&ouml;glich sein, melde diese entweder &uuml;ber den *Melden*-Knopf auf den Profilseiten, oder, wenn du noch nicht genug Reputation hast, kontaktiere uns &uuml;ber das [Helpdesk](/helpdesk).
    """,
    "ban.calm-down": u"""
In letzter Zeit kam es vor, dass du etwas &uuml;berreagiert hast und dadurch Konflikte ausgel&ouml;st oder verschlimmert hast.
Das ist an sich nichts schlimmes, jeder ist manchmal w&uuml;tend. Aber dein Verhalten war teilweise grenzwertig und hat unseren [Code of Conduct](/help/legal/coc) verletzt.

Wir gehen davon aus, dass dies nicht absichtlich geschehen ist. Doch um dich daran zu erinnern, nett zu bleiben, schicken wir dir diese Nachricht und sperren dich, zu deinem Schutz und zum Schutz der Community, kurzzeitig sperren, damit die Konfliktsituation ersteinmal deeskalieren kann.

Wenn du der Meinung bist, dass andere Nutzer dich provozieren, versuche diesen aus dem Weg zu gehen. Sollte dies nicht m&ouml;glich sein, melde diese entweder &uuml;ber den *Melden*-Knopf auf den Profilseiten, oder, wenn du noch nicht genug Reputation hast, kontaktiere uns &uuml;ber das [Helpdesk](/helpdesk).
    """,
    "ban.no-improvement": u"""
Wir mussten dich bereits mehrfach ermahnen und sperren. Leider hast du daraus anscheinen nichts gelernt und/oder dein Verhalten nicht verbessert.

Da du offensichtlich nicht in der Lage bist, unsere [Nutzungsbedingungen](/help/legal/terms) und unseren [Code of Conduct](/help/legal/coc) einzuhalten, bist du auf unserer Seite **nicht l&auml;nger Willkommen!**

------

Wir haben dein Benutzerkonto jetzt längerfristig gesperrt.

*&uuml;berlege dir gut **ob** und **wie** du nach Ende der Sperrung wieder auf &pi;-Learn teilnehmen m&ouml;chtest.*

Wenn du nach dieser Sperrung IRGENDWIE negativ auffallen solltest, **werden wir dein Benutzerkonto l&ouml;schen und dich dauerhaft von der Nutzung dieser Webseite ausschlie&szlig;en.**
    """,
    "ban.no-contribution": u"""
Wenn man deine Beitr&auml;ge zu dieser Webseite betrachtet, f&auml;llt einem auf, dass du **keine Bereicherung f&uuml;r die Community** darstellst.

Deine Beitr&auml;ge sind gr&ouml;&szlig;tenteils schlecht formatiert, zu kurz und/oder enthalten keine n&uuml;tzlichen Informationen.

Da du damit eine Last f&uuml;r die Community darstellst haben wir dein Benutzerkonto f&uuml;r {Dauer} gesperrt.

Bitte trage danach nur dann Inhalte bei, wenn du meinst, dass diese der Qualit&auml;t der Seite nicht schaden, im Idealfall diese sogar verbessern. Kannst du dies nicht, solltest du lieber ganz verzichten Inhalte beizutragen.
    """
}

def getTemplate(t):
    return TEMPLATES[t].strip()

def parseTemplate(t, **kwargs):
    t = getTemplate(t)
    for key, value in kwargs.items():
        t = t.replace(u"{" + key + u"}", unicode(value))
    return t
