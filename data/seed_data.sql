-- Catégories
INSERT OR IGNORE INTO category (name, max_items) VALUES ('top', 1);
INSERT OR IGNORE INTO category (name, max_items) VALUES ('bottom', 1);
INSERT OR IGNORE INTO category (name, max_items) VALUES ('shoes', 1);
INSERT OR IGNORE INTO category (name, max_items) VALUES ('accessory', 4);
INSERT OR IGNORE INTO category (name, max_items) VALUES ('hair', 1);
INSERT OR IGNORE INTO category (name, max_items) VALUES ('face', 1);

-- Thèmes
INSERT OR IGNORE INTO theme (code, label) VALUES ('casual','Casual');
INSERT OR IGNORE INTO theme (code, label) VALUES ('soiree','Soirée');
INSERT OR IGNORE INTO theme (code, label) VALUES ('colorful','Colorful');
INSERT OR IGNORE INTO theme (code, label) VALUES ('chic','Chic');

-- Mannequins
INSERT OR IGNORE INTO mannequin (id, name, base_sprite_path) VALUES (1, 'Marinette', 'assets/mannequins/mannequin_base.png');

-- Vêtements (référencent les catégories par sous-requête)
INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('Top rose punk', (SELECT id FROM category WHERE name='top'), 'assets/clothes/tops/top1.png', 'colorful', 20);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('Top rose chic', (SELECT id FROM category WHERE name='top'), 'assets/clothes/tops/top2.png', 'soiree', 20);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('Top medieval', (SELECT id FROM category WHERE name='top'), 'assets/clothes/tops/top3.png', 'Chic', 20);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('top violet', (SELECT id FROM category WHERE name='top'), 'assets/clothes/tops/top4.png', 'casual', 20);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('top vert classe', (SELECT id FROM category WHERE name='top'), 'assets/clothes/tops/top5.png', 'chic', 20);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('jeans déchirée', (SELECT id FROM category WHERE name='bottom'), 'assets/clothes/bottoms/bottom1.png', 'casual', 15);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('jupe classic', (SELECT id FROM category WHERE name='bottom'), 'assets/clothes/bottoms/bottom2.png', 'chic', 15);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('pantalon maléfique', (SELECT id FROM category WHERE name='bottom'), 'assets/clothes/bottoms/bottom3.png', 'soiree', 15);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('jupe medieval', (SELECT id FROM category WHERE name='bottom'), 'assets/clothes/bottoms/bottom4.png', 'soiree', 15);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('pantalon vert', (SELECT id FROM category WHERE name='bottom'), 'assets/clothes/bottoms/bottom5.png', 'casual', 15);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('jupe classic', (SELECT id FROM category WHERE name='bottom'), 'assets/clothes/bottoms/bottom2.png', 'chic', 15);