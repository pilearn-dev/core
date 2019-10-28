CREATE TABLE settings (
  setting_group VARCHAR(30),
  setting_key VARCHAR(30) PRIMARY KEY,
  setting_value TEXT,
  setting_description VARCHAR(250)
)
INSERT INTO settings VALUES
('Identität', 'site-name', 'π-Learn', 'Der Name der Seite in reiner Textform'),
('Identität', 'site-short-name', 'π-Learn', 'Der Name der Seite in reiner Textform (Kurzform)'),
('Identität', 'site-label', 'π-Learn', 'Der Name der Seite, wie er in der Navigationsleiste ausgegeben wird (<x> enthält Attribute, wie z.B. beta)'),
('Identität', 'site-language', 'de', 'Die Sprache der Seite (de/en)'),

('Logging', 'logging-errors-sentry-key', 'https://36ab18e688374a98aed8a511c414a9e3@sentry.io/1461987', 'Der geheime Schlüssel für das Sentry.io Fehleranalyse-Tool'),
('Logging', 'logging-matomo-id', '1', 'Die Nummer der Seite im Matomo-Analytics-Tool'),

('Zugang', 'access-private', 'false', 'Ob diese Seite zugriffsbeschränkt ist'),
('Zugang', 'access-private-token', '5ae2caf-4f22c4a-c29896-7e50dc', 'Das Geheimnis, das als Masterpasswort für die Zugriffsbeschränkung verwendet wird'),
('Zugang', 'access-private-notice', 'Nur das &pi;-Learn-Team darf auf diese Entwicklerseite zugreifen.', 'Die Nachricht, die für Unbefugte angezeigt wird'),
('Zugang', 'access-allow-password', '1', 'Ob die Zugriffsbeschränkung mit einem Passwort umgangen werden kann'),
('Zugang', 'access-allow-password-value', 'covfefe', 'Das Passwort, mit dem die Beschränkung umgangen werden könnte'),


('Features', 'enable-mathjax', '1', 'Ob MathJax (mathematische Notation) geladen werden soll'),
('Features', 'enable-mathjax-tokens-block', '::( )::', 'Die MathJax-Begrenzungen (Blöcke)'),
('Features', 'enable-mathjax-tokens-inline', ':( ):', 'Die MathJax-Begrenzungen (Inline)'),
('Features', 'enable-teaching-teams', 'no', 'Ob Teach (Team-Nutzung) erlaubt sein soll.')




CREATE TABLE teach_groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  token VARCHAR(7),
  name VARCHAR(75),
  org_name VARCHAR(150),
  org_rep_name VARCHAR(150),
  org_email VARCHAR(150),
  active TINYINT,
  is_demo TINYINT
)
