-- name: register_user!
INSERT OR IGNORE INTO users (vk_id, first_name) VALUES (:vk_id, :first_name);

-- name: get_user^
SELECT * FROM users WHERE vk_id = :vk_id;

-- name: add_score!
UPDATE users SET eco_points = eco_points + :points WHERE vk_id = :vk_id;

-- name: get_top_users
SELECT first_name, eco_points FROM users ORDER BY eco_points DESC LIMIT 10;

-- name: get_eco_points
SELECT * FROM eco_points WHERE category = :category;