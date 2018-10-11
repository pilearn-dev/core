CREATE TABLE help_entry (
  id INTEGER PRIMARY KEY,
  master_page INT,
  active TINYINT,
  template VARCHAR(25),
  help_cat INT,
  url_part VARCHAR(30),
  url VARCHAR(100),
  title VARCHAR(300),
  original_content TEXT,
  override_content TEXT,
  editable_by_admin TINYINT,
  subpage_by_admin TINYINT,
  is_deprecated TINYINT,
  is_pinned TINYINT,
  last_change INT,
  last_editor INT
)
INSERT INTO help_entry (master_page, active, template, help_cat, url_part, url, title, original_content, override_content, editable_by_admin, subpage_by_admin, is_deprecated, is_pinned, last_change, last_editor) VALUES (0, 1, 'default', 1, 'coc', 'legal/coc', 'Code of Conduct', ?, '', 0, 0, 0, 1, 0, 0)
CREATE TABLE help_category (
  id INTEGER PRIMARY KEY,
  active TINYINT,
  cat_symbol VARCHAR(30),
  url_part VARCHAR(30),
  title VARCHAR(100),
  original_excerpt VARCHAR(300),
  override_excerpt VARCHAR(300),
  editable_by_admin TINYINT,
  newpage_by_admin TINYINT
)
INSERT INTO help_category (active, cat_symbol, url_part, title, original_excerpt, override_excerpt, editable_by_admin, newpage_by_admin) VALUES (1, 'fa-book', 'legal', 'Rechtliches', 'Nutzungsbedingungen, Code of Conduct und weitere verbindliche Dokumente', '', 0, 0)
