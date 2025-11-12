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

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('calm', (SELECT id FROM category WHERE name='face'), 'assets/clothes/faces/face1.png', 'casual', 10);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('energetic', (SELECT id FROM category WHERE name='face'), 'assets/clothes/faces/face2.png', 'colorful', 10);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('serene', (SELECT id FROM category WHERE name='face'), 'assets/clothes/faces/face3.png', 'chic', 10);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('interested', (SELECT id FROM category WHERE name='face'), 'assets/clothes/faces/face4.png', 'soiree', 10);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('happy', (SELECT id FROM category WHERE name='face'), 'assets/clothes/faces/face5.png', 'colorful', 10);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('bob', (SELECT id FROM category WHERE name='hair'), 'assets/clothes/hairs/hair1.png', 'chic', 25);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('blue', (SELECT id FROM category WHERE name='hair'), 'assets/clothes/hairs/hair2.png', 'soiree', 25);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('blond', (SELECT id FROM category WHERE name='hair'), 'assets/clothes/hairs/hair3.png', 'casual', 25);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('long', (SELECT id FROM category WHERE name='hair'), 'assets/clothes/hairs/hair4.png', 'chic', 25);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('violet', (SELECT id FROM category WHERE name='hair'), 'assets/clothes/hairs/hair5.png', 'colorful', 25);